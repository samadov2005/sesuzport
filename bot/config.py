from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfig:
    token: str
    webhook_url: str | None
    webhook_secret: str | None
    redis_url: str
    webapp_url: str
    archive_channel_id: str | None

def get_bot_config() -> BotConfig:
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError('BOT_TOKEN environment variable is required')
    raw_webapp_url = (os.getenv('WEBAPP_URL') or os.getenv('RENDER_EXTERNAL_URL') or 'https://sesuzport.onrender.com').strip().rstrip('/')
    if 'sesportuz.onrender.com' in raw_webapp_url:
        raw_webapp_url = raw_webapp_url.replace('sesportuz.onrender.com', 'sesuzport.onrender.com')
    return BotConfig(
        token=token,
        webhook_url=os.getenv('WEBHOOK_URL'),
        webhook_secret=os.getenv('WEBHOOK_SECRET'),
        redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        webapp_url=raw_webapp_url,
        archive_channel_id=os.getenv('ARCHIVE_CHANNEL_ID') or os.getenv('MEDIA_CHANNEL_ID'),
    )

