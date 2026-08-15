from asgiref.sync import sync_to_async
from apps.users.models import TelegramUser
from django.utils import timezone

@sync_to_async
def get_or_create_user(telegram_id: int, username: str | None, first_name: str, last_name: str | None) -> tuple[TelegramUser, bool]:
    return TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'last_activity': timezone.now()
        }
    )

@sync_to_async
def update_user_role(telegram_id: int, role: str) -> TelegramUser:
    user = TelegramUser.objects.get(telegram_id=telegram_id)
    user.role = role
    user.save()
    return user

@sync_to_async
def get_user_by_telegram_id(telegram_id: int) -> TelegramUser | None:
    try:
        return TelegramUser.objects.get(telegram_id=telegram_id)
    except TelegramUser.DoesNotExist:
        return None

@sync_to_async
def update_last_activity(telegram_id: int) -> None:
    TelegramUser.objects.filter(telegram_id=telegram_id).update(last_activity=timezone.now())
