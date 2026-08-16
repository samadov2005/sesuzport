from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.i18n import get_btn


def role_keyboard(is_admin: bool = False, is_entrepreneur: bool = False, lang: str = 'uz', show_back: bool = False) -> ReplyKeyboardMarkup:
    row1 = [KeyboardButton(text=get_btn('btn_role_consumer', lang))]
    if is_entrepreneur or is_admin:
        row1.append(KeyboardButton(text=get_btn('btn_role_entrepreneur', lang)))

    buttons = [row1]
    if is_admin:
        buttons.append([KeyboardButton(text=get_btn('btn_role_admin', lang))])

    if show_back:
        back_text = "⬅️ Orqaga" if lang == 'uz' else "⬅️ Назад"
        buttons.append([KeyboardButton(text=back_text)])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False
    )
