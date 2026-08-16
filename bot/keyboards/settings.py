from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.i18n import get_btn


def settings_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Settings keyboard with language change and back to main menu."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_btn('btn_change_lang', lang))],
            [KeyboardButton(text=get_btn('btn_back_to_menu', lang))],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
