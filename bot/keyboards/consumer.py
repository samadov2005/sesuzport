from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def consumer_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Shikoyat qilish"), KeyboardButton(text="📁 Mening murojaatlarim")],
            [KeyboardButton(text="🏪 Do'konlarni tekshirish"), KeyboardButton(text="💳 Keshbeklarni kuzatish")],
            [KeyboardButton(text="⚖️ Huquqlarim"), KeyboardButton(text="💬 Yordam")],
            [KeyboardButton(text="🔄 Rolni almashtirish")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
