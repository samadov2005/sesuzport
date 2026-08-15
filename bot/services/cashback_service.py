from decimal import Decimal

from asgiref.sync import sync_to_async
from apps.cashback.models import CashbackAccount, CashbackTransaction, TransactionType
from apps.users.models import TelegramUser
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@sync_to_async
def get_or_create_cashback_account(telegram_id: int) -> CashbackAccount:
    """Get or create a cashback account for the user."""
    user = TelegramUser.objects.get(telegram_id=telegram_id)
    account, _ = CashbackAccount.objects.get_or_create(
        user=user,
        defaults={
            'balance': Decimal('0.00'),
            'total_earned': Decimal('0.00'),
            'total_spent': Decimal('0.00'),
        },
    )
    return account


@sync_to_async
def get_cashback_balance(telegram_id: int) -> dict:
    """Return balance info dict with real monthly calculation."""
    user = TelegramUser.objects.get(telegram_id=telegram_id)
    account, _ = CashbackAccount.objects.get_or_create(
        user=user,
        defaults={
            'balance': Decimal('0.00'),
            'total_earned': Decimal('0.00'),
            'total_spent': Decimal('0.00'),
        },
    )

    # Real monthly earned calculation
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_txs = CashbackTransaction.objects.filter(
        account=account,
        transaction_type=TransactionType.EARN,
        created_at__gte=month_start,
    ).values_list('amount', flat=True)
    monthly_earned = sum(monthly_txs, Decimal('0.00'))

    # Recent transactions (last 5)
    recent = list(
        CashbackTransaction.objects.filter(account=account)
        .order_by('-created_at')[:5]
    )

    return {
        'balance': account.balance,
        'monthly_earned': monthly_earned,
        'total_earned': account.total_earned,
        'total_spent': account.total_spent,
        'recent_transactions': recent,
    }


@sync_to_async
def add_cashback(
    telegram_id: int,
    amount: Decimal,
    description: str,
    transaction_type: str = TransactionType.EARN,
) -> CashbackTransaction:
    """Add a cashback transaction and update account balance."""
    from django.db import transaction as db_transaction

    with db_transaction.atomic():
        user = TelegramUser.objects.get(telegram_id=telegram_id)
        account, _ = CashbackAccount.objects.get_or_create(user=user)

        tx = CashbackTransaction.objects.create(
            account=account,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
        )

        if transaction_type == TransactionType.EARN:
            account.balance += amount
            account.total_earned += amount
        elif transaction_type == TransactionType.SPEND:
            account.balance -= amount
            account.total_spent += amount
        elif transaction_type == TransactionType.ADJUSTMENT:
            account.balance += amount  # can be negative for deductions

        account.save()
        return tx


@sync_to_async
def get_cashback_transactions(telegram_id: int, page: int = 1, page_size: int = 10) -> tuple:
    """Return paginated cashback transactions."""
    from django.core.paginator import Paginator

    user = TelegramUser.objects.get(telegram_id=telegram_id)
    try:
        account = CashbackAccount.objects.get(user=user)
    except CashbackAccount.DoesNotExist:
        return [], 0

    qs = CashbackTransaction.objects.filter(account=account).order_by('-created_at')
    paginator = Paginator(qs, page_size)
    try:
        txs = list(paginator.page(page).object_list)
    except Exception:
        txs = []
    return txs, paginator.num_pages
