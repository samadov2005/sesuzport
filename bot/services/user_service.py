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
def is_entrepreneur_user(telegram_id: int) -> bool:
    """Check if the user is authorized as ENTREPRENEUR, ADMIN or MODERATOR."""
    from apps.users.models import UserRole
    # User is entrepreneur if their database role is ENTREPRENEUR, ADMIN or MODERATOR
    # (or if they own any registered stores)
    user = TelegramUser.objects.filter(telegram_id=telegram_id, is_active=True).first()
    if not user:
        return False
    if user.role in [UserRole.ENTREPRENEUR, UserRole.ADMIN, UserRole.MODERATOR]:
        return True
    return False

@sync_to_async
def update_user_role(telegram_id: int, role: str) -> TelegramUser:
    """
    Update user session or role safely.
    Admins, Moderators, and authorized Entrepreneurs retain their authorization.
    """
    from apps.users.models import UserRole
    try:
        user = TelegramUser.objects.get(telegram_id=telegram_id)
    except TelegramUser.DoesNotExist:
        return None

    # Never downgrade Admin, Moderator, or authorized Entrepreneur to CONSUMER when switching modes
    if user.role in [UserRole.ADMIN, UserRole.MODERATOR, UserRole.ENTREPRENEUR]:
        # Keep DB role safe so their permissions are not lost
        return user

    if role == UserRole.ENTREPRENEUR and user.role != UserRole.ENTREPRENEUR:
        return user

    user.role = role
    user.save(update_fields=['role'])
    return user

@sync_to_async
def get_user_by_telegram_id(telegram_id: int) -> TelegramUser | None:
    try:
        return TelegramUser.objects.get(telegram_id=telegram_id)
    except TelegramUser.DoesNotExist:
        return None

@sync_to_async
def get_user_language(telegram_id: int) -> str:
    """Get the user's selected language ('uz' or 'ru'). Defaults to 'uz'."""
    try:
        user = TelegramUser.objects.only('language').get(telegram_id=telegram_id)
        return user.language or 'uz'
    except TelegramUser.DoesNotExist:
        return 'uz'

@sync_to_async
def update_user_language(telegram_id: int, language: str) -> None:
    """Update the user's language in the database."""
    lang = language if language in ('uz', 'ru') else 'uz'
    TelegramUser.objects.filter(telegram_id=telegram_id).update(language=lang)

@sync_to_async
def update_last_activity(telegram_id: int) -> None:
    TelegramUser.objects.filter(telegram_id=telegram_id).update(last_activity=timezone.now())
