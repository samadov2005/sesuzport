from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.i18n import get_btn


def entrepreneur_keyboard(is_admin: bool = False, lang: str = 'uz') -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text=get_btn('btn_my_stores', lang)),
            KeyboardButton(text=get_btn('btn_store_stats', lang))
        ],
        [
            KeyboardButton(text=get_btn('btn_ent_complaints', lang)),
            KeyboardButton(text=get_btn('btn_ent_rating', lang))
        ],
        [
            KeyboardButton(text=get_btn('btn_ent_cashback', lang)),
            KeyboardButton(text=get_btn('btn_support', lang))
        ],
        [
            KeyboardButton(text=get_btn('btn_settings', lang))
        ]
    ]

    extra_row = []
    if is_admin:
        extra_row.append(KeyboardButton(text=get_btn('btn_role_admin', lang)))
    extra_row.append(KeyboardButton(text=get_btn('btn_change_role', lang)))

    buttons.append(extra_row)

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        is_persistent=True
    )
