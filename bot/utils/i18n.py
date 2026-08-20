"""
Internationalization (i18n) module for SESPORT Telegram Bot.
Supports Uzbek (uz) and Russian (ru).
"""
from typing import Dict, Any

MESSAGES: Dict[str, Dict[str, str]] = {
    # ── Language selection ──────────────────────────────────────────────────
    'choose_language': {
        'uz': "🇺🇿 <b>Tilni tanlang / Выберите язык:</b>",
        'ru': "🇷🇺 <b>Выберите язык / Tilni tanlang:</b>",
    },
    'language_changed': {
        'uz': "✅ Til muvaffaqiyatli <b>O'zbekcha</b>ga o'zgartirildi.",
        'ru': "✅ Язык успешно изменен на <b>Русский</b>.",
    },

    # ── Onboarding / Registration ───────────────────────────────────────────
    'welcome_onboarding': {
        'uz': (
            "👋 <b>SESPORT botiga xush kelibsiz!</b>\n\n"
            "Sizni ro'yxatdan o'tkazib olaylik — bu bir necha soniya oladi.\n\n"
            "1️⃣ <b>Ism va familyangizni</b> kiriting:\n"
            "<i>(masalan: Aziz Karimov)</i>"
        ),
        'ru': (
            "👋 <b>Добро пожаловать в бот SESPORT!</b>\n\n"
            "Давайте пройдем быструю регистрацию — это займет всего пару секунд.\n\n"
            "1️⃣ Введите ваше <b>Имя и Фамилию</b>:\n"
            "<i>(например: Азиз Каримов)</i>"
        ),
    },
    'invalid_name': {
        'uz': "⚠️ Iltimos, <b>haqiqiy ism va familyangizni</b> kiriting (2–100 belgi).",
        'ru': "⚠️ Пожалуйста, введите <b>реальное имя и фамилию</b> (от 2 до 100 символов).",
    },
    'ask_phone': {
        'uz': (
            "✅ <b>{name}</b> — qabul qilindi!\n\n"
            "2️⃣ <b>Telefon raqamingizni</b> ulashing:\n"
            "Pastdagi tugmani bosing yoki raqamni qo'lda kiriting (+998XXXXXXXXX)."
        ),
        'ru': (
            "✅ <b>{name}</b> — принято!\n\n"
            "2️⃣ Поделитесь своим <b>номером телефона</b>:\n"
            "Нажмите кнопку ниже или введите номер вручную (+998XXXXXXXXX)."
        ),
    },
    'invalid_phone': {
        'uz': "⚠️ Noto'g'ri format. Iltimos, telefon raqamingizni kiriting yoki quyidagi tugmani bosing:",
        'ru': "⚠️ Неверный формат. Пожалуйста, введите номер телефона или нажмите кнопку ниже:",
    },
    'ask_phone2': {
        'uz': (
            "3️⃣ <b>Qo'shimcha telefon raqam</b> (ixtiyoriy):\n\n"
            "Agar ikkinchi raqamingiz bo'lsa kiriting, aks holda «⏭ O'tkazib yuborish» tugmasini bosing."
        ),
        'ru': (
            "3️⃣ <b>Дополнительный номер телефона</b> (необязательно):\n\n"
            "Если у вас есть второй номер, введите его, либо нажмите кнопку «⏭ Пропустить»."
        ),
    },
    'complaint_start': {
        'uz': (
            "📝 <b>Yangi shikoyat yuborish</b>\n\n"
            "Mahsulot yoki do'konda qanday muammoga duch keldingiz?\n\n"
            "👇 <b>Quyidagi tayyor sabablardan birini tanlang yoki ovozli xabar (yoki matn) yuboring:</b>"
        ),
        'ru': (
            "📝 <b>Новая жалоба</b>\n\n"
            "С какой проблемой вы столкнулись?\n\n"
            "👇 <b>Выберите готовую причину ниже или отправьте голосовое/текстовое сообщение:</b>"
        ),
    },
    'complaint_custom_text_prompt': {
        'uz': (
            "✍️ <b>Muammo tavsifini yozing yoki ovozli xabar yuboring:</b>\n\n"
            "Do'kon va aniqlangan qoidabuzarlik haqida ma'lumot qoldiring."
        ),
        'ru': (
            "✍️ <b>Опишите проблему или отправьте голосовое сообщение:</b>\n\n"
            "Укажите название магазина и суть нарушения."
        ),
    },
    'complaint_photo_prompt': {
        'uz': (
            "📸 <b>Mahsulotning holati va yaroqlilik muddatini rasmga oling:</b>\n\n"
            "🛡️ <i>Xavfsizlik talabi: Soxtalashtirish va eski rasmlarni yuklashning oldini olish uchun rasm faqat <b>jonli kamera</b> orqali qabul qilinadi. Telefon xotirasi (galereya)dan yuklash taqiqlangan.</i>\n\n"
            "👇 Pastdagi <b>«📸 Kamerani ochish (Jonli)»</b> tugmasini bosing:"
        ),
        'ru': (
            "📸 <b>Сделайте снимок товара и срока годности на месте:</b>\n\n"
            "🛡️ <i>Требование безопасности: Во избежание фальсификаций фото принимается только через <b>онлайн камеру</b>. Загрузка из галереи отключена.</i>\n\n"
            "👇 Нажмите кнопку <b>«📸 Открыть камеру (Онлайн)»</b> ниже:"
        ),
    },
    'complaint_location_prompt': {
        'uz': (
            "📍 <b>Do'konning GPS joylashuvini yuboring:</b>\n\n"
            "🛡️ <i>Soxta shikoyatlarning oldini olish uchun faqat do'konda turgan joyingizdan GPS yuborilishi shart.</i>\n\n"
            "👇 Pastdagi <b>«📍 Haqiqiy GPS joylashuvni yuborish»</b> tugmasini bosing:"
        ),
        'ru': (
            "📍 <b>Отправьте GPS локацию магазина:</b>\n\n"
            "🛡️ <i>Во избежание ложных жалоб, локация должна отправляться прямо из магазина.</i>\n\n"
            "👇 Нажмите кнопку <b>«📍 Отправить реальную GPS локацию»</b> внизу:"
        ),
    },
    'reg_success': {
        'uz': (
            "🎉 <b>Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!</b>\n\n"
            "👤 Ism: <b>{name}</b>\n"
            "📱 Asosiy raqam: <b>{phone}</b>{phone2_line}\n\n"
            "Iste'molchi xizmatlaridan foydalanishingiz mumkin:"
        ),
        'ru': (
            "🎉 <b>Регистрация успешно завершена!</b>\n\n"
            "👤 Имя: <b>{name}</b>\n"
            "📱 Основной номер: <b>{phone}</b>{phone2_line}\n\n"
            "Теперь вам доступны все функции потребителя:"
        ),
    },
    'reg_success_multi': {
        'uz': (
            "🎉 <b>Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!</b>\n\n"
            "👤 Ism: <b>{name}</b>\n"
            "📱 Asosiy raqam: <b>{phone}</b>{phone2_line}\n\n"
            "Endi platformadan to'liq foydalanishingiz mumkin. Rolingizni tanlang:"
        ),
        'ru': (
            "🎉 <b>Регистрация успешно завершена!</b>\n\n"
            "👤 Имя: <b>{name}</b>\n"
            "📱 Основной номер: <b>{phone}</b>{phone2_line}\n\n"
            "Теперь вы можете полноценно пользоваться платформой. Выберите вашу роль:"
        ),
    },

    # ── Main Menus ──────────────────────────────────────────────────────────
    'welcome_back': {
        'uz': "🛡️ <b>SESPORT</b> — Xush kelibsiz!\n\nIste'molchi boshqaruv menyusi:",
        'ru': "🛡️ <b>SESPORT</b> — Добро пожаловать!\n\nГлавное меню потребителя:",
    },
    'select_role': {
        'uz': "🛡️ <b>SESPORT</b> — Xush kelibsiz!\n\nRolingizni tanlang:",
        'ru': "🛡️ <b>SESPORT</b> — Добро пожаловать!\n\nВыберите вашу роль:",
    },
    'consumer_menu_header': {
        'uz': "Iste'molchi menyusi. Atrofingizdagi do'konlarni tekshiring, buzilishlar haqida murojaat yuboring va keshbeklaringizni kuzating.",
        'ru': "Меню потребителя. Проверяйте магазины поблизости, отправляйте жалобы о нарушениях и отслеживайте свой кэшбэк.",
    },
    'entrepreneur_menu_header': {
        'uz': (
            "💼 <b>Tadbirkor menyusi</b>\n\n"
            "Do'konlaringizni boshqaring va statistikani kuzatib boring.\n"
            "Murojaatlarni ko'ring va reytingingizni oshiring."
        ),
        'ru': (
            "💼 <b>Панель предпринимателя</b>\n\n"
            "Управляйте своими магазинами и следите за статистикой.\n"
            "Просматривайте обращения и повышайте свой рейтинг."
        ),
    },
    'entrepreneur_restricted': {
        'uz': (
            "⛔ <b>Kirish cheklangan:</b>\n\n"
            "Tadbirkor bo'limi faqat tizim administratori tomonidan tasdiqlangan tadbirkorlar uchun mo'ljallangan.\n\n"
            "Agar siz tadbirkor bo'lsangiz va do'konlaringizni tizimga ulamoqchi bo'lsangiz, "
            "iltimos, administrator bilan bog'laning: @sesport_admin"
        ),
        'ru': (
            "⛔ <b>Доступ ограничен:</b>\n\n"
            "Раздел предпринимателя доступен только для подтвержденных администратором пользователей.\n\n"
            "Если вы являетесь предпринимателем и хотите подключить свои магазины, "
            "пожалуйста, свяжитесь с администратором: @sesport_admin"
        ),
    },
    'main_menu': {
        'uz': "Asosiy menyu:",
        'ru': "Главное меню:",
    },
    'action_cancelled': {
        'uz': "❌ Amal bekor qilindi.",
        'ru': "❌ Действие отменено.",
    },
    'no_active_action': {
        'uz': "❌ Bekor qilinadigan faol amal yo'q.",
        'ru': "❌ Нет активных действий для отмены.",
    },

    # ── Settings ────────────────────────────────────────────────────────────
    'settings_header': {
        'uz': (
            "⚙️ <b>Sozlamalar</b>\n\n"
            "Til: <b>🇺🇿 O'zbekcha</b>\n\n"
            "Quyidagi tugma orqali tilni o'zgartirishingiz mumkin:"
        ),
        'ru': (
            "⚙️ <b>Настройки</b>\n\n"
            "Язык: <b>🇷🇺 Русский</b>\n\n"
            "Вы можете изменить язык с помощью кнопки ниже:"
        ),
    },
    'select_new_language': {
        'uz': "Tilni tanlang / Выберите язык:",
        'ru': "Выберите язык / Tilni tanlang:",
    },

    # ── Help ────────────────────────────────────────────────────────────────
    'help_text': {
        'uz': (
            "🛡️ <b>SESPORT — Iste'molchilarni himoya qilish platformasi</b>\n\n"
            "📋 <b>Buyruqlar:</b>\n"
            "/start — Botni qayta boshlash\n"
            "/cancel — Joriy amalni bekor qilish\n"
            "/help — Yordam\n\n"
            "📌 <b>Asosiy funksiyalar:</b>\n"
            "📝 Shikoyat qilish — Muddati o'tgan yoki buzilgan mahsulot haqida murojaat\n"
            "📁 Mening murojaatlarim — Barcha murojaatlaringiz holatini ko'rish\n"
            "🏪 Do'konlarni tekshirish — Yaqin atrofdagi do'konlar va reyting\n"
            "💳 Keshbeklarni kuzatish — Keshbek balansi va tarixi\n"
            "⚖️ Huquqlarim — Iste'molchi huquqlari qonunchiligi\n"
            "⚙️ Sozlamalar — Tilni o'zgartirish va sozlash\n"
            "💬 Yordam — Aloqa ma'lumotlari"
        ),
        'ru': (
            "🛡️ <b>SESPORT — Платформа защиты прав потребителей</b>\n\n"
            "📋 <b>Команды:</b>\n"
            "/start — Перезапуск бота\n"
            "/cancel — Отмена текущего действия\n"
            "/help — Помощь\n\n"
            "📌 <b>Основные функции:</b>\n"
            "📝 Подать жалобу — Обращение о просроченной или испорченной продукции\n"
            "📁 Мои обращения — Просмотр статуса ваших жалоб\n"
            "🏪 Проверка магазинов — Ближайшие магазины и их рейтинг безопасности\n"
            "💳 Мой кэшбэк — Баланс и история кэшбэка\n"
            "⚖️ Мои права — Законодательство о правах потребителей\n"
            "⚙️ Настройки — Изменение языка и параметров\n"
            "💬 Помощь — Контакты поддержки"
        ),
    },
}

BUTTONS: Dict[str, Dict[str, str]] = {
    # Language
    'lang_uz': {'uz': "🇺🇿 O'zbekcha", 'ru': "🇺🇿 O'zbekcha"},
    'lang_ru': {'uz': "🇷🇺 Русский", 'ru': "🇷🇺 Русский"},

    # Consumer Menu
    'btn_complaint': {'uz': "📝 Shikoyat qilish", 'ru': "📝 Подать жалобу"},
    'btn_my_complaints': {'uz': "📁 Mening murojaatlarim", 'ru': "📁 Мои обращения"},
    'btn_stores': {'uz': "🏪 Do'konlarni tekshirish", 'ru': "🏪 Проверка магазинов"},
    'btn_cashback': {'uz': "💳 Keshbeklarni kuzatish", 'ru': "💳 Мой кэшбэк"},
    'btn_rights': {'uz': "⚖️ Huquqlarim", 'ru': "⚖️ Мои права"},
    'btn_support': {'uz': "💬 Yordam", 'ru': "💬 Помощь"},
    'btn_settings': {'uz': "⚙️ Sozlamalar", 'ru': "⚙️ Настройки"},
    'btn_change_role': {'uz': "🔄 Rolni almashtirish", 'ru': "🔄 Сменить роль"},

    # Roles
    'btn_role_consumer': {'uz': "👤 Iste'molchi (Mijoz)", 'ru': "👤 Потребитель (Клиент)"},
    'btn_role_entrepreneur': {'uz': "💼 Tadbirkor", 'ru': "💼 Предприниматель"},
    'btn_role_admin': {'uz': "🛡️ Admin panel", 'ru': "🛡️ Админ панель"},

    # Entrepreneur Menu
    'btn_my_stores': {'uz': "🏪 Mening do'konlarim", 'ru': "🏪 Мои магазины"},
    'btn_store_stats': {'uz': "📊 Do'kon statistikasi", 'ru': "📊 Статистика магазина"},
    'btn_ent_complaints': {'uz': "📋 Murojaatlar", 'ru': "📋 Обращения"},
    'btn_ent_rating': {'uz': "⭐ Reytingim", 'ru': "⭐ Мой рейтинг"},
    'btn_ent_cashback': {'uz': "💰 Keshbek", 'ru': "💰 Кэшбэк"},

    # Settings
    'btn_change_lang': {'uz': "🌐 Tilni o'zgartirish", 'ru': "🌐 Изменить язык"},
    'btn_back_to_menu': {'uz': "🔙 Asosiy menyu", 'ru': "🔙 Главное меню"},

    # Common
    'btn_share_contact': {'uz': "📱 Telefon raqamni ulashish", 'ru': "📱 Поделиться контактом"},
    'btn_skip': {'uz': "⏭ O'tkazib yuborish", 'ru': "⏭ Пропустить"},
    'btn_cancel': {'uz': "❌ Bekor qilish", 'ru': "❌ Отмена"},
}


def get_text(key: str, lang: str = 'uz', **kwargs: Any) -> str:
    """Get localized text by key and language, formatting with kwargs."""
    lang = lang if lang in ('uz', 'ru') else 'uz'
    text_dict = MESSAGES.get(key, {})
    template = text_dict.get(lang, text_dict.get('uz', key))
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


def get_btn(key: str, lang: str = 'uz') -> str:
    """Get localized button label."""
    lang = lang if lang in ('uz', 'ru') else 'uz'
    btn_dict = BUTTONS.get(key, {})
    return btn_dict.get(lang, btn_dict.get('uz', key))
