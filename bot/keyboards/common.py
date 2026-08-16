from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from bot.utils.i18n import get_btn


def back_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    back_text = "⬅️ Orqaga" if lang == 'uz' else "⬅️ Назад"
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=back_text)]],
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


def store_location_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Keyboard for store search — location button, name search, and all stores."""
    if lang == 'ru':
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📍 Отправить мое местоположение", request_location=True)],
                [KeyboardButton(text="🔍 Поиск по названию"), KeyboardButton(text="📋 Все магазины")],
                [KeyboardButton(text="⬅️ Главное меню")],
            ],
            resize_keyboard=True,
        )
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Joylashuvimni yuborish", request_location=True)],
            [KeyboardButton(text="🔍 Nomi bo'yicha qidirish"), KeyboardButton(text="📋 Barcha do'konlar")],
            [KeyboardButton(text="⬅️ Asosiy menyu")],
        ],
        resize_keyboard=True,
    )


def store_search_cancel_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    if lang == 'ru':
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📍 Отправить мое местоположение", request_location=True)],
                [KeyboardButton(text="📋 Все магазины")],
                [KeyboardButton(text="⬅️ Главное меню")],
            ],
            resize_keyboard=True,
        )
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Joylashuvimni yuborish", request_location=True)],
            [KeyboardButton(text="📋 Barcha do'konlar")],
            [KeyboardButton(text="⬅️ Asosiy menyu")],
        ],
        resize_keyboard=True,
    )
