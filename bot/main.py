from __future__ import annotations
from pathlib import Path
import asyncio
import logging
import os
import sys
import aiohttp

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

from bot.config import get_bot_config
from bot.dispatcher import get_bot, get_dispatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


async def keep_alive() -> None:
    """Render.com 15 daqiqada uxlab qolmasligi uchun har 3 daqiqada /healthz/ ga so'rov yuboradi"""
    base_url = os.getenv('WEBAPP_URL', os.getenv('RENDER_EXTERNAL_URL', 'https://sesuzport.onrender.com'))
    if not base_url.startswith('http'):
        base_url = f"https://{base_url}"
    ping_url = f"{base_url.rstrip('/')}/healthz/"
    port = os.getenv('PORT', '8000')
    local_url = f"http://127.0.0.1:{port}/healthz/"
    
    await asyncio.sleep(30)  # Konteyner to'liq yuklangach boshlaydi
    logger.info(f"Keep-alive self-ping vazifasi boshlandi (tashqi: {ping_url}, mahalliy: {local_url})")
    
    while True:
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # 1. Tashqi Render routerini faol tutish
                try:
                    async with session.get(ping_url) as resp:
                        logger.info(f"Keep-alive ping (tashqi): {ping_url} -> status {resp.status}")
                except Exception as ex:
                    logger.debug(f"Tashqi ping xatosi: {ex}")
                # 2. Mahalliy Gunicorn jarayonini tekshirish
                try:
                    async with session.get(local_url) as resp:
                        logger.debug(f"Keep-alive ping (mahalliy): status {resp.status}")
                except Exception as ex:
                    logger.debug(f"Mahalliy ping xatosi: {ex}")
        except Exception as e:
            logger.debug(f"Keep-alive session xatosi: {e}")
            
        await asyncio.sleep(180)  # Har 3 daqiqada (15 daqiqalik render uyqusidan oldinroq)


async def main() -> None:
    bot = get_bot()
    dp = get_dispatcher()
    
    logger.info('Starting SESPORT bot...')
    
    # Keep-alive vazifasi
    asyncio.create_task(keep_alive())
    
    while True:
        try:
            # Webhookni tozalash
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Telegram long-polling boshlandi...")
            await dp.start_polling(bot, handle_signals=True)
            break
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot to'xtatildi (signal orqali).")
            break
        except Exception as exc:
            logger.error(f"Polling xatosi ro'y berdi: {exc}. 5 soniyada qayta ulanadi...")
            await asyncio.sleep(5)
            
    await bot.session.close()
    logger.info('Bot stopped.')


if __name__ == '__main__':
    asyncio.run(main())
