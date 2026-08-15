import re
import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from bot.states.registration import RegistrationStates
from bot.keyboards.registration import share_contact_keyboard, skip_keyboard, remove_keyboard
from bot.keyboards.role import role_keyboard
from bot.services.admin_service import is_admin_user

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
) -> None:
    from apps.users.models import TelegramUser
    # Split name into first/last for Telegram compatibility
    parts = full_name_input.strip().split(None, 1)
    first = parts[0]
    last = parts[1] if len(parts) > 1 else None

    TelegramUser.objects.filter(telegram_id=telegram_id).update(
        full_name_input=full_name_input,
        first_name=first,
        last_name=last,
        phone_number=phone,
        phone_number2=phone2,
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
    await state.set_state(RegistrationStates.waiting_for_full_name)
    await message.answer(
        "👋 <b>SESPORT botiga xush kelibsiz!</b>\n\n"
        "Sizni ro'yxatdan o'tkazib olaylik — bu bir necha soniya oladi.\n\n"
        "1️⃣ <b>Ism va familyangizni</b> kiriting:\n"
        "<i>(masalan: Aziz Karimov)</i>",
        parse_mode="HTML",
        reply_markup=remove_keyboard(),
    )


# ─── Step 1: Full name ────────────────────────────────────────────────────

@router.message(RegistrationStates.waiting_for_full_name, F.text)
async def reg_receive_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if len(name) < 2 or len(name) > 100:
        await message.answer(
            "⚠️ Iltimos, <b>haqiqiy ism va familyangizni</b> kiriting (2–100 belgi).",
            parse_mode="HTML",
        )
        return

    await state.update_data(full_name_input=name)
    await state.set_state(RegistrationStates.waiting_for_phone)
    await message.answer(
        f"✅ <b>{name}</b> — qabul qilindi!\n\n"
        "2️⃣ <b>Telefon raqamingizni</b> ulashing:\n"
        "Pastdagi tugmani bosing yoki raqamni qo'lda kiriting.",
        parse_mode="HTML",
        reply_markup=share_contact_keyboard(),
    )


# ─── Step 2: Phone (contact or manual) ───────────────────────────────────

@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def reg_receive_contact(message: Message, state: FSMContext) -> None:
    phone = _clean_phone(message.contact.phone_number)
    await state.update_data(phone=phone)
    await _ask_phone2(message, state)


@router.message(RegistrationStates.waiting_for_phone, F.text)
async def reg_receive_phone_text(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if not PHONE_RE.match(text):
        await message.answer(
            "⚠️ Noto'g'ri format. Iltimos, telefon raqamingizni kiriting yoki "
            "quyidagi tugmani bosing:",
            reply_markup=share_contact_keyboard(),
        )
        return
    phone = _clean_phone(text)
    await state.update_data(phone=phone)
    await _ask_phone2(message, state)


async def _ask_phone2(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationStates.waiting_for_phone2)
    await message.answer(
        "3️⃣ <b>Qo'shimcha telefon raqam</b> (ixtiyoriy):\n\n"
        "Agar ikkinchi raqamingiz bo'lsa kiriting, aks holda «⏭ O'tkazib yuborish» tugmasini bosing.",
        parse_mode="HTML",
        reply_markup=skip_keyboard(),
    )


# ─── Step 3: Phone2 (optional) ────────────────────────────────────────────

@router.message(RegistrationStates.waiting_for_phone2, F.text == "⏭ O'tkazib yuborish")
async def reg_skip_phone2(message: Message, state: FSMContext) -> None:
    await _finish_registration(message, state, phone2=None)


@router.message(RegistrationStates.waiting_for_phone2, F.text)
async def reg_receive_phone2(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if not PHONE_RE.match(text):
        await message.answer(
            "⚠️ Noto'g'ri format. Raqamni kiriting yoki o'tkazib yuboring:",
            reply_markup=skip_keyboard(),
        )
        return
    phone2 = _clean_phone(text)
    await _finish_registration(message, state, phone2=phone2)


# ─── Finish ───────────────────────────────────────────────────────────────

async def _finish_registration(message: Message, state: FSMContext, phone2: str | None) -> None:
    data = await state.get_data()
    full_name = data.get('full_name_input', '')
    phone = data.get('phone')

    await _save_registration(
        telegram_id=message.from_user.id,
        full_name_input=full_name,
        phone=phone,
        phone2=phone2,
    )
    await state.clear()

    is_admin = await is_admin_user(message.from_user.id)

    phone2_line = f"\n📞 Qo'shimcha raqam: <b>{phone2}</b>" if phone2 else ""
    await message.answer(
        f"🎉 <b>Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!</b>\n\n"
        f"👤 Ism: <b>{full_name}</b>\n"
        f"📱 Asosiy raqam: <b>{phone or '—'}</b>{phone2_line}\n\n"
        f"Endi platformadan to'liq foydalanishingiz mumkin. Rolingizni tanlang:",
        parse_mode="HTML",
        reply_markup=role_keyboard(is_admin=is_admin),
    )
