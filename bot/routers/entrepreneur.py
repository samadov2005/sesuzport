import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.entrepreneur import entrepreneur_keyboard
from bot.services.user_service import update_user_role, is_entrepreneur_user, get_user_language
from bot.services.admin_service import is_admin_user
from bot.utils.i18n import get_text

logger = logging.getLogger(__name__)
router = Router(name='entrepreneur_router')


@router.message(F.text.in_(["💼 Tadbirkor", "💼 Предприниматель"]))
async def role_entrepreneur(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)
    if not is_ent:
        await message.answer(
            get_text('entrepreneur_restricted', lang),
            parse_mode="HTML",
        )
        return

    await update_user_role(message.from_user.id, 'ENTREPRENEUR')
    is_admin = await is_admin_user(message.from_user.id)
    await message.answer(
        get_text('entrepreneur_menu_header', lang),
        reply_markup=entrepreneur_keyboard(is_admin=is_admin, lang=lang),
        parse_mode="HTML",
    )


@router.message(F.text.in_(["🏪 Mening do'konlarim", "🏪 Мои магазины"]))
async def my_stores(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    if lang == 'ru':
        text = (
            "🏪 <b>Мои магазины</b>\n\n"
            "В этом разделе вы можете просматривать зарегистрированные магазины.\n\n"
            "📋 Магазинов пока нет.\n\n"
            "Для добавления или редактирования обратитесь к администратору:\n"
            "📱 Admin: @sesport_admin"
        )
    else:
        text = (
            "🏪 <b>Mening do'konlarim</b>\n\n"
            "Bu bo'limda siz ro'yxatdan o'tgan do'konlaringizni ko'rishingiz mumkin.\n\n"
            "📋 Hozircha ro'yxatdan o'tgan do'konlar yo'q.\n\n"
            "Do'kon qo'shish yoki tahrirlash uchun administrator bilan bog'laning:\n"
            "📱 Admin: @sesport_admin"
        )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text.in_(["📊 Do'kon statistikasi", "📊 Статистика магазина"]))
async def store_statistics(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    if lang == 'ru':
        text = (
            "📊 <b>Статистика магазина</b>\n\n"
            "Здесь отображаются обращения и статистика рейтинга вашего магазина.\n\n"
            "📈 Всего обращений: <b>0</b>\n"
            "✅ Решено: <b>0</b>\n"
            "⭐ Средний рейтинг: <b>—</b>\n\n"
            "Статистика появится после регистрации магазина."
        )
    else:
        text = (
            "📊 <b>Do'kon statistikasi</b>\n\n"
            "Bu bo'limda do'koningizga kelib tushgan murojaatlar va reyting statistikasi ko'rinadi.\n\n"
            "📈 Jami murojaatlar: <b>0</b>\n"
            "✅ Hal qilingan: <b>0</b>\n"
            "⭐ O'rtacha reyting: <b>—</b>\n\n"
            "Do'kon ro'yxatdan o'tgandan so'ng statistika ko'rinadi."
        )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text.in_(["📋 Murojaatlar", "📋 Обращения"]))
async def entrepreneur_complaints(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    if lang == 'ru':
        text = (
            "📋 <b>Обращения в ваш магазин</b>\n\n"
            "Пока обращений нет.\n\n"
            "Вы будете уведомлены при поступлении новых обращений."
        )
    else:
        text = (
            "📋 <b>Do'koningizga kelgan murojaatlar</b>\n\n"
            "Hozircha do'koningizga murojaatlar yo'q.\n\n"
            "Yangi murojaatlar kelganida siz xabardor qilinasiz."
        )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text.in_(["⭐ Reytingim", "⭐ Мой рейтинг"]))
async def entrepreneur_rating(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    if lang == 'ru':
        text = (
            "⭐ <b>Рейтинг магазина</b>\n\n"
            "Статус безопасности и рейтинг вашего магазина:\n\n"
            "🛡 Статус безопасности: <b>Не определен</b>\n"
            "⭐ Рейтинг: <b>—/5.0</b>\n"
            "📊 Количество оценок: <b>0</b>\n\n"
            "Рейтинг формируется на основе обращений потребителей и результатов модерации."
        )
    else:
        text = (
            "⭐ <b>Do'kon reytingi</b>\n\n"
            "Do'koningizning xavfsizlik holati va reytingi:\n\n"
            "🛡 Xavfsizlik holati: <b>Aniqlanmagan</b>\n"
            "⭐ Reyting: <b>—/5.0</b>\n"
            "📊 Baholashlar soni: <b>0</b>\n\n"
            "Reyting iste'molchilarning murojaatlari va moderatsiya natijalari asosida shakllanadi."
        )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text.in_(["💰 Keshbek", "💰 Кэшбэк"]))
async def entrepreneur_cashback(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    if lang == 'ru':
        text = (
            "💰 <b>Программа кэшбэка для предпринимателей</b>\n\n"
            "Условия программы кэшбэка:\n"
            "• Повышайте уровень безопасности магазина\n"
            "• Оперативно решайте обращения\n"
            "• Получайте бонусные преимущества\n\n"
            "💳 Баланс кэшбэка: <b>0 сум</b>\n\n"
            "Для подробной информации обратитесь к администратору."
        )
    else:
        text = (
            "💰 <b>Tadbirkor keshbek dasturi</b>\n\n"
            "Tadbirkorlar uchun keshbek dasturi:\n"
            "• Do'koningiz xavfsizlik holatini yaxshilang\n"
            "• Murojaatlarni tezda hal qiling\n"
            "• Bonus imtiyozlar oling\n\n"
            "💳 Keshbek balansi: <b>0 so'm</b>\n\n"
            "Batafsil ma'lumot uchun administrator bilan bog'laning."
        )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text.in_(["💬 Yordam", "💬 Помощь"]))
async def entrepreneur_support(message: Message) -> None:
    # Redirect to support router — handled there
    pass
