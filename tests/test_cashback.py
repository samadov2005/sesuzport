"""
Tests for CashbackAccount and CashbackTransaction models.
"""
from decimal import Decimal
from django.test import TestCase
from apps.users.models import TelegramUser, UserRole
from apps.cashback.models import CashbackAccount, CashbackTransaction, TransactionType


class CashbackAccountTest(TestCase):
    """Test CashbackAccount model."""

    def setUp(self) -> None:
        self.user = TelegramUser.objects.create(
            telegram_id=111222333,
            username='cashback_user',
            first_name='Cashback',
            last_name='Test',
            role=UserRole.CONSUMER,
        )

    def test_create_cashback_account(self) -> None:
        """Test creating a cashback account."""
        account = CashbackAccount.objects.create(user=self.user)
        self.assertIsNotNone(account.pk)
        self.assertEqual(account.balance, Decimal('0'))
        self.assertEqual(account.total_earned, Decimal('0'))
        self.assertEqual(account.total_spent, Decimal('0'))

    def test_cashback_account_one_to_one(self) -> None:
        """Test that each user has only one cashback account."""
        from django.db import IntegrityError
        CashbackAccount.objects.create(user=self.user)
        with self.assertRaises(Exception):
            CashbackAccount.objects.create(user=self.user)

    def test_cashback_account_str(self) -> None:
        """Test __str__ representation."""
        account = CashbackAccount.objects.create(user=self.user)
        self.assertIn("so'm", str(account))

    def test_get_or_create_account(self) -> None:
        """Test get_or_create pattern for cashback accounts."""
        account1, created1 = CashbackAccount.objects.get_or_create(user=self.user)
        self.assertTrue(created1)

        account2, created2 = CashbackAccount.objects.get_or_create(user=self.user)
        self.assertFalse(created2)
        self.assertEqual(account1.pk, account2.pk)

    def test_balance_calculation(self) -> None:
        """Test balance calculation after transactions."""
        account = CashbackAccount.objects.create(user=self.user)

        # Add earn transaction
        CashbackTransaction.objects.create(
            account=account,
            amount=Decimal('50000'),
            transaction_type=TransactionType.EARN,
            description='Murojaat uchun keshbek',
        )
        account.balance += Decimal('50000')
        account.total_earned += Decimal('50000')
        account.save()

        # Add spend transaction
        CashbackTransaction.objects.create(
            account=account,
            amount=Decimal('10000'),
            transaction_type=TransactionType.SPEND,
            description='Keshbekdan foydalanish',
        )
        account.balance -= Decimal('10000')
        account.total_spent += Decimal('10000')
        account.save()

        refreshed = CashbackAccount.objects.get(pk=account.pk)
        self.assertEqual(refreshed.balance, Decimal('40000'))
        self.assertEqual(refreshed.total_earned, Decimal('50000'))
        self.assertEqual(refreshed.total_spent, Decimal('10000'))

    def test_cashback_transaction_types(self) -> None:
        """Test all transaction types."""
        account = CashbackAccount.objects.create(user=self.user)

        earn_tx = CashbackTransaction.objects.create(
            account=account,
            amount=Decimal('25000'),
            transaction_type=TransactionType.EARN,
            description='Earn transaction',
        )
        spend_tx = CashbackTransaction.objects.create(
            account=account,
            amount=Decimal('5000'),
            transaction_type=TransactionType.SPEND,
            description='Spend transaction',
        )
        adjust_tx = CashbackTransaction.objects.create(
            account=account,
            amount=Decimal('1000'),
            transaction_type=TransactionType.ADJUSTMENT,
            description='Adjustment transaction',
        )

        self.assertEqual(earn_tx.transaction_type, TransactionType.EARN)
        self.assertEqual(spend_tx.transaction_type, TransactionType.SPEND)
        self.assertEqual(adjust_tx.transaction_type, TransactionType.ADJUSTMENT)

    def test_transaction_ordering(self) -> None:
        """Test transactions are ordered by created_at descending."""
        account = CashbackAccount.objects.create(user=self.user)

        tx1 = CashbackTransaction.objects.create(
            account=account,
            amount=Decimal('10000'),
            transaction_type=TransactionType.EARN,
            description='First',
        )
        tx2 = CashbackTransaction.objects.create(
            account=account,
            amount=Decimal('20000'),
            transaction_type=TransactionType.EARN,
            description='Second',
        )

        transactions = CashbackTransaction.objects.filter(account=account)
        # tx2 is newer, should come first
        self.assertEqual(transactions.first().pk, tx2.pk)

    def test_monthly_earned_calculation(self) -> None:
        """Test that monthly earned can be calculated."""
        from django.utils import timezone
        import datetime

        account = CashbackAccount.objects.create(user=self.user)
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        CashbackTransaction.objects.create(
            account=account,
            amount=Decimal('15000'),
            transaction_type=TransactionType.EARN,
            description='This month earn',
        )

        monthly_earned = CashbackTransaction.objects.filter(
            account=account,
            transaction_type=TransactionType.EARN,
            created_at__gte=month_start,
        ).values_list('amount', flat=True)

        total_monthly = sum(monthly_earned)
        self.assertEqual(total_monthly, Decimal('15000'))

    def test_transaction_str(self) -> None:
        """Test transaction __str__ representation."""
        account = CashbackAccount.objects.create(user=self.user)
        tx = CashbackTransaction.objects.create(
            account=account,
            amount=Decimal('5000'),
            transaction_type=TransactionType.EARN,
            description='Test transaction',
        )
        self.assertIn('EARN', str(tx))

    def test_account_cascade_delete(self) -> None:
        """Test that transactions are deleted when account is deleted."""
        account = CashbackAccount.objects.create(user=self.user)
        CashbackTransaction.objects.create(
            account=account,
            amount=Decimal('5000'),
            transaction_type=TransactionType.EARN,
            description='To be deleted',
        )

        account_pk = account.pk
        account.delete()

        remaining = CashbackTransaction.objects.filter(account_id=account_pk)
        self.assertEqual(remaining.count(), 0)
