from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def back_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
        resize_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def rights_list_keyboard(rights_list: list) -> InlineKeyboardMarkup:
    buttons = []
    for right in rights_list:
        category = f"[{right.category}] " if right.category else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"⚖️ {category}{right.title[:40]}",
                callback_data=f"right_{right.id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def store_location_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for store search — location button, name search, and all stores."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Joylashuvimni yuborish", request_location=True)],
            [KeyboardButton(text="🔍 Nomi bo'yicha qidirish"), KeyboardButton(text="📋 Barcha do'konlar")],
            [KeyboardButton(text="⬅️ Asosiy menyu")],
        ],
        resize_keyboard=True,
    )


def store_search_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Joylashuvimni yuborish", request_location=True)],
            [KeyboardButton(text="📋 Barcha do'konlar")],
            [KeyboardButton(text="⬅️ Asosiy menyu")],
        ],
        resize_keyboard=True,
    )

