from aiogram import Router, F
from aiogram.types import Message
from bot.keyboards.consumer import consumer_keyboard
from bot.services.user_service import update_user_role, is_entrepreneur_user, get_user_language
from bot.services.admin_service import is_admin_user
from bot.utils.i18n import get_text

router = Router(name='consumer_router')

@router.message(F.text.in_(["👤 Iste'molchi (Mijoz)", "👤 Потребитель (Клиент)"]))
async def role_consumer(message: Message):
    await update_user_role(message.from_user.id, 'CONSUMER')
    lang = await get_user_language(message.from_user.id)
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)
    await message.answer(
        get_text('consumer_menu_header', lang),
        reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang)
    )
