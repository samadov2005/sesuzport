import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError

logger = logging.getLogger(__name__)
router = Router(name='common_router')

@router.errors()
async def error_handler(update, exception):
    logger.exception(f"Exception handling update: {update}\n{exception}")
    if update.message:
        try:
            await update.message.answer("⚠️ Texnik xatolik yuz berdi. Iltimos, birozdan so'ng qayta urinib ko'ring.")
        except TelegramAPIError:
            pass

@router.message()
async def unhandled_message(message: Message):
    await message.answer("Kechirasiz, bu buyruqni tushunmadim. /help buyrug'ini kiriting.")
