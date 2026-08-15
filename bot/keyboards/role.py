from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def role_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="👤 Iste'molchi (Mijoz)"),
            KeyboardButton(text="💼 Tadbirkor")
        ]
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="🛡️ Admin panel")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )
