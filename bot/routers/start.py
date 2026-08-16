import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.role import role_keyboard
from bot.keyboards.consumer import consumer_keyboard
from bot.keyboards.entrepreneur import entrepreneur_keyboard
from bot.services.user_service import get_user_language, is_entrepreneur_user
from bot.services.admin_service import is_admin_user
from bot.utils.i18n import get_text, get_btn

logger = logging.getLogger(__name__)
router = Router(name='start_router')


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    from bot.routers.registration import _is_already_registered, start_registration

    already_registered = await _is_already_registered(message.from_user.id)

    if not already_registered:
        # New user: run onboarding registration flow with language choice
        await start_registration(message, state)
        return

    lang = await get_user_language(message.from_user.id)
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)

    if is_admin or is_ent:
        await message.answer(
            get_text('select_role', lang),
            reply_markup=role_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            get_text('welcome_back', lang),
            reply_markup=consumer_keyboard(is_admin=False, is_entrepreneur=False, lang=lang),
            parse_mode="HTML",
        )


@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    await message.answer(get_text('help_text', lang), parse_mode="HTML")


@router.message(Command('cancel'))
async def cmd_cancel(message: Message, state: FSMContext, **data) -> None:
    current_state = await state.get_state()
    await state.clear()

    telegram_user = data.get('telegram_user')
    role = telegram_user.role if telegram_user else None

    lang = await get_user_language(message.from_user.id)

    if current_state:
        await message.answer(get_text('action_cancelled', lang))
    else:
        await message.answer(get_text('no_active_action', lang))

    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)

    if role == 'ENTREPRENEUR' and (is_ent or is_admin):
        await message.answer(
            get_text('main_menu', lang),
            reply_markup=entrepreneur_keyboard(is_admin=is_admin, lang=lang)
        )
    elif role in ['ADMIN', 'MODERATOR'] and is_admin:
        await message.answer(
            get_text('main_menu', lang),
            reply_markup=role_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang)
        )
    else:
        await message.answer(
            get_text('main_menu', lang),
            reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang)
        )


@router.message(F.text.in_(["🔄 Rolni almashtirish", "🔄 Сменить роль"]))
async def change_role(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)

    if not (is_admin or is_ent):
        await message.answer(
            "Sizda faqat Iste'molchi roli mavjud." if lang == 'uz' else "Вам доступна только роль потребителя.",
            reply_markup=consumer_keyboard(is_admin=False, is_entrepreneur=False, lang=lang),
        )
        return

    await message.answer(
        get_text('select_role', lang),
        reply_markup=role_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang, show_back=True),
    )
