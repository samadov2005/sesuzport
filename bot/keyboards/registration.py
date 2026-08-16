from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from bot.utils.i18n import get_btn


def share_contact_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Keyboard with a native contact-share button."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_btn('btn_share_contact', lang), request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def skip_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Keyboard with skip and optional manual entry."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_btn('btn_skip', lang))],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
