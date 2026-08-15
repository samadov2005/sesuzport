import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.entrepreneur import entrepreneur_keyboard
from bot.keyboards.role import role_keyboard
from bot.services.user_service import update_user_role

logger = logging.getLogger(__name__)
router = Router(name='entrepreneur_router')


@router.message(F.text == "💼 Tadbirkor")
async def role_entrepreneur(message: Message, state: FSMContext) -> None:
    await state.clear()
    await update_user_role(message.from_user.id, 'ENTREPRENEUR')
    await message.answer(
        "💼 <b>Tadbirkor menyusi</b>\n\n"
        "Do'konlaringizni boshqaring va statistikani kuzatib boring.\n"
        "Murojaatlarni ko'ring va reytingingizni oshiring.",
        reply_markup=entrepreneur_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text == "🏪 Mening do'konlarim")
async def my_stores(message: Message) -> None:
    await message.answer(
        "🏪 <b>Mening do'konlarim</b>\n\n"
        "Bu bo'limda siz ro'yxatdan o'tgan do'konlaringizni ko'rishingiz mumkin.\n\n"
        "📋 Hozircha ro'yxatdan o'tgan do'konlar yo'q.\n\n"
        "Do'kon qo'shish yoki tahrirlash uchun administrator bilan bog'laning:\n"
        "📱 Admin: @sesport_admin",
        parse_mode="HTML",
    )


@router.message(F.text == "📊 Do'kon statistikasi")
async def store_statistics(message: Message) -> None:
    await message.answer(
        "📊 <b>Do'kon statistikasi</b>\n\n"
        "Bu bo'limda do'koningizga kelib tushgan murojaatlar va reyting statistikasi ko'rinadi.\n\n"
        "📈 Jami murojaatlar: <b>0</b>\n"
        "✅ Hal qilingan: <b>0</b>\n"
        "⭐ O'rtacha reyting: <b>—</b>\n\n"
        "Do'kon ro'yxatdan o'tgandan so'ng statistika ko'rinadi.",
        parse_mode="HTML",
    )


@router.message(F.text == "📋 Murojaatlar")
async def entrepreneur_complaints(message: Message) -> None:
    await message.answer(
        "📋 <b>Do'koningizga kelgan murojaatlar</b>\n\n"
        "Hozircha do'koningizga murojaatlar yo'q.\n\n"
        "Yangi murojaatlar kelganida siz xabardor qilinasiz.",
        parse_mode="HTML",
    )


@router.message(F.text == "⭐ Reytingim")
async def entrepreneur_rating(message: Message) -> None:
    await message.answer(
        "⭐ <b>Do'kon reytingi</b>\n\n"
        "Do'koningizning xavfsizlik holati va reytingi:\n\n"
        "🛡 Xavfsizlik holati: <b>Aniqlanmagan</b>\n"
        "⭐ Reyting: <b>—/5.0</b>\n"
        "📊 Baholashlar soni: <b>0</b>\n\n"
        "Reyting iste'molchilarning murojaatlari va moderatsiya natijalari asosida shakllanadi.",
        parse_mode="HTML",
    )


@router.message(F.text == "💰 Keshbek")
async def entrepreneur_cashback(message: Message) -> None:
    await message.answer(
        "💰 <b>Tadbirkor keshbek dasturi</b>\n\n"
        "Tadbirkorlar uchun keshbek dasturi:\n"
        "• Do'koningiz xavfsizlik holatini yaxshilang\n"
        "• Murojaatlarni tezda hal qiling\n"
        "• Bonus imtiyozlar oling\n\n"
        "💳 Keshbek balansi: <b>0 so'm</b>\n\n"
        "Batafsil ma'lumot uchun administrator bilan bog'laning.",
        parse_mode="HTML",
    )


@router.message(F.text == "💬 Yordam")
async def entrepreneur_support(message: Message) -> None:
    # Redirect to support router — handled there
    pass
