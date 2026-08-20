import logging
import re
import os
import json

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from bot.config import get_bot_config
from bot.keyboards.consumer import consumer_keyboard
from bot.keyboards.complaint import (
    cancel_keyboard,
    camera_keyboard,
    complaint_reasons_keyboard,
    location_keyboard,
    complaint_detail_keyboard,
    complaints_list_keyboard,
)
from bot.services.complaint_service import (
    create_complaint,
    get_user_complaints,
    get_complaint_by_id,
    update_complaint_status_by_admin,
)
from bot.services.user_service import get_user_language, is_entrepreneur_user
from bot.services.admin_service import is_admin_user
from bot.services.notification_service import (
    notify_complaint_created,
    notify_admins_new_complaint,
    notify_complaint_status_changed,
)
from bot.states.complaint import ComplaintStates
from bot.utils.i18n import get_text
from bot.utils.formatters import (
    format_complaint_confirmation,
    format_complaint_detail,
    format_date,
    format_complaint_status,
)

logger = logging.getLogger(__name__)
router = Router(name='complaints_router')


# ─── Start Complaint FSM ────────────────────────────────────────────────────

@router.message(F.text.in_(["📝 Shikoyat qilish", "📝 Подать жалобу", "Shikoyat qilish", "/complaint", "/shikoyat"]))
async def start_complaint(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    await state.set_state(ComplaintStates.waiting_for_description)
    await message.answer(
        get_text('complaint_start', lang),
        reply_markup=complaint_reasons_keyboard(lang),
        parse_mode="HTML",
    )


# ─── State 1: Description (Text, Voice, or Reason Button) ─────────────────────

@router.message(ComplaintStates.waiting_for_description, F.voice)
async def process_description_voice(message: Message, state: FSMContext) -> None:
    """Handle voice message description for seniors/ease-of-use."""
    lang = await get_user_language(message.from_user.id)
    voice_file_id = message.voice.file_id
    duration = message.voice.duration
    desc = f"🎙 [Ovozli xabar ({duration} soniya)]" if lang == 'uz' else f"🎙 [Голосовое сообщение ({duration} сек)]"
    
    await state.update_data(description=desc, voice_file_id=voice_file_id)
    await state.set_state(ComplaintStates.waiting_for_photo)
    
    await message.answer(
        "✅ <b>" + ("Ovozli xabar qabul qilindi!" if lang == 'uz' else "Голосовое сообщение принято!") + "</b>\n\n" +
        get_text('complaint_photo_prompt', lang),
        reply_markup=cancel_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(ComplaintStates.waiting_for_description, F.text)
async def process_description_text(message: Message, state: FSMContext) -> None:
    lang = await get_user_language(message.from_user.id)
    text = (message.text or '').strip()

    if text in ['❌ Bekor qilish', '❌ Отмена']:
        await _cancel_complaint(message, state)
        return

    # If user selected custom text option button
    if text in ["✍️ Boshqa muammo (yozib kiritish)", "✍️ Другая причина (написать)"]:
        await message.answer(
            get_text('complaint_custom_text_prompt', lang),
            reply_markup=cancel_keyboard(lang),
            parse_mode="HTML",
        )
        return

    # Check reason buttons or custom input
    if len(text) < 5:
        await message.answer(
            "⚠️ " + ("Iltimos, sababni tanlang yoki kamida 5 ta belgi yozing:" if lang == 'uz' else "Пожалуйста, выберите причину или введите не менее 5 символов:"),
            parse_mode="HTML",
        )
        return

    if len(text) > 3000:
        await message.answer(
            f"⚠️ " + (f"Tavsif juda uzun. Maksimal 3000 ta belgi (hozir {len(text)} ta)." if lang == 'uz' else f"Слишком длинный текст. Максимум 3000 символов (сейчас {len(text)})."),
            parse_mode="HTML",
        )
        return

    await state.update_data(description=text)
    await state.set_state(ComplaintStates.waiting_for_photo)
    config = get_bot_config()
    if config.webapp_url.startswith('https://'):
        await message.answer(
            get_text('complaint_photo_prompt', lang),
            reply_markup=camera_keyboard(lang),
            parse_mode="HTML",
        )
    else:
        dev_prompt = (
            "📸 <b>Mahsulotning holati va yaroqlilik muddatini rasmga olib yuboring:</b>" if lang == 'uz' else
            "📸 <b>Сфотографируйте товар и отправьте фото:</b>"
        )
        await message.answer(
            dev_prompt,
            reply_markup=cancel_keyboard(lang),
            parse_mode="HTML",
        )


@router.message(ComplaintStates.waiting_for_description, F.photo | F.document)
async def process_description_with_photo(message: Message, state: FSMContext) -> None:
    config = get_bot_config()
    lang = await get_user_language(message.from_user.id)
    caption = (message.caption or '').strip()

    if config.webapp_url.startswith('https://'):
        if len(caption) >= 5:
            await state.update_data(description=caption)
        await state.set_state(ComplaintStates.waiting_for_photo)
        reject_text = (
            "🛡️ <b>Xavfsizlik talabi:</b>\n\n"
            "Telefon xotirasi (galereya)dan rasm yuklash taqiqlangan. "
            "Murojaat haqqoniy bo'lishi uchun rasm faqat <b>voqea joyida jonli kamera</b> orqali olinishi shart.\n\n"
            "👇 Pastdagi <b>«📸 Kamerani ochish (Jonli)»</b> tugmasini bosing:"
        ) if lang == 'uz' else (
            "🛡️ <b>Требование безопасности:</b>\n\n"
            "Загрузка фото из галереи запрещена. "
            "Фотография должна быть сделана исключительно через <b>онлайн камеру</b> на месте.\n\n"
            "👇 Нажмите кнопку <b>«📸 Открыть камеру (Онлайн)»</b> ниже:"
        )
        await message.answer(
            reject_text,
            reply_markup=camera_keyboard(lang),
            parse_mode="HTML",
        )
    else:
        photo_id = message.photo[-1].file_id if message.photo else message.document.file_id
        if len(caption) >= 5:
            await state.update_data(description=caption, photo_file_id=photo_id)
            await state.set_state(ComplaintStates.waiting_for_location)
            await message.answer(
                get_text('complaint_location_prompt', lang),
                reply_markup=location_keyboard(lang),
                parse_mode="HTML",
            )
        else:
            await state.update_data(photo_file_id=photo_id)
            await message.answer(
                "📸 " + ("Rasm qabul qilindi!\n\nEndi muammoni tanlang yoki yozing:" if lang == 'uz' else "Фото принято!\n\nТеперь выберите причину или напишите:"),
                reply_markup=complaint_reasons_keyboard(lang),
                parse_mode="HTML",
            )


# ─── State 2: Photo (Live Camera WebApp or HTTP fallback) ────────────────────

@router.message(ComplaintStates.waiting_for_photo, F.web_app_data)
async def process_camera_photo_webapp(message: Message, state: FSMContext) -> None:
    """Handle photo captured from live Camera WebApp."""
    lang = await get_user_language(message.from_user.id)
    try:
        payload = json.loads(message.web_app_data.data)
        file_path = payload.get('file_path')

        if not file_path or not os.path.exists(file_path):
            await message.answer(
                "⚠️ " + ("Rasm fayli topilmadi. Iltimos, kamerani ochib qayta rasmga oling:" if lang == 'uz' else "Файл не найден. Пожалуйста, откройте камеру и сделайте фото заново:"),
                reply_markup=camera_keyboard(lang),
            )
            return

        # Send confirmation photo to telegram chat and capture Telegram file_id
        photo_file = FSInputFile(file_path)
        confirm_caption = (
            "📸 <b>Jonli kamera orqali olingan rasm qabul qilindi!</b>" if lang == 'uz' else
            "📸 <b>Фото с онлайн камеры успешно принято!</b>"
        )
        sent_msg = await message.answer_photo(
            photo=photo_file,
            caption=confirm_caption,
            parse_mode="HTML"
        )
        photo_id = sent_msg.photo[-1].file_id
        await state.update_data(photo_file_id=photo_id, local_photo_path=file_path)
        await state.set_state(ComplaintStates.waiting_for_location)
        await message.answer(
            get_text('complaint_location_prompt', lang),
            reply_markup=location_keyboard(lang),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Error processing camera webapp data: {e}", exc_info=True)
        await message.answer(
            "⚠️ " + ("Rasmni qayta ishlashda xatolik yuz berdi. Qayta urinib ko'ring:" if lang == 'uz' else "Ошибка при обработке фото. Попробуйте еще раз:"),
            reply_markup=camera_keyboard(lang),
        )


@router.message(ComplaintStates.waiting_for_photo, F.photo | F.document)
async def reject_or_accept_photo_in_waiting(message: Message, state: FSMContext) -> None:
    """If HTTPS WebApp camera is active, enforce live camera. Otherwise (local HTTP test), accept photo."""
    config = get_bot_config()
    lang = await get_user_language(message.from_user.id)

    if config.webapp_url.startswith('https://'):
        reject_text = (
            "🛡️ <b>Xavfsizlik talabi:</b>\n\n"
            "Telefon xotirasi (galereya)dan rasm yuklash taqiqlangan.\n"
            "Soxtalashtirishlarning oldini olish uchun rasm faqat <b>voqea joyida jonli kamera</b> orqali olinishi shart.\n\n"
            "👇 Iltimos, pastdagi <b>«📸 Kamerani ochish (Jonli)»</b> tugmasini bosing:"
        ) if lang == 'uz' else (
            "🛡️ <b>Требование безопасности:</b>\n\n"
            "Загрузка фото из галереи отключена.\n"
            "Фотография должна быть сделана исключительно через <b>онлайн камеру</b> на месте.\n\n"
            "👇 Пожалуйста, нажмите кнопку <b>«📸 Открыть камеру (Онлайн)»</b> ниже:"
        )
        await message.answer(
            reject_text,
            reply_markup=camera_keyboard(lang),
            parse_mode="HTML",
        )
    else:
        photo_id = message.photo[-1].file_id if message.photo else message.document.file_id
        await state.update_data(photo_file_id=photo_id)
        await state.set_state(ComplaintStates.waiting_for_location)
        await message.answer(
            get_text('complaint_location_prompt', lang),
            reply_markup=location_keyboard(lang),
            parse_mode="HTML",
        )


@router.message(ComplaintStates.waiting_for_photo, F.text.in_(['❌ Bekor qilish', '❌ Отмена']))
async def cancel_at_photo(message: Message, state: FSMContext) -> None:
    await _cancel_complaint(message, state)


@router.message(ComplaintStates.waiting_for_photo)
async def process_photo_invalid(message: Message) -> None:
    config = get_bot_config()
    lang = await get_user_language(message.from_user.id)
    kb = camera_keyboard(lang) if config.webapp_url.startswith('https://') else cancel_keyboard(lang)
    await message.answer(
        "⚠️ " + ("Iltimos, mahsulot <b>rasmini</b> yuboring yoki «❌ Bekor qilish» tugmasini bosing." if lang == 'uz' else "Пожалуйста, отправьте <b>фото</b> товара или нажмите «❌ Отмена»."),
        reply_markup=kb,
        parse_mode="HTML",
    )


# ─── State 3: Location (Mandatory Real GPS Check) ──────────────────────────

@router.message(ComplaintStates.waiting_for_location, F.location)
async def process_location_gps(message: Message, state: FSMContext) -> None:
    await _finalize_complaint(
        message=message,
        state=state,
        latitude=message.location.latitude,
        longitude=message.location.longitude,
    )


@router.message(ComplaintStates.waiting_for_location, F.text.in_(['❌ Bekor qilish', '❌ Отмена']))
async def cancel_at_location(message: Message, state: FSMContext) -> None:
    await _cancel_complaint(message, state)


@router.message(ComplaintStates.waiting_for_location)
async def process_location_invalid(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    await message.answer(
        get_text('complaint_location_prompt', lang),
        reply_markup=location_keyboard(lang),
        parse_mode="HTML",
    )


async def _finalize_complaint(message: Message, state: FSMContext, latitude: float, longitude: float) -> None:
    lang = await get_user_language(message.from_user.id)
    data = await state.get_data()
    description = data.get('description', 'Tavsif berilmagan')
    photo_file_id = data.get('photo_file_id', '')

    user_info = {
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name or '',
        'username': message.from_user.username or '',
    }

    try:
        complaint = await create_complaint(
            telegram_id=message.from_user.id,
            description=description,
            photo_file_id=photo_file_id,
            latitude=latitude,
            longitude=longitude,
            user_info=user_info,
        )
    except Exception as e:
        logger.error(f"Failed to create complaint for user {message.from_user.id}: {e}", exc_info=True)
        await state.clear()
        is_admin = await is_admin_user(message.from_user.id)
        is_ent = await is_entrepreneur_user(message.from_user.id)
        await message.answer(
            "⚠️ " + ("Murojaatni saqlashda texnik xatolik yuz berdi. Iltimos, qayta urinib ko'ring." if lang == 'uz' else "Произошла техническая ошибка. Пожалуйста, попробуйте снова."),
            reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
        )
        return

    await state.clear()

    confirm_text = format_complaint_confirmation(
        ticket_id=complaint.ticket_id,
        description=complaint.description,
        latitude=float(complaint.latitude),
        longitude=float(complaint.longitude),
    )
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)
    await message.answer(
        confirm_text,
        reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
        parse_mode="HTML",
    )

    # 1. Notify user
    try:
        await notify_complaint_created(message.from_user.id, complaint.ticket_id)
    except Exception as e:
        logger.warning(f"User confirmation notification error: {e}")

    # 2. Notify all admins with photo/voice + action buttons
    try:
        await notify_admins_new_complaint(complaint.id)
    except Exception as e:
        logger.error(f"Admin alert notification error: {e}", exc_info=True)


# ─── Admin Moderation Actions (Inline Callbacks) ───────────────────────────

@router.callback_query(F.data.startswith("adm_status_"))
async def admin_status_callback(callback: CallbackQuery) -> None:
    parts = callback.data.split('_')
    # adm_status_<complaint_id>_<STATUS>
    if len(parts) < 4:
        await callback.answer("Noto'g'ri so'rov.")
        return

    complaint_id = int(parts[2])
    new_status = '_'.join(parts[3:])

    try:
        complaint = await update_complaint_status_by_admin(
            complaint_id=complaint_id,
            new_status=new_status,
            comment=f"Admin @{callback.from_user.username or callback.from_user.id} tomonidan yangilandi"
        )
        if not complaint:
            await callback.answer("Murojaat topilmadi.", show_alert=True)
            return

        # Notify user about the new status
        await notify_complaint_status_changed(
            telegram_id=complaint.user.telegram_id,
            ticket_id=complaint.ticket_id,
            new_status=new_status,
        )

        status_text = complaint.get_status_display()
        await callback.answer(f"✅ Holat «{status_text}» ga o'zgartirildi!")

        # Update caption or message
        updated_caption = (
            f"🎫 <b>Murojaat:</b> <code>{complaint.ticket_id}</code>\n"
            f"👤 <b>Foydalanuvchi:</b> {complaint.user.full_name}\n"
            f"📊 <b>Yangi holat:</b> <b>{status_text}</b>\n"
            f"👮 <b>Moderator:</b> @{callback.from_user.username or callback.from_user.id}\n\n"
            f"📝 <b>Tavsif:</b>\n{complaint.description}"
        )
        if callback.message.caption:
            await callback.message.edit_caption(caption=updated_caption, parse_mode="HTML")
        else:
            await callback.message.edit_text(text=updated_caption, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error in admin status callback: {e}", exc_info=True)
        await callback.answer("Xatolik yuz berdi.", show_alert=True)


# ─── My Complaints ────────────────────────────────────────────────────────

@router.message(F.text.in_(["📁 Mening murojaatlarim", "📁 Мои обращения", "Mening murojaatlarim", "/my_complaints"]))
async def my_complaints(message: Message) -> None:
    lang = await get_user_language(message.from_user.id)
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)

    try:
        complaints, total_pages = await get_user_complaints(message.from_user.id, page=1)
    except Exception as e:
        logger.error(f"My complaints error for {message.from_user.id}: {e}")
        await message.answer("⚠️ " + ("Murojaatlarni olishda xatolik yuz berdi." if lang == 'uz' else "Ошибка при получении обращений."))
        return

    if not complaints:
        text = (
            "📁 <b>Mening murojaatlarim</b>\n\nSizda hali yuborilgan murojaatlar yo'q.\n\n"
            "📝 Yangi murojaat yuborish uchun quyidagi «📝 Shikoyat qilish» tugmasini bosing."
            if lang == 'uz' else
            "📁 <b>Мои обращения</b>\n\nУ вас пока нет отправленных обращений.\n\n"
            "📝 Чтобы отправить жалобу, нажмите «📝 Подать жалобу» ниже."
        )
        await message.answer(
            text,
            reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
            parse_mode="HTML",
        )
        return

    text = _build_complaints_text(complaints, page=1, total_pages=total_pages, lang=lang)
    kb = complaints_list_keyboard(complaints, 1, total_pages, lang=lang)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("complaints_page_"))
async def complaints_page(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    page = int(callback.data.split('_')[2])
    try:
        complaints, total_pages = await get_user_complaints(callback.from_user.id, page=page)
        text = _build_complaints_text(complaints, page=page, total_pages=total_pages, lang=lang)
        kb = complaints_list_keyboard(complaints, page, total_pages, lang=lang)
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        logger.error(f"Complaints page error: {e}")
        await callback.answer("Xatolik yuz berdi.")


@router.callback_query(F.data.startswith("complaint_detail_"))
async def complaint_detail_cb(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    complaint_id = int(callback.data.split('_')[2])
    try:
        c = await get_complaint_by_id(complaint_id, callback.from_user.id)
        if not c:
            await callback.answer("Murojaat topilmadi." if lang == 'uz' else "Обращение не найдено.")
            return
        text = format_complaint_detail(c)
        await callback.message.answer(
            text,
            reply_markup=complaint_detail_keyboard(c.id, lang=lang),
            parse_mode="HTML",
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Complaint detail error: {e}")
        await callback.answer("Xatolik yuz berdi.")


@router.callback_query(F.data.startswith("complaint_photo_"))
async def complaint_photo_cb(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    complaint_id = int(callback.data.split('_')[2])
    try:
        c = await get_complaint_by_id(complaint_id, callback.from_user.id)
        if not c or not c.photo_file_id:
            await callback.answer("Rasm topilmadi." if lang == 'uz' else "Фото не найдено.")
            return
        caption_text = f"📷 Murojaat rasmi: <code>{c.ticket_id}</code>" if lang == 'uz' else f"📷 Фото обращения: <code>{c.ticket_id}</code>"
        await callback.message.answer_photo(
            c.photo_file_id,
            caption=caption_text,
            parse_mode="HTML",
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Complaint photo error: {e}")
        await callback.answer("Xatolik yuz berdi.")


@router.callback_query(F.data.startswith("complaint_location_"))
async def complaint_location_cb(callback: CallbackQuery) -> None:
    lang = await get_user_language(callback.from_user.id)
    complaint_id = int(callback.data.split('_')[2])
    try:
        c = await get_complaint_by_id(complaint_id, callback.from_user.id)
        if not c or not c.latitude:
            await callback.answer("Joylashuv topilmadi." if lang == 'uz' else "Локация не найдена.")
            return
        await callback.message.answer_location(
            latitude=float(c.latitude),
            longitude=float(c.longitude),
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Complaint location error: {e}")
        await callback.answer("Xatolik yuz berdi.")


@router.callback_query(F.data == "ignore")
async def ignore_cb(callback: CallbackQuery) -> None:
    await callback.answer()


# ─── Helpers ──────────────────────────────────────────────────────────────

async def _cancel_complaint(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    is_admin = await is_admin_user(message.from_user.id)
    is_ent = await is_entrepreneur_user(message.from_user.id)
    text = "❌ Murojaat bekor qilindi.\n\nAsosiy menyuga qaytdingiz." if lang == 'uz' else "❌ Обращение отменено.\n\nВы вернулись в главное меню."
    await message.answer(
        text,
        reply_markup=consumer_keyboard(is_admin=is_admin, is_entrepreneur=is_ent, lang=lang),
    )


def _build_complaints_text(complaints, page: int, total_pages: int, lang: str = 'uz') -> str:
    title = f"📁 <b>Mening murojaatlarim</b> (sahifa {page}/{total_pages}):\n" if lang == 'uz' else f"📁 <b>Мои обращения</b> (страница {page}/{total_pages}):\n"
    lines = [title]
    for c in complaints:
        status_label = format_complaint_status(c.status)
        date_label = format_date(c.created_at)
        lines.append(
            f"🎫 <b>{c.ticket_id}</b>\n"
            f"   Holat: {status_label}\n"
            f"   Sana: 📅 {date_label}\n"
        )
    hint = "Batafsil ma'lumot olish uchun quyidagi tugmalardan foydalaning:" if lang == 'uz' else "Для подробной информации нажмите кнопку ниже:"
    lines.append(hint)
    return '\n'.join(lines)
