import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states.settings import SettingsStates
from bot.keyboards.settings import settings_keyboard
from bot.keyboards.language import language_keyboard
from bot.keyboards.consumer import consumer_keyboard
from bot.keyboards.entrepreneur import entrepreneur_keyboard
from bot.services.user_service import get_user_language, update_user_language, is_entrepreneur_user
from bot.services.admin_service import is_admin_user
from bot.utils.i18n import get_text, get_btn

logger = logging.getLogger(__name__)
router = Router(name='settings_router')


@router.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки", "/settings"]))
async def open_settings(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    await message.answer(
        get_text('settings_header', lang),
        parse_mode="HTML",
        reply_markup=settings_keyboard(lang),
    )


@router.message(F.text.in_(["🌐 Tilni o'zgartirish", "🌐 Изменить язык"]))
async def change_language_prompt(message: Message, state: FSMContext) -> None:
    lang = await get_user_language(message.from_user.id)
    await state.set_state(SettingsStates.waiting_for_language)
    await message.answer(
        get_text('select_new_language', lang),
        reply_markup=language_keyboard(show_back=True, lang=lang),
    )


@router.message(SettingsStates.waiting_for_language, F.text.in_(["⬅️ Orqaga", "⬅️ Назад", "❌ Bekor qilish", "❌ Отмена"]))
async def cancel_language_change(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    await message.answer(
        get_text('settings_header', lang),
        parse_mode="HTML",
        reply_markup=settings_keyboard(lang),
    )


@router.message(SettingsStates.waiting_for_language, F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def process_language_change(message: Message, state: FSMContext) -> None:
    new_lang = 'ru' if "Русский" in message.text else 'uz'
    await update_user_language(message.from_user.id, new_lang)
    await state.clear()

    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)

    await message.answer(
        get_text('language_changed', new_lang),
        parse_mode="HTML",
        reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=new_lang),
    )


@router.message(F.text.in_(["🔙 Asosiy menyu", "🔙 Главное меню", "⬅️ Asosiy menyu", "⬅️ Главное меню", "⬅️ Orqaga", "⬅️ Назад"]))
async def back_to_main_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)

    await message.answer(
        get_text('main_menu', lang),
        reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
    )
