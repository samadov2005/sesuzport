import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.consumer import consumer_keyboard
from bot.keyboards.common import store_location_keyboard, store_search_cancel_keyboard
from bot.services.store_service import get_nearby_stores, search_stores, get_all_stores_list
from bot.services.user_service import get_user_language, is_entrepreneur_user
from bot.services.admin_service import is_admin_user
from bot.utils.formatters import format_store_card
from bot.states.complaint import ComplaintStates
from bot.states.stores import StoreSearchStates

logger = logging.getLogger(__name__)
router = Router(name='stores_router')


@router.message(F.text.in_(["🏪 Do'konlarni tekshirish", "🏪 Проверка магазинов", "Do'konlarni tekshirish", "/stores"]))
async def check_stores(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    # Don't interfere if we're in complaint FSM
    if current in [
        ComplaintStates.waiting_for_description,
        ComplaintStates.waiting_for_photo,
        ComplaintStates.waiting_for_location,
    ]:
        return

    lang = await get_user_language(message.from_user.id)
    await state.set_state(StoreSearchStates.waiting_for_query)
    
    if lang == 'ru':
        text = (
            "🏪 <b>Проверка магазинов и рейтинг безопасности</b>\n\n"
            "Чтобы найти магазины вокруг вас:\n\n"
            "📍 <b>Отправить местоположение</b> — найти ближайшие магазины\n"
            "🔍 <b>Поиск по названию</b> — найти по имени или адресу\n"
            "📋 <b>Все магазины</b> — список всех зарегистрированных магазинов\n\n"
            "<i>Либо просто отправьте название магазина текстовым сообщением.</i>"
        )
    else:
        text = (
            "🏪 <b>Do'konlarni tekshirish va xavfsizlik reytingi</b>\n\n"
            "Atrofingizdagi do'konlarni topish uchun quyidagi usullardan foydalanishingiz mumkin:\n\n"
            "📍 <b>Joylashuvimni yuborish</b> — eng yaqin do'konlar va ulargacha bo'lgan masofani aniqlash\n"
            "🔍 <b>Nomi bo'yicha qidirish</b> — do'kon nomi yoki manzili bo'yicha qidirish\n"
            "📋 <b>Barcha do'konlar</b> — ro'yxatdan o'tgan barcha do'konlar\n\n"
            "<i>Yoki to'g'ridan-to'g'ri qidirilayotgan do'kon nomini xabar qilib yozishingiz mumkin.</i>"
        )
    await message.answer(
        text,
        reply_markup=store_location_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(F.location)
async def handle_location_for_stores(message: Message, state: FSMContext) -> None:
    """Handle location for store proximity search."""
    current = await state.get_state()
    # If in complaint FSM, skip (complaint router handles it)
    if current == ComplaintStates.waiting_for_location:
        return

    lang = await get_user_language(message.from_user.id)
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)

    lat = message.location.latitude
    lon = message.location.longitude
    loading_msg = await message.answer("🔍 " + ("Yaqin atrofdagi do'konlar hisoblanmoqda..." if lang == 'uz' else "Ищем ближайшие магазины..."))

    try:
        results, is_close = await get_nearby_stores(lat, lon, limit=6)
        if not results:
            stores = await get_all_stores_list(limit=10)
            if not stores:
                await message.answer(
                    "❌ " + ("Hozircha tizimda faol do'konlar mavjud emas." if lang == 'uz' else "В системе пока нет активных магазинов."),
                    reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
                )
                return
            title = "📍 Yaqin atrofda do'kon topilmadi. Barcha do'konlar:\n\n" if lang == 'uz' else "📍 Поблизости магазинов не найдено. Все магазины:\n\n"
            text = title + "\n\n".join(format_store_card(s) for s in stores)
        else:
            if is_close:
                text = f"🏪 <b>" + (f"Sizga eng yaqin do'konlar ({len(results)} ta):" if lang == 'uz' else f"Ближайшие к вам магазины ({len(results)}):") + "</b>\n\n"
            else:
                text = (
                    f"📍 <b>" + ("Hududingizga eng yaqin do'konlar (masofa bo'yicha saralangan):" if lang == 'uz' else "Ближайшие к вашему району магазины:") + "</b>\n\n"
                )
            text += "\n\n──────────────\n\n".join(format_store_card(store, dist) for store, dist in results)

        try:
            await loading_msg.delete()
        except Exception:
            pass

        await message.answer(
            text,
            reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.error(f"Store location search error: {e}", exc_info=True)
        await message.answer(
            "⚠️ " + ("Do'konlarni qidirishda xatolik yuz berdi." if lang == 'uz' else "Произошла ошибка при поиске."),
            reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
        )
    finally:
        await state.clear()


@router.message(F.text.in_(["🔍 Nomi bo'yicha qidirish", "🔍 Поиск по названию", "🔍 Do'kon nomini kiriting"]))
async def prompt_store_search_name(message: Message, state: FSMContext) -> None:
    lang = await get_user_language(message.from_user.id)
    await state.set_state(StoreSearchStates.waiting_for_query)
    text = (
        "🔍 Qidirilayotgan do'kon nomini yoki manzilini yozing:\n<i>(Masalan: Korzinka, Makro, Yunusobod)</i>"
        if lang == 'uz' else
        "🔍 Введите название или адрес магазина:\n<i>(Например: Корзинка, Макро, Юнусабад)</i>"
    )
    await message.answer(
        text,
        reply_markup=store_search_cancel_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(F.text.in_(["📋 Barcha do'konlar", "📋 Все магазины", "/all_stores"]))
async def all_stores(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)
    try:
        stores = await get_all_stores_list(limit=25)
        if not stores:
            await message.answer("❌ " + ("Hozircha tizimda do'konlar yo'q." if lang == 'uz' else "В системе пока нет магазинов."), reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang))
            return
        title = f"🏪 <b>Barcha ro'yxatdan o'tgan do'konlar ({len(stores)} ta):</b>\n\n" if lang == 'uz' else f"🏪 <b>Все зарегистрированные магазины ({len(stores)}):</b>\n\n"
        text = title + "\n\n──────────────\n\n".join(format_store_card(s) for s in stores)
        await message.answer(
            text,
            reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.error(f"All stores error: {e}", exc_info=True)
        await message.answer("⚠️ Xatolik yuz berdi.", reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang))


@router.message(F.text.in_(["⬅️ Asosiy menyu", "⬅️ Главное меню", "❌ Bekor qilish", "Bekor qilish", "❌ Отмена"]))
async def cancel_store_search(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)
    text = "Asosiy menyu:" if lang == 'uz' else "Главное меню:"
    await message.answer(text, reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang))


@router.message(StoreSearchStates.waiting_for_query, F.text)
async def process_store_text_search(message: Message, state: FSMContext) -> None:
    query = (message.text or '').strip()
    lang = await get_user_language(message.from_user.id)
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)

    if not query or query in ["⬅️ Asosiy menyu", "⬅️ Главное меню", "❌ Bekor qilish", "❌ Отмена"]:
        await state.clear()
        text = "Asosiy menyu:" if lang == 'uz' else "Главное меню:"
        await message.answer(text, reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang))
        return

    try:
        stores = await search_stores(query)
        if not stores:
            not_found_text = (
                f"❌ <b>«{query}»</b> bo'yicha hech qanday do'kon topilmadi.\n\n"
                f"Boshqa nom bilan qidirib ko'ring yoki «📋 Barcha do'konlar» tugmasini bosing."
                if lang == 'uz' else
                f"❌ По запросу <b>«{query}»</b> ничего не найдено.\n\n"
                f"Попробуйте другое название или нажмите «📋 Все магазины»."
            )
            await message.answer(
                not_found_text,
                reply_markup=store_search_cancel_keyboard(lang),
                parse_mode="HTML",
            )
            return

        title = f"🔍 <b>«{query}» bo'yicha topilgan do'konlar ({len(stores)} ta):</b>\n\n" if lang == 'uz' else f"🔍 <b>Найдено по запросу «{query}» ({len(stores)}):</b>\n\n"
        text = title + "\n\n──────────────\n\n".join(format_store_card(s) for s in stores)
        await message.answer(
            text,
            reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Store search error for query '{query}': {e}", exc_info=True)
        await message.answer(
            "⚠️ " + ("Qidiruvda xatolik yuz berdi." if lang == 'uz' else "Ошибка при поиске."),
            reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
        )
