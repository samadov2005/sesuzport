import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError

from bot.keyboards.consumer import consumer_keyboard
from bot.services.user_service import get_user_language, is_entrepreneur_user
from bot.services.admin_service import is_admin_user

logger = logging.getLogger(__name__)
router = Router(name='common_router')


@router.message(F.text.in_(["❌ Bekor qilish", "❌ Отмена", "/cancel", "⬅️ Asosiy menyu", "⬅️ Главное меню", "🔙 Asosiy menyu", "🔙 Главное меню", "⬅️ Orqaga", "⬅️ Назад"]))
async def global_cancel_or_back(message: Message, state: FSMContext) -> None:
    """Global catch-all for Cancel and Back in any menu/state."""
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)
    text = "Asosiy menyuga qaytdingiz." if lang == 'uz' else "Вы вернулись в главное меню."
    await message.answer(
        text,
        reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
    )


from aiogram.types import Message, ErrorEvent


@router.errors()
async def error_handler(event: ErrorEvent):
    logger.exception(f"Exception handling update: {event.update}\n{event.exception}")
    if event.update and event.update.message:
        try:
            await event.update.message.answer("⚠️ Texnik xatolik yuz berdi. Iltimos, birozdan so'ng qayta urinib ko'ring.")
        except Exception:
            pass


@router.message()
async def unhandled_message(message: Message):
    lang = await get_user_language(message.from_user.id)
    if lang == 'ru':
        text = "Извините, команда не распознана. Воспользуйтесь меню ниже или введите /help."
    else:
        text = "Kechirasiz, bu buyruqni tushunmadim. Pastdagi menyudan foydalaning yoki /help buyrug'ini bosing."
    await message.answer(text)
