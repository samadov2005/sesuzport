from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )


def location_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Haqiqiy GPS joylashuvni yuborish", request_location=True)],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=True
    )


def complaint_detail_keyboard(complaint_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📷 Rasm", callback_data=f"complaint_photo_{complaint_id}"),
                InlineKeyboardButton(text="📍 Joylashuv", callback_data=f"complaint_location_{complaint_id}")
            ]
        ]
    )


def complaints_list_keyboard(complaints: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
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
        nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"complaints_page_{page-1}"))

    if total_pages > 1:
        nav_row.append(InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="ignore"))

    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"complaints_page_{page+1}"))

    if nav_row:
        buttons.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)
