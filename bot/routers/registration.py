import re
import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from bot.states.registration import RegistrationStates
from bot.keyboards.language import language_keyboard
from bot.keyboards.registration import share_contact_keyboard, skip_keyboard, remove_keyboard
from bot.keyboards.role import role_keyboard
from bot.keyboards.consumer import consumer_keyboard
from bot.services.admin_service import is_admin_user
from bot.services.user_service import is_entrepreneur_user, update_user_language, get_user_language
from bot.utils.i18n import get_text, get_btn

logger = logging.getLogger(__name__)
router = Router(name='registration_router')

PHONE_RE = re.compile(r'^\+?[\d\s\-\(\)]{7,15}$')


def _clean_phone(raw: str) -> str:
    """Strip spaces/dashes, ensure leading +."""
    cleaned = re.sub(r'[\s\-\(\)]', '', raw.strip())
    if cleaned and not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    return cleaned


@sync_to_async
def _save_registration(
    telegram_id: int,
    full_name_input: str,
    phone: str | None,
    phone2: str | None,
    language: str = 'uz',
) -> None:
    from apps.users.models import TelegramUser
    parts = full_name_input.strip().split(None, 1)
    first = parts[0]
    last = parts[1] if len(parts) > 1 else None

    TelegramUser.objects.filter(telegram_id=telegram_id).update(
        full_name_input=full_name_input,
        first_name=first,
        last_name=last,
        phone_number=phone,
        phone_number2=phone2,
        language=language,
        is_registered=True,
    )


@sync_to_async
def _is_already_registered(telegram_id: int) -> bool:
    from apps.users.models import TelegramUser
    return TelegramUser.objects.filter(telegram_id=telegram_id, is_registered=True).exists()


# ─── Entry point ──────────────────────────────────────────────────────────

async def start_registration(message: Message, state: FSMContext) -> None:
    """Called from start.py when user is new (not yet registered)."""
    await state.clear()
    await state.set_state(RegistrationStates.waiting_for_language)
    await message.answer(
        "🇺🇿 <b>Assalomu alaykum! SESPORT botiga xush kelibsiz!</b>\n"
        "Iltimos, tilni tanlang.\n\n"
        "🇷🇺 <b>Здравствуйте! Добро пожаловать в бот SESPORT!</b>\n"
        "Пожалуйста, выберите язык.",
        parse_mode="HTML",
        reply_markup=language_keyboard(),
    )


# ─── Step 0: Language Selection ──────────────────────────────────────────

@router.message(RegistrationStates.waiting_for_language, F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def reg_receive_language(message: Message, state: FSMContext) -> None:
    lang = 'ru' if "Русский" in message.text else 'uz'
    await state.update_data(language=lang)
    await update_user_language(message.from_user.id, lang)

    await state.set_state(RegistrationStates.waiting_for_full_name)
    from bot.keyboards.complaint import cancel_keyboard
    await message.answer(
        get_text('welcome_onboarding', lang),
        parse_mode="HTML",
        reply_markup=cancel_keyboard(lang),
    )


@router.message(RegistrationStates.waiting_for_language)
async def reg_invalid_language(message: Message) -> None:
    await message.answer(
        "🇺🇿 Iltimos, quyidagi tugmalardan birini tanlang:\n"
        "🇷🇺 Пожалуйста, выберите один из вариантов ниже:",
        reply_markup=language_keyboard(),
    )


# ─── Step 1: Full name ────────────────────────────────────────────────────

@router.message(RegistrationStates.waiting_for_full_name, F.text)
async def reg_receive_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get('language', 'uz')
    name = message.text.strip()

    if name in ["❌ Bekor qilish", "❌ Отмена", "⬅️ Orqaga", "⬅️ Назад", "🔙 Asosiy menyu", "🔙 Главное меню"]:
        await state.clear()
        await start_registration(message, state)
        return

    if len(name) < 2 or len(name) > 100:
        await message.answer(
            get_text('invalid_name', lang),
            parse_mode="HTML",
        )
        return

    await state.update_data(full_name_input=name)
    await state.set_state(RegistrationStates.waiting_for_phone)
    await message.answer(
        get_text('ask_phone', lang, name=name),
        parse_mode="HTML",
        reply_markup=share_contact_keyboard(lang),
    )


# ─── Step 2: Phone (contact or manual) ───────────────────────────────────

@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def reg_receive_contact(message: Message, state: FSMContext) -> None:
    phone = _clean_phone(message.contact.phone_number)
    await state.update_data(phone=phone)
    await _ask_phone2(message, state)


@router.message(RegistrationStates.waiting_for_phone, F.text)
async def reg_receive_phone_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get('language', 'uz')
    text = message.text.strip()

    if text in ["❌ Bekor qilish", "❌ Отмена", "⬅️ Orqaga", "⬅️ Назад", "🔙 Asosiy menyu", "🔙 Главное меню"]:
        await state.set_state(RegistrationStates.waiting_for_full_name)
        from bot.keyboards.complaint import cancel_keyboard
        await message.answer(
            get_text('welcome_onboarding', lang),
            reply_markup=cancel_keyboard(lang),
            parse_mode="HTML",
        )
        return

    if not PHONE_RE.match(text):
        await message.answer(
            get_text('invalid_phone', lang),
            reply_markup=share_contact_keyboard(lang),
        )
        return
    phone = _clean_phone(text)
    await state.update_data(phone=phone)
    await _ask_phone2(message, state)


async def _ask_phone2(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get('language', 'uz')
    await state.set_state(RegistrationStates.waiting_for_phone2)
    await message.answer(
        get_text('ask_phone2', lang),
        parse_mode="HTML",
        reply_markup=skip_keyboard(lang),
    )


# ─── Step 3: Phone2 (optional) ────────────────────────────────────────────

@router.message(RegistrationStates.waiting_for_phone2, F.text.in_(["⏭ O'tkazib yuborish", "⏭ Пропустить"]))
async def reg_skip_phone2(message: Message, state: FSMContext) -> None:
    await _finish_registration(message, state, phone2=None)


@router.message(RegistrationStates.waiting_for_phone2, F.text)
async def reg_receive_phone2(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get('language', 'uz')
    text = message.text.strip()

    if text in ["❌ Bekor qilish", "❌ Отмена", "⬅️ Orqaga", "⬅️ Назад", "🔙 Asosiy menyu", "🔙 Главное меню"]:
        full_name = data.get('full_name_input', '')
        await state.set_state(RegistrationStates.waiting_for_phone)
        await message.answer(
            get_text('ask_phone', lang, name=full_name),
            reply_markup=share_contact_keyboard(lang),
            parse_mode="HTML",
        )
        return

    if not PHONE_RE.match(text):
        await message.answer(
            get_text('invalid_phone', lang),
            reply_markup=skip_keyboard(lang),
        )
        return
    phone2 = _clean_phone(text)
    await _finish_registration(message, state, phone2=phone2)


# ─── Finish ───────────────────────────────────────────────────────────────

async def _finish_registration(message: Message, state: FSMContext, phone2: str | None) -> None:
    data = await state.get_data()
    full_name = data.get('full_name_input', '')
    phone = data.get('phone')
    lang = data.get('language', 'uz')

    await _save_registration(
        telegram_id=message.from_user.id,
        full_name_input=full_name,
        phone=phone,
        phone2=phone2,
        language=lang,
    )
    await state.clear()

    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)

    phone2_label = "📞 Qo'shimcha raqam" if lang == 'uz' else "📞 Доп. номер"
    phone2_line = f"\n{phone2_label}: <b>{phone2}</b>" if phone2 else ""

    if is_admin or is_ent:
        await message.answer(
            get_text('reg_success_multi', lang, name=full_name, phone=phone or '—', phone2_line=phone2_line),
            parse_mode="HTML",
            reply_markup=role_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
        )
    else:
        await message.answer(
            get_text('reg_success', lang, name=full_name, phone=phone or '—', phone2_line=phone2_line),
            parse_mode="HTML",
            reply_markup=consumer_keyboard(is_admin=False, is_entrepreneur=False, lang=lang),
        )
