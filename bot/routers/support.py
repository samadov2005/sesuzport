from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from apps.support.models import SupportConfiguration
from bot.services.user_service import get_user_language

router = Router(name='support_router')

@router.message(F.text.in_(["💬 Yordam", "💬 Помощь", "/help", "/support"]))
async def show_support(message: Message):
    lang = await get_user_language(message.from_user.id)
    
    @sync_to_async
    def get_support():
        return SupportConfiguration.objects.filter(is_active=True).first()
        
    support = await get_support()
    
    phone = support.phone if support and support.phone else "+998712000000"
    email = support.email if support and support.email else "info@sesport.uz"
    tg_user = support.telegram_username if support and support.telegram_username else "sesport_admin"
    hours = support.working_hours if support and support.working_hours else "09:00 - 18:00 (Du-Jum)"
    
    clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')

    if lang == 'ru':
        text = (
            f"💬 <b>Служба поддержки и Горячая линия</b>\n\n"
            f"📞 <b>Горячая линия:</b> {phone}\n"
            f"💬 <b>Telegram:</b> @{tg_user}\n"
            f"✉️ <b>Email:</b> {email}\n"
            f"⏰ <b>Время работы:</b> {hours}\n\n"
            f"<i>Если у вас возникли сложности при отправке жалобы или вопросы по качеству товаров, вы можете позвонить нам напрямую!</i>"
        )
        call_btn_text = "📞 Позвонить на горячую линию"
        tg_btn_text = "💬 Написать в Telegram"
    else:
        text = (
            f"💬 <b>Mijozlarni qo'llab-quvvatlash va Ishonch telefoni</b>\n\n"
            f"📞 <b>Ishonch telefoni:</b> {phone}\n"
            f"💬 <b>Telegram:</b> @{tg_user}\n"
            f"✉️ <b>Email:</b> {email}\n"
            f"⏰ <b>Ish vaqti:</b> {hours}\n\n"
            f"<i>Agar botdan foydalanishda qiyinchilik bo'lsa yoki tezkor yordam kerak bo'lsa, to'g'ridan-to'g'ri qo'ng'iroq qilishingiz mumkin!</i>"
        )
        call_btn_text = "📞 Ishonch telefoniga qo'ng'iroq"
        tg_btn_text = "💬 Telegramda yozish"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=tg_btn_text, url=f"https://t.me/{tg_user}")],
        ]
    )

    await message.answer(text, reply_markup=kb, parse_mode="HTML")
