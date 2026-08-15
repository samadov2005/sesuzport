import logging
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

_bot_instance: Bot | None = None


def set_bot_instance(bot: Bot) -> None:
    global _bot_instance
    _bot_instance = bot


async def notify_complaint_status_changed(
    telegram_id: int,
    ticket_id: str,
    new_status: str,
    moderation_comment: str | None = None,
) -> bool:
    if not _bot_instance:
        logger.error("Bot instance not set in notification_service")
        return False

    status_titles = {
        'PENDING': "⏳ Kutilmoqda",
        'UNDER_REVIEW': "🔍 Ko'rib chiqilmoqda",
        'APPROVED': "✅ Tasdiqlandi",
        'REJECTED': "❌ Rad etildi",
        'RESOLVED': "🎯 Murojaat bo'yicha masala hal qilindi",
    }
    status_title = status_titles.get(new_status, "Holat o'zgardi")

    text = (
        f"📢 <b>Murojaat holati yangilandi!</b>\n\n"
        f"🎫 <b>Chipta ID:</b> <code>{ticket_id}</code>\n"
        f"📊 <b>Yangi holat:</b> {status_title}\n"
    )
    if moderation_comment:
        text += f"\n💬 <b>Moderator izohi:</b>\n<i>{moderation_comment}</i>"

    try:
        await _bot_instance.send_message(chat_id=telegram_id, text=text, parse_mode="HTML")
        return True
    except TelegramAPIError as e:
        logger.error(f"Failed to send notification to {telegram_id}: {e}")
        return False


async def notify_complaint_created(
    telegram_id: int,
    ticket_id: str,
) -> bool:
    """Send confirmation message to user."""
    if not _bot_instance:
        return False

    text = (
        f"✅ <b>Murojaatingiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"🎫 <b>Chipta raqamingiz:</b> <code>{ticket_id}</code>\n\n"
        f"Murojaatingiz moderatorlar tomonidan ko'rib chiqiladi. "
        f"Holat o'zgarganda sizga bot orqali xabar yuboriladi."
    )
    try:
        await _bot_instance.send_message(chat_id=telegram_id, text=text, parse_mode="HTML")
        return True
    except TelegramAPIError as e:
        logger.error(f"Failed to send notification to {telegram_id}: {e}")
        return False


async def notify_admins_new_complaint(complaint_id: int) -> int:
    """
    Send detailed notification with photo and action buttons to all admins and moderators.
    """
    if not _bot_instance:
        logger.warning("Bot instance not set for admin notification")
        return 0

    from apps.complaints.models import Complaint
    from apps.users.models import TelegramUser, UserRole

    @sync_to_async
    def get_data():
        try:
            c = Complaint.objects.select_related('user').get(id=complaint_id)
        except Complaint.DoesNotExist:
            return None, []

        admin_ids = list(TelegramUser.objects.filter(
            role__in=[UserRole.ADMIN, UserRole.MODERATOR],
            is_active=True
        ).values_list('telegram_id', flat=True))

        return c, admin_ids

    complaint, admin_ids = await get_data()
    if not complaint or not admin_ids:
        logger.info(f"No admins found to notify for complaint {complaint_id}")
        return 0

    user_mention = f"@{complaint.user.username}" if complaint.user.username else f"ID: {complaint.user.telegram_id}"
    admin_caption = (
        f"🚨 <b>YANGI SHIKOYAT KELIB TUSHDI!</b>\n\n"
        f"🎫 <b>Chipta ID:</b> <code>{complaint.ticket_id}</code>\n"
        f"👤 <b>Foydalanuvchi:</b> {complaint.user.full_name} ({user_mention})\n"
        f"🆔 <b>User ID:</b> <code>{complaint.user.telegram_id}</code>\n"
        f"📅 <b>Sana:</b> {complaint.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"📝 <b>Tavsif:</b>\n{complaint.description}\n\n"
        f"📍 <b>Joylashuv:</b> <a href=\"https://maps.google.com/?q={complaint.latitude},{complaint.longitude}\">Xaritada ochish (GPS)</a>"
    )

    admin_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔍 Ko'rib chiqilmoqda",
                    callback_data=f"adm_status_{complaint.id}_UNDER_REVIEW"
                ),
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"adm_status_{complaint.id}_APPROVED"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"adm_status_{complaint.id}_REJECTED"
                ),
                InlineKeyboardButton(
                    text="🎯 Hal qilindi",
                    callback_data=f"adm_status_{complaint.id}_RESOLVED"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📍 Xaritada ko'rish (Google Maps)",
                    url=f"https://maps.google.com/?q={complaint.latitude},{complaint.longitude}"
                )
            ]
        ]
    )

    sent_count = 0
    for admin_id in admin_ids:
        try:
            if complaint.photo_file_id:
                await _bot_instance.send_photo(
                    chat_id=admin_id,
                    photo=complaint.photo_file_id,
                    caption=admin_caption,
                    reply_markup=admin_kb,
                    parse_mode="HTML",
                )
            else:
                await _bot_instance.send_message(
                    chat_id=admin_id,
                    text=admin_caption,
                    reply_markup=admin_kb,
                    parse_mode="HTML",
                    disable_web_page_preview=False,
                )
            sent_count += 1
        except Exception as e:
            logger.warning(f"Failed to send admin alert to {admin_id}: {e}")

    logger.info(f"Notified {sent_count} admins about complaint {complaint.ticket_id}")
    return sent_count


async def notify_general_message(
    telegram_id: int,
    text: str,
) -> bool:
    if not _bot_instance:
        return False
    try:
        await _bot_instance.send_message(chat_id=telegram_id, text=text, parse_mode="HTML")
        return True
    except TelegramAPIError as e:
        logger.error(f"Failed to send notification to {telegram_id}: {e}")
        return False
