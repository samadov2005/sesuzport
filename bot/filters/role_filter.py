from aiogram.filters import BaseFilter
from aiogram.types import Message
from typing import Any

class RoleFilter(BaseFilter):
    def __init__(self, role: str):
        self.role = role
    
    async def __call__(self, message: Message, **data: Any) -> bool:
        telegram_user = data.get('telegram_user')
        if telegram_user is None:
            return False
        return telegram_user.role == self.role
