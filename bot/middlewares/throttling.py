from typing import Callable, Dict, Any, Awaitable
import time
from aiogram import BaseMiddleware
from aiogram.types import Message

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 30, window: int = 60):
        self.limit = limit
        self.window = window
        self.users = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        now = time.time()
        
        if user_id not in self.users:
            self.users[user_id] = []
            
        # Clean up old messages
        self.users[user_id] = [t for t in self.users[user_id] if now - t < self.window]
        
        if len(self.users[user_id]) >= self.limit:
            await event.answer("⚠️ Iltimos, biroz kutib turing.")
            return
            
        self.users[user_id].append(now)
        return await handler(event, data)
