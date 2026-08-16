import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.consumer import consumer_keyboard
from bot.keyboards.common import back_keyboard
from bot.services.cashback_service import get_cashback_balance, get_cashback_transactions
from bot.services.user_service import get_user_language
from bot.utils.formatters import format_cashback_info, format_money, format_transaction_type, format_datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)
router = Router(name='cashback_router')


def cashback_history_keyboard(page: int, total_pages: int, lang: str = 'uz') -> InlineKeyboardMarkup:
    buttons = []
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"cb_hist_{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="ignore"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"cb_hist_{page + 1}"))
    if nav:
        buttons.append(nav)
    refresh_text = "🔄 Yangilash" if lang == 'uz' else "🔄 Обновить"
    buttons.append([InlineKeyboardButton(text=refresh_text, callback_data="cb_refresh")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text.in_(["💳 Keshbeklarni kuzatish", "💳 Мой кэшбэк"]))
async def view_cashback(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    try:
        data = await get_cashback_balance(message.from_user.id)
        text = format_cashback_info(data)
        hist_btn = "📋 Tranzaksiyalar tarixi" if lang == 'uz' else "📋 История транзакций"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=hist_btn, callback_data="cb_hist_1")],
        ])
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Cashback error for {message.from_user.id}: {e}")
        await message.answer("⚠️ " + ("Keshbek ma'lumotlarini olishda xatolik yuz berdi." if lang == 'uz' else "Ошибка при получении кэшбэка."))


@router.callback_query(F.data == "cb_refresh")
async def cashback_refresh(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    try:
        data = await get_cashback_balance(callback.from_user.id)
        text = format_cashback_info(data)
        hist_btn = "📋 Tranzaksiyalar tarixi" if lang == 'uz' else "📋 История транзакций"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=hist_btn, callback_data="cb_hist_1")],
        ])
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer("✅ " + ("Yangilandi!" if lang == 'uz' else "Обновлено!"))
    except Exception as e:
        logger.error(f"Cashback refresh error: {e}")
        await callback.answer("Xatolik yuz berdi.")


@router.callback_query(F.data.startswith("cb_hist_"))
async def cashback_history(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    try:
        page = int(callback.data.split("_")[2])
        txs, total_pages = await get_cashback_transactions(callback.from_user.id, page=page)

        if not txs:
            await callback.answer("Tranzaksiyalar yo'q." if lang == 'uz' else "Нет транзакций.")
            return

        title = f"📋 <b>Tranzaksiyalar tarixi</b> (sahifa {page}/{total_pages}):\n" if lang == 'uz' else f"📋 <b>История транзакций</b> (страница {page}/{total_pages}):\n"
        lines = [title]
        for tx in txs:
            sign = "➕" if tx.transaction_type == "EARN" else "➖"
            lines.append(
                f"{sign} <b>{format_money(tx.amount)}</b>\n"
                f"   📝 {tx.description[:50]}\n"
                f"   🕐 {format_datetime(tx.created_at)}\n"
            )
        text = "\n".join(lines)

        keyboard = cashback_history_keyboard(page, total_pages, lang=lang)
        try:
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        except Exception:
            await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        logger.error(f"Cashback history error: {e}")
        await callback.answer("Xatolik yuz berdi.")
