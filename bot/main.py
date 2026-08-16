from pathlib import Path
import asyncio
import logging
import os
import sys

# Ensure project root is at the beginning of sys.path before any imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
bot_dir = str(Path(__file__).resolve().parent)
if bot_dir in sys.path:
    sys.path.remove(bot_dir)

# Setup Django FIRST before any other imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import get_bot_config
from bot.middlewares.user_registration import UserRegistrationMiddleware
from bot.middlewares.logging_middleware import LoggingMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.services.notification_service import set_bot_instance

# Import all routers
from bot.routers import start, registration, admin, consumer, entrepreneur, complaints, stores, cashback, rights, support, common
from bot.routers import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config = get_bot_config()
    
    # Setup storage
    if config.redis_url and os.getenv('USE_REDIS', 'false').lower() == 'true':
        from redis.asyncio import Redis
        redis = Redis.from_url(config.redis_url)
        storage = RedisStorage(redis=redis)
        logger.info('Using Redis FSM storage')
    else:
        storage = MemoryStorage()
        logger.info('Using Memory FSM storage')
    
    # Setup bot
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    # Register bot instance for notifications
    set_bot_instance(bot)
    
    # Setup dispatcher
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
    
    logger.info('Starting SESPORT bot...')
    
    try:
        # Delete any existing webhook
        await bot.delete_webhook(drop_pending_updates=True)
        # Start polling
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info('Bot stopped.')


if __name__ == '__main__':
    asyncio.run(main())
