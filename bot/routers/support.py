from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from apps.support.models import SupportConfiguration
from bot.services.user_service import get_user_language

router = Router(name='support_router')

@router.message(F.text.in_(["💬 Yordam", "💬 Помощь", "/help", "/support"]))
async def show_support(message: Message):
    lang = await get_user_language(message.from_user.id)
    
    @sync_to_async
    def get_support():
        return SupportConfiguration.objects.filter(is_active=True).first()
        
    support = await get_support()
    
    phone = support.phone if support and support.phone else "+998712000000"
    email = support.email if support and support.email else "info@sesport.uz"
    tg_admin = support.telegram_username if support and support.telegram_username else "sesport_admin"
    hours = support.working_hours if support and support.working_hours else "09:00 - 18:00 (Du-Jum)"

    if lang == 'ru':
        text = (
            f"💬 <b>Служба поддержки и Консультационный центр SESPORT</b>\n\n"
            f"📞 <b>Горячая линия:</b> {phone} (короткий номер 1080)\n"
            f"👤 <b>Администрация:</b> @{tg_admin}\n"
            f"👨‍💻 <b>Разработчик:</b> @samadov2005\n"
            f"✉️ <b>Email:</b> {email}\n"
            f"⏰ <b>Время работы:</b> {hours}\n\n"
            f"<i>Выберите вопрос ниже для быстрого ответа или напишите нам напрямую:</i>"
        )
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="👤 Написать администратору", url=f"https://t.me/{tg_admin}")],
                [InlineKeyboardButton(text="❓ Как подать жалобу?", callback_data="faq_complaint")],
                [InlineKeyboardButton(text="💰 Как работает кешбэк?", callback_data="faq_cashback")],
                [InlineKeyboardButton(text="🏪 Рейтинг безопасности магазинов", callback_data="faq_stores")],
            ]
        )
    else:
        text = (
            f"💬 <b>SESPORT — Mijozlarni qo'llab-quvvatlash va Ishonch markazi</b>\n\n"
            f"📞 <b>Ishonch telefoni:</b> {phone} (qisqa raqam 1080)\n"
            f"👤 <b>Bosh administrator:</b> @{tg_admin}\n"
            f"👨‍💻 <b>Loyiha dasturchisi:</b> @samadov2005\n"
            f"✉️ <b>Rasmiy email:</b> {email}\n"
            f"⏰ <b>Ish vaqti:</b> {hours}\n\n"
            f"<i>Tezkor ma'lumot olish uchun quyidagi savollardan birini tanlang yoki to'g'ridan-to'g'ri yozing:</i>"
        )
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="👤 Bosh administratorga yozish", url=f"https://t.me/{tg_admin}")],
                [InlineKeyboardButton(text="❓ Shikoyat qanday yuboriladi?", callback_data="faq_complaint")],
                [InlineKeyboardButton(text="💰 Keshbek tizimi qanday ishlaydi?", callback_data="faq_cashback")],
                [InlineKeyboardButton(text="🏪 Do'konlar xavfsizlik reytingi nima?", callback_data="faq_stores")],
            ]
        )

    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "faq_complaint")
async def faq_complaint_handler(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    if lang == 'ru':
        text = (
            "❓ <b>Как подать жалобу и как она рассматривается?</b>\n\n"
            "1. Нажмите кнопку <b>«📝 Подать жалобу»</b> в главном меню.\n"
            "2. Выберите причину (просрочка, санитария, чек) или напишите свою.\n"
            "3. Сделайте фото через <b>онлайн-камеру</b> прямо на месте.\n"
            "4. Отправьте <b>GPS-локацию</b> магазина.\n\n"
            "🛡 После отправки обращение попадает на проверку инспекторам SES. "
            "Статус обращения можно отслеживать в разделе <b>«📁 Мои обращения»</b>."
        )
    else:
        text = (
            "❓ <b>Shikoyat qanday yuboriladi va ko'rib chiqiladi?</b>\n\n"
            "1. Asosiy menyuda <b>«📝 Shikoyat qilish»</b> tugmasini bosing.\n"
            "2. Muammoni tanlang (muddati o'tgan, sanitariya, narx/chek) yoki yozing.\n"
            "3. Voqea joyida <b>jonli kamera</b> orqali rasmga oling.\n"
            "4. Do'konning <b>haqiqiy GPS joylashuvini</b> yuboring.\n\n"
            "🛡 Yuborilgan murojaat darhol SES inspektorlari nazoratiga o'tadi va tekshiriladi. "
            "Holatni <b>«📁 Mening murojaatlarim»</b> bo'limida onlayn kuzatib borasiz."
        )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "faq_cashback")
async def faq_cashback_handler(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    if lang == 'ru':
        text = (
            "💰 <b>Как работает кешбэк и бонусы?</b>\n\n"
            "• Граждане, отправляющие подтвержденные жалобы на нарушения качества и санитарии, "
            "получают поощрительные баллы и кешбэк.\n"
            "• Баланс и историю начислений можно проверить в разделе <b>«💰 Кешбэк»</b>."
        )
    else:
        text = (
            "💰 <b>Keshbek va bonuslar tizimi qanday ishlaydi?</b>\n\n"
            "• Sifatsiz yoki muddati o'tgan mahsulotlar bo'yicha asosli shikoyat yuborgan va "
            "murojaati tasdiqlangan faol fuqarolarga rag'batlantiruvchi keshbek ballari beriladi.\n"
            "• Jamg'arilgan ballarni <b>«💰 Keshbek»</b> bo'limida ko'rishingiz mumkin."
        )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "faq_stores")
async def faq_stores_handler(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    if lang == 'ru':
        text = (
            "🏪 <b>Что означает рейтинг безопасности магазинов?</b>\n\n"
            "🟢 <b>Зеленый (Xavfsiz):</b> Проверенный магазин, соблюдающий все санитарные нормы.\n"
            "🟡 <b>Желтый (Diqqat):</b> Были незначительные замечания, находится на контроле.\n"
            "🔴 <b>Красный (Xavfli):</b> Выявлены серьезные нарушения качества или санитарии.\n\n"
            "📍 Ближайшие безопасные магазины можно найти в разделе <b>«🏪 Магазины»</b>."
        )
    else:
        text = (
            "🏪 <b>Do'konlar xavfsizlik reytingi nima?</b>\n\n"
            "🟢 <b>Yashil (Xavfsiz):</b> Sanitariya va sifat talablariga to'liq javob beruvchi ishonchli do'kon.\n"
            "🟡 <b>Sariq (Diqqat):</b> Kichik kamchiliklar qayd etilgan, nazoratdagi savdo shoxobchasi.\n"
            "🔴 <b>Qizil (Xavfli):</b> Muddati o'tgan mahsulotlar yoki jiddiy qoidabuzarliklar aniqlangan do'kon.\n\n"
            "📍 Yaqin atrofdagi xavfsiz do'konlarni <b>«🏪 Do'konlar»</b> bo'limida xaritada ko'rishingiz mumkin."
        )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

