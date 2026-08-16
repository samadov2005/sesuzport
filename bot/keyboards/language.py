from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def language_keyboard(show_back: bool = False, lang: str = 'uz') -> ReplyKeyboardMarkup:
    """Keyboard with Uzbek and Russian language options with flags, plus optional back button."""
    buttons = [
        [
            KeyboardButton(text="🇺🇿 O'zbekcha"),
            KeyboardButton(text="🇷🇺 Русский"),
        ]
    ]
    if show_back:
        back_text = "⬅️ Orqaga" if lang == 'uz' else "⬅️ Назад"
        buttons.append([KeyboardButton(text=back_text)])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False,
    )
