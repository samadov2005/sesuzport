from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from asgiref.sync import sync_to_async

class UserRegistrationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        
        user = None
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user

        if user and not user.is_bot:
            from apps.users.models import TelegramUser
            from django.utils import timezone
            
            @sync_to_async
            def get_or_create_user():
                telegram_user, created = TelegramUser.objects.get_or_create(
                    telegram_id=user.id,
                    defaults={
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'last_activity': timezone.now()
                    }
                )
                if not created:
                    telegram_user.last_activity = timezone.now()
                    update_fields = ['last_activity']
                    if user.username != telegram_user.username:
                        telegram_user.username = user.username
                        update_fields.append('username')
                    if user.first_name != telegram_user.first_name:
                        telegram_user.first_name = user.first_name
                        update_fields.append('first_name')
                    if user.last_name != telegram_user.last_name:
                        telegram_user.last_name = user.last_name
                        update_fields.append('last_name')
                    telegram_user.save(update_fields=update_fields)
                return telegram_user

            db_user = await get_or_create_user()
            data['telegram_user'] = db_user
            
        return await handler(event, data)
