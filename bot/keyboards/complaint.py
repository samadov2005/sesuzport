from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from bot.config import get_bot_config
from bot.utils.i18n import get_btn


def camera_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Keyboard with dedicated WebApp button to open the live device camera only if HTTPS is configured."""
    config = get_bot_config()
    camera_url = f"{config.webapp_url.rstrip('/')}/camera/"
    camera_btn_text = "📸 Kamerani ochish (Jonli)" if lang == 'uz' else "📸 Открыть камеру (Онлайн)"

    if camera_url.startswith('https://'):
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=camera_btn_text, web_app=WebAppInfo(url=camera_url))],
                [KeyboardButton(text=get_btn('btn_cancel', lang))]
            ],
            resize_keyboard=True,
            is_persistent=True,
            one_time_keyboard=True
        )
    else:
        # Fallback for HTTP local testing (Telegram Bot API rejects http:// in WebAppInfo)
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=get_btn('btn_cancel', lang))]
            ],
            resize_keyboard=True,
            is_persistent=True
        )


def cancel_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_btn('btn_cancel', lang))]
        ],
        resize_keyboard=True,
        is_persistent=True
    )


def complaint_reasons_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Fast-select complaint reasons + custom input button + cancel."""
    if lang == 'ru':
        buttons = [
            [KeyboardButton(text="⏳ Просроченный товар"), KeyboardButton(text="🏷 Неверная цена / Чек")],
            [KeyboardButton(text="🧼 Нарушение санитарии"), KeyboardButton(text="🪰 Испорченный / Некачественный")],
            [KeyboardButton(text="✍️ Другая причина (написать)")],
            [KeyboardButton(text=get_btn('btn_cancel', lang))]
        ]
    else:
        buttons = [
            [KeyboardButton(text="⏳ Muddati o'tgan mahsulot"), KeyboardButton(text="🏷 Narx noto'g'ri / Chek bermadi")],
            [KeyboardButton(text="🧼 Sanitariya holati yomon"), KeyboardButton(text="🪰 Sifatsiz / Aynigan mahsulot")],
            [KeyboardButton(text="✍️ Boshqa muammo (yozib kiritish)")],
            [KeyboardButton(text=get_btn('btn_cancel', lang))]
        ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        is_persistent=True
    )


def location_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    send_loc_text = "📍 Haqiqiy GPS joylashuvni yuborish" if lang == 'uz' else "📍 Отправить реальную GPS локацию"
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=send_loc_text, request_location=True)],
            [KeyboardButton(text=get_btn('btn_cancel', lang))]
        ],
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=True
    )


def complaint_detail_keyboard(complaint_id: int, lang: str = 'uz') -> InlineKeyboardMarkup:
    photo_text = "📷 Rasm" if lang == 'uz' else "📷 Фото"
    loc_text = "📍 Joylashuv" if lang == 'uz' else "📍 Локация"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=photo_text, callback_data=f"complaint_photo_{complaint_id}"),
                InlineKeyboardButton(text=loc_text, callback_data=f"complaint_location_{complaint_id}")
            ]
        ]
    )


def complaints_list_keyboard(complaints: list, page: int, total_pages: int, lang: str = 'uz') -> InlineKeyboardMarkup:
    buttons = []
    
    # Add a row for each complaint in this page
    for c in complaints:
        buttons.append([
            InlineKeyboardButton(
                text=f"🎫 {c.ticket_id} ({c.get_status_display()})",
                callback_data=f"complaint_detail_{c.id}"
            )
        ])

    # Navigation buttons
    nav_row = []
    if page > 1:
        prev_text = "⬅️ Oldingi" if lang == 'uz' else "⬅️ Назад"
        nav_row.append(InlineKeyboardButton(text=prev_text, callback_data=f"complaints_page_{page-1}"))

    if total_pages > 1:
        nav_row.append(InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="ignore"))

    if page < total_pages:
        next_text = "Keyingi ➡️" if lang == 'uz' else "Вперед ➡️"
        nav_row.append(InlineKeyboardButton(text=next_text, callback_data=f"complaints_page_{page+1}"))

    if nav_row:
        buttons.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)
