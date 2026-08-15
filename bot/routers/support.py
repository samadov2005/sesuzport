from aiogram import Router, F
from aiogram.types import Message
from asgiref.sync import sync_to_async
from apps.support.models import SupportConfiguration

router = Router(name='support_router')

@router.message(F.text == "💬 Yordam")
async def show_support(message: Message):
    @sync_to_async
    def get_support():
        return SupportConfiguration.objects.filter(is_active=True).first()
        
    support = await get_support()
    
    if not support:
        await message.answer("Yordam ma'lumotlari hozircha mavjud emas.")
        return
        
    text = (
        f"💬 Yordam\n\n"
        f"📞 Telefon: {support.phone}\n"
        f"✉️ Email: {support.email}\n"
        f"💬 Telegram: @{support.telegram_username}\n"
        f"⏰ Ish vaqti: {support.working_hours}\n\n"
        f"{support.description}"
    )
    
    await message.answer(text)
