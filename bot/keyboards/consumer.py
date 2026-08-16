from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.i18n import get_btn


def consumer_keyboard(is_admin: bool = False, is_entrepreneur: bool = False, lang: str = 'uz') -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text=get_btn('btn_complaint', lang)),
            KeyboardButton(text=get_btn('btn_my_complaints', lang))
        ],
        [
            KeyboardButton(text=get_btn('btn_stores', lang)),
            KeyboardButton(text=get_btn('btn_cashback', lang))
        ],
        [
            KeyboardButton(text=get_btn('btn_rights', lang)),
            KeyboardButton(text=get_btn('btn_support', lang))
        ],
        [
            KeyboardButton(text=get_btn('btn_settings', lang))
        ]
    ]

    extra_row = []
    if is_admin:
        extra_row.append(KeyboardButton(text=get_btn('btn_role_admin', lang)))
    if is_admin or is_entrepreneur:
        extra_row.append(KeyboardButton(text=get_btn('btn_change_role', lang)))

    if extra_row:
        buttons.append(extra_row)

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        is_persistent=True
    )
