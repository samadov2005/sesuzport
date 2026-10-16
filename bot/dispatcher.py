from __future__ import annotations
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import get_bot_config
from bot.middlewares.user_registration import UserRegistrationMiddleware
from bot.middlewares.logging_middleware import LoggingMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.services.notification_service import set_bot_instance

from bot.routers import (
    start,
    registration,
    admin,
    consumer,
    entrepreneur,
    complaints,
    stores,
    cashback,
    rights,
    support,
    settings,
    common,
)

logger = logging.getLogger(__name__)

_bot_instance: Bot | None = None
_dispatcher_instance: Dispatcher | None = None


def get_bot() -> Bot:
    """Return a singleton Bot instance configured from environment."""
    global _bot_instance
    if _bot_instance is None:
        config = get_bot_config()
        _bot_instance = Bot(
            token=config.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        set_bot_instance(_bot_instance)
    return _bot_instance


def get_dispatcher() -> Dispatcher:
    """Return a singleton Dispatcher instance with all middlewares and routers configured."""
    global _dispatcher_instance
    if _dispatcher_instance is None:
        config = get_bot_config()
        
        # Setup storage
        if config.redis_url and os.getenv('USE_REDIS', 'false').lower() == 'true':
            from redis.asyncio import Redis
            from aiogram.fsm.storage.redis import RedisStorage
            redis = Redis.from_url(config.redis_url)
            storage = RedisStorage(redis=redis)
            logger.info('Using Redis FSM storage')
        else:
            storage = MemoryStorage()
            logger.info('Using Memory FSM storage')
            
        dp = Dispatcher(storage=storage)
        
        # Register middlewares
        dp.update.outer_middleware(LoggingMiddleware())
        dp.update.outer_middleware(UserRegistrationMiddleware())
        dp.message.middleware(ThrottlingMiddleware())
        
        # Include routers (order matters!)
        dp.include_router(start.router)
        dp.include_router(registration.router)
        dp.include_router(admin.router)
        dp.include_router(consumer.router)
        dp.include_router(entrepreneur.router)
        dp.include_router(complaints.router)
        dp.include_router(stores.router)
        dp.include_router(cashback.router)
        dp.include_router(rights.router)
        dp.include_router(support.router)
        dp.include_router(settings.router)
        dp.include_router(common.router)  # Must be last (catches unhandled)
        
        _dispatcher_instance = dp
    return _dispatcher_instance
