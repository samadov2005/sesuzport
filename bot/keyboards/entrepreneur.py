from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def entrepreneur_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏪 Mening do'konlarim"), KeyboardButton(text="📊 Do'kon statistikasi")],
            [KeyboardButton(text="📋 Murojaatlar"), KeyboardButton(text="⭐ Reytingim")],
            [KeyboardButton(text="💰 Keshbek"), KeyboardButton(text="💬 Yordam")],
            [KeyboardButton(text="🔄 Rolni almashtirish")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
