import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.role import role_keyboard
from bot.keyboards.consumer import consumer_keyboard
from bot.keyboards.entrepreneur import entrepreneur_keyboard

logger = logging.getLogger(__name__)
router = Router(name='start_router')


HELP_TEXT = (
    "🛡️ <b>SESPORT — Iste'molchilarni himoya qilish platformasi</b>\n\n"
    "📋 <b>Buyruqlar:</b>\n"
    "/start — Botni qayta boshlash va rol tanlash\n"
    "/cancel — Joriy amalni bekor qilish\n"
    "/help — Yordam\n\n"
    "📌 <b>Asosiy funksiyalar (Iste'molchi):</b>\n"
    "📝 Shikoyat qilish — Muddati o'tgan yoki buzilgan mahsulot haqida murojaat\n"
    "📁 Mening murojaatlarim — Barcha murojaatlaringizni ko'ring\n"
    "🏪 Do'konlarni tekshirish — Yaqin atrofdagi do'konlar va xavfsizlik reytingi\n"
    "💳 Keshbeklarni kuzatish — Keshbek hisobingiz va tarixi\n"
    "⚖️ Huquqlarim — Iste'molchi huquqlari ma'lumotlari\n"
    "💬 Yordam — Aloqa ma'lumotlari\n\n"
    "❓ Muammo bo'lsa, /cancel bilan amalni bekor qiling."
)


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    from bot.routers.registration import _is_already_registered, start_registration
    from bot.services.admin_service import is_admin_user

    already_registered = await _is_already_registered(message.from_user.id)

    if not already_registered:
        # New user: run onboarding registration flow
        await start_registration(message, state)
        return

    is_admin = await is_admin_user(message.from_user.id)
    await message.answer(
        "🛡️ <b>SESPORT</b> — Xush kelibsiz!\n\n"
        "Rolingizni tanlang:",
        reply_markup=role_keyboard(is_admin=is_admin),
        parse_mode="HTML",
    )


@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML")


@router.message(Command('cancel'))
async def cmd_cancel(message: Message, state: FSMContext, **data) -> None:
    current_state = await state.get_state()
    await state.clear()

    telegram_user = data.get('telegram_user')
    role = telegram_user.role if telegram_user else None

    if current_state:
        await message.answer("❌ Amal bekor qilindi.")
    else:
        await message.answer("❌ Bekor qilinadigan faol amal yo'q.")

    if role == 'CONSUMER':
        await message.answer("Asosiy menyu:", reply_markup=consumer_keyboard())
    elif role == 'ENTREPRENEUR':
        await message.answer("Asosiy menyu:", reply_markup=entrepreneur_keyboard())
    else:
        await message.answer("Rolingizni tanlang:", reply_markup=role_keyboard())


@router.message(F.text == '🔄 Rolni almashtirish')
async def change_role(message: Message, state: FSMContext) -> None:
    await state.clear()
    from bot.services.admin_service import is_admin_user
    is_admin = await is_admin_user(message.from_user.id)
    await message.answer(
        "Rolingizni tanlang:",
        reply_markup=role_keyboard(is_admin=is_admin),
    )
