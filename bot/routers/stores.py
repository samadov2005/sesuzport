import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.consumer import consumer_keyboard
from bot.keyboards.common import store_location_keyboard, store_search_cancel_keyboard
from bot.services.store_service import get_nearby_stores, search_stores, get_all_stores_list
from bot.utils.formatters import format_store_card
from bot.states.complaint import ComplaintStates
from bot.states.stores import StoreSearchStates

logger = logging.getLogger(__name__)
router = Router(name='stores_router')


@router.message(F.text.in_(["🏪 Do'konlarni tekshirish", "Do'konlarni tekshirish", "/stores"]))
async def check_stores(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    # Don't interfere if we're in complaint FSM
    if current in [
        ComplaintStates.waiting_for_description,
        ComplaintStates.waiting_for_photo,
        ComplaintStates.waiting_for_location,
    ]:
        return

    await state.set_state(StoreSearchStates.waiting_for_query)
    await message.answer(
        "🏪 <b>Do'konlarni tekshirish va xavfsizlik reytingi</b>\n\n"
        "Atrofingizdagi do'konlarni topish uchun quyidagi usullardan foydalanishingiz mumkin:\n\n"
        "📍 <b>Joylashuvimni yuborish</b> — eng yaqin do'konlar va ulargacha bo'lgan masofani aniqlash\n"
        "🔍 <b>Nomi bo'yicha qidirish</b> — do'kon nomi yoki manzili bo'yicha qidirish\n"
        "📋 <b>Barcha do'konlar</b> — ro'yxatdan o'tgan barcha do'konlar\n\n"
        "<i>Yoki to'g'ridan-to'g'ri qidirilayotgan do'kon nomini xabar qilib yozishingiz mumkin.</i>",
        reply_markup=store_location_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.location)
async def handle_location_for_stores(message: Message, state: FSMContext) -> None:
    """Handle location for store proximity search."""
    current = await state.get_state()
    # If in complaint FSM, skip (complaint router handles it)
    if current == ComplaintStates.waiting_for_location:
        return

    lat = message.location.latitude
    lon = message.location.longitude
    loading_msg = await message.answer("🔍 Yaqin atrofdagi do'konlar hisoblanmoqda...")

    try:
        results, is_close = await get_nearby_stores(lat, lon, limit=6)
        if not results:
            stores = await get_all_stores_list(limit=10)
            if not stores:
                await message.answer(
                    "❌ Hozircha tizimda faol do'konlar mavjud emas.",
                    reply_markup=consumer_keyboard(),
                )
                return
            text = "📍 Yaqin atrofda do'kon topilmadi. Barcha do'konlar:\n\n"
            text += "\n\n".join(format_store_card(s) for s in stores)
        else:
            if is_close:
                text = f"🏪 <b>Sizga eng yaqin do'konlar ({len(results)} ta):</b>\n\n"
            else:
                text = (
                    f"📍 <b>Hududingizga eng yaqin do'konlar (masofa bo'yicha saralangan):</b>\n\n"
                    f"<i>(Atrofingizda bevosita yaqin do'kon bo'lmasa, eng yaqin filiallar ko'rsatiladi)</i>\n\n"
                )
            text += "\n\n──────────────\n\n".join(format_store_card(store, dist) for store, dist in results)

        try:
            await loading_msg.delete()
        except Exception:
            pass

        await message.answer(
            text,
            reply_markup=consumer_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.error(f"Store location search error: {e}", exc_info=True)
        await message.answer(
            "⚠️ Do'konlarni qidirishda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=consumer_keyboard(),
        )
    finally:
        await state.clear()


@router.message(F.text.in_(["🔍 Nomi bo'yicha qidirish", "🔍 Do'kon nomini kiriting"]))
async def prompt_store_search_name(message: Message, state: FSMContext) -> None:
    await state.set_state(StoreSearchStates.waiting_for_query)
    await message.answer(
        "🔍 Qidirilayotgan do'kon nomini yoki manzilini yozing:\n"
        "<i>(Masalan: Korzinka, Makro, Samarqand darvoza, Yunusobod)</i>",
        reply_markup=store_search_cancel_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text.in_(["📋 Barcha do'konlar", "/all_stores"]))
async def all_stores(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        stores = await get_all_stores_list(limit=25)
        if not stores:
            await message.answer("❌ Hozircha tizimda do'konlar yo'q.", reply_markup=consumer_keyboard())
            return
        text = f"🏪 <b>Barcha ro'yxatdan o'tgan do'konlar ({len(stores)} ta):</b>\n\n"
        text += "\n\n──────────────\n\n".join(format_store_card(s) for s in stores)
        await message.answer(
            text,
            reply_markup=consumer_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.error(f"All stores error: {e}", exc_info=True)
        await message.answer("⚠️ Xatolik yuz berdi.", reply_markup=consumer_keyboard())


@router.message(F.text.in_(["⬅️ Asosiy menyu", "❌ Bekor qilish", "Bekor qilish"]))
async def cancel_store_search(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Asosiy menyu:", reply_markup=consumer_keyboard())


@router.message(StoreSearchStates.waiting_for_query, F.text)
async def process_store_text_search(message: Message, state: FSMContext) -> None:
    query = (message.text or '').strip()
    if not query or query in ["⬅️ Asosiy menyu", "❌ Bekor qilish"]:
        await state.clear()
        await message.answer("Asosiy menyu:", reply_markup=consumer_keyboard())
        return

    try:
        stores = await search_stores(query)
        if not stores:
            await message.answer(
                f"❌ <b>«{query}»</b> bo'yicha hech qanday do'kon topilmadi.\n\n"
                f"Boshqa nom bilan qidirib ko'ring yoki «📋 Barcha do'konlar» tugmasini bosing.",
                reply_markup=store_search_cancel_keyboard(),
                parse_mode="HTML",
            )
            return

        text = f"🔍 <b>«{query}» bo'yicha topilgan do'konlar ({len(stores)} ta):</b>\n\n"
        text += "\n\n──────────────\n\n".join(format_store_card(s) for s in stores)
        await message.answer(
            text,
            reply_markup=consumer_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Store search error for query '{query}': {e}", exc_info=True)
        await message.answer(
            "⚠️ Qidiruvda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
            reply_markup=consumer_keyboard(),
        )
