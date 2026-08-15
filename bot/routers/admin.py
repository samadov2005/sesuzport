import logging
import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.admin import (
    admin_main_keyboard,
    admin_pending_list_keyboard,
    admin_complaint_actions_keyboard,
    admin_broadcast_confirm_keyboard,
    admin_stores_filter_keyboard,
    admin_store_edit_keyboard,
)
from bot.keyboards.role import role_keyboard
from bot.keyboards.complaint import cancel_keyboard
from bot.services.admin_service import (
    is_admin_user,
    get_admin_dashboard_stats,
    get_pending_complaints,
    search_complaint_or_user,
    get_all_active_user_ids,
    get_stores_by_safety,
    update_store_safety,
)
from bot.services.complaint_service import (
    get_complaint_by_id,
    update_complaint_status_by_admin,
)
from bot.services.notification_service import (
    notify_complaint_status_changed,
    notify_general_message,
)
from bot.states.admin import AdminStates
from bot.utils.formatters import format_date, format_complaint_status

logger = logging.getLogger(__name__)
router = Router(name='admin_router')


# ─── Admin Check Helper ───────────────────────────────────────────────────

async def _check_admin(event: Message | CallbackQuery) -> bool:
    user_id = event.from_user.id
    if not await is_admin_user(user_id):
        if isinstance(event, Message):
            await event.answer("⛔ <b>Kirish taqiqlangan:</b> Sizda administrator huquqlari mavjud emas.", parse_mode="HTML")
        else:
            await event.answer("⛔ Sizda administrator huquqlari yo'q.", show_alert=True)
        return False
    return True


# ─── Admin Menu ───────────────────────────────────────────────────────────

@router.message(Command('admin'))
@router.message(F.text.in_(["🛡️ Admin panel", "Admin panel", "/dashboard"]))
async def cmd_admin_panel(message: Message, state: FSMContext) -> None:
    if not await _check_admin(message):
        return

    await state.clear()
    await message.answer(
        "🛡️ <b>SESPORT Administrator Boshqaruv Markazi</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:\n"
        "• ⏳ <b>Kutilayotganlar</b> — Navbatdagi murojaatlarni ko'rib chiqish\n"
        "• 📊 <b>Statistika</b> — Tizimning real vaqtdagi ko'rsatkichlari\n"
        "• 🔍 <b>Qidirish</b> — Chipta ID yoki foydalanuvchi qidiruvi\n"
        "• 📢 <b>Xabar tarqatish</b> — Barcha foydalanuvchilarga e'lon\n"
        "• 🏪 <b>Do'konlar</b> — Xavfsizlik darajasini boshqarish",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML",
    )


# ─── 1. Statistics ────────────────────────────────────────────────────────

@router.message(F.text.in_(["📊 Statistika", "/stats"]))
async def admin_statistics(message: Message) -> None:
    if not await _check_admin(message):
        return

    stats = await get_admin_dashboard_stats()

    text = (
        "📊 <b>SESPORT — Tizim statistikasi</b>\n\n"
        "👥 <b>Foydalanuvchilar:</b>\n"
        f"• Jami: <b>{stats['total_users']}</b> ta\n"
        f"• Bugun qo'shilgan: <b>+{stats['new_users_today']}</b> ta\n\n"
        "📋 <b>Murojaatlar:</b>\n"
        f"• Jami: <b>{stats['total_complaints']}</b> ta\n"
        f"• Bugungi: <b>{stats['complaints_today']}</b> ta\n"
        f"• ⏳ Kutilmoqda: <b>{stats['pending']}</b> ta\n"
        f"• 🔍 Ko'rilmoqda: <b>{stats['under_review']}</b> ta\n"
        f"• ✅ Tasdiqlangan: <b>{stats['approved']}</b> ta\n"
        f"• ❌ Rad etilgan: <b>{stats['rejected']}</b> ta\n"
        f"• 🎯 Hal qilingan: <b>{stats['resolved']}</b> ta\n\n"
        "🏪 <b>Do'konlar tarmog'i:</b>\n"
        f"• Jami: <b>{stats['total_stores']}</b> ta\n"
        f"• 🟢 Xavfsiz: <b>{stats['green_stores']}</b> ta\n"
        f"• 🟡 Ehtiyotkor: <b>{stats['yellow_stores']}</b> ta\n"
        f"• 🔴 Xavfli: <b>{stats['red_stores']}</b> ta"
    )
    await message.answer(text, parse_mode="HTML")


# ─── 2. Pending Complaints Queue ──────────────────────────────────────────

@router.message(F.text.in_(["⏳ Kutilayotgan shikoyatlar", "/pending"]))
async def admin_pending_complaints(message: Message) -> None:
    if not await _check_admin(message):
        return

    complaints, total_pages = await get_pending_complaints(page=1)
    if not complaints:
        await message.answer("✅ <b>Hozircha yangi kutilayotgan murojaatlar yo'q.</b> Barcha shikoyatlar ko'rib chiqilgan!", parse_mode="HTML")
        return

    text = f"⏳ <b>Ko'rib chiqilishi kerak bo'lgan murojaatlar</b> (1/{total_pages}):\n\nBirini tanlab, to'g'ridan-to'g'ri o'zgartiring:"
    kb = admin_pending_list_keyboard(complaints, 1, total_pages)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("adm_page_"))
async def admin_pending_page(callback: CallbackQuery) -> None:
    if not await _check_admin(callback):
        return

    page = int(callback.data.split('_')[2])
    complaints, total_pages = await get_pending_complaints(page=page)

    if not complaints:
        await callback.message.edit_text("✅ <b>Kutilayotgan murojaatlar qolmadi.</b>", parse_mode="HTML")
        await callback.answer()
        return

    text = f"⏳ <b>Ko'rib chiqilishi kerak bo'lgan murojaatlar</b> ({page}/{total_pages}):"
    kb = admin_pending_list_keyboard(complaints, page, total_pages)
    try:
        if callback.message.text:
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        else:
            await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("adm_view_"))
async def admin_view_complaint(callback: CallbackQuery) -> None:
    if not await _check_admin(callback):
        return

    complaint_id = int(callback.data.split('_')[2])
    c = await get_complaint_by_id(complaint_id)
    if not c:
        await callback.answer("Murojaat topilmadi.", show_alert=True)
        return

    status_str = format_complaint_status(c.status)
    caption = (
        f"🎫 <b>Murojaat:</b> <code>{c.ticket_id}</code>\n"
        f"📊 <b>Holat:</b> {status_str}\n"
        f"👤 <b>Foydalanuvchi:</b> {c.user.full_name} (@{c.user.username or 'yo\'q'})\n"
        f"🆔 <b>User ID:</b> <code>{c.user.telegram_id}</code>\n"
        f"📅 <b>Sana:</b> {format_date(c.created_at)}\n\n"
        f"📝 <b>Tavsif:</b>\n{c.description}\n\n"
        f"📍 <b>Koordinatalar:</b> <code>{c.latitude}, {c.longitude}</code>"
    )

    kb = admin_complaint_actions_keyboard(
        complaint_id=c.id,
        current_status=c.status,
        latitude=float(c.latitude) if c.latitude else None,
        longitude=float(c.longitude) if c.longitude else None,
    )

    if c.photo_file_id:
        try:
            await callback.message.answer_photo(
                photo=c.photo_file_id,
                caption=caption,
                reply_markup=kb,
                parse_mode="HTML"
            )
            await callback.answer()
            return
        except Exception as e:
            logger.warning(f"Failed to send photo for complaint {c.id}: {e}")

    await callback.message.answer(caption, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


# ─── Moderation Status Buttons ─────────────────────────────────────────────

@router.callback_query(F.data.startswith("adm_setstatus_"))
async def admin_set_status(callback: CallbackQuery) -> None:
    if not await _check_admin(callback):
        return

    parts = callback.data.split('_')
    # adm_setstatus_<complaint_id>_<STATUS>
    complaint_id = int(parts[2])
    new_status = '_'.join(parts[3:])

    complaint = await update_complaint_status_by_admin(
        complaint_id=complaint_id,
        new_status=new_status,
        comment=f"Moderator @{callback.from_user.username or callback.from_user.id} tomonidan tasdiqlandi"
    )
    if not complaint:
        await callback.answer("Murojaat topilmadi.", show_alert=True)
        return

    # Notify user
    await notify_complaint_status_changed(
        telegram_id=complaint.user.telegram_id,
        ticket_id=complaint.ticket_id,
        new_status=new_status,
    )

    status_name = complaint.get_status_display()
    await callback.answer(f"✅ Holat «{status_name}» ga o'zgartirildi!")

    updated_caption = (
        f"🎫 <b>Murojaat:</b> <code>{complaint.ticket_id}</code>\n"
        f"📊 <b>Yangi holat:</b> <b>{status_name}</b>\n"
        f"👮 <b>Moderator:</b> @{callback.from_user.username or callback.from_user.id}\n"
        f"👤 <b>Foydalanuvchi:</b> {complaint.user.full_name}\n\n"
        f"📝 <b>Tavsif:</b>\n{complaint.description}"
    )

    kb = admin_complaint_actions_keyboard(
        complaint_id=complaint.id,
        current_status=complaint.status,
        latitude=float(complaint.latitude) if complaint.latitude else None,
        longitude=float(complaint.longitude) if complaint.longitude else None,
    )

    if callback.message.caption:
        await callback.message.edit_caption(caption=updated_caption, reply_markup=kb, parse_mode="HTML")
    else:
        await callback.message.edit_text(text=updated_caption, reply_markup=kb, parse_mode="HTML")


# ─── Moderation Comment / Reply to User ────────────────────────────────────

@router.callback_query(F.data.startswith("adm_comment_"))
async def admin_start_comment(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _check_admin(callback):
        return

    complaint_id = int(callback.data.split('_')[2])
    await state.set_state(AdminStates.waiting_for_moderation_comment)
    await state.update_data(moderating_complaint_id=complaint_id)

    await callback.message.answer(
        f"💬 <b>Murojaat bo'yicha foydalanuvchiga xabar/izoh yozing:</b>\n\n"
        f"Yozgan xabaringiz to'g'ridan-to'g'ri foydalanuvchiga yetkaziladi va shikoyat tarixiga saqlanadi.\n"
        f"<i>Bekor qilish uchun /cancel yozing.</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminStates.waiting_for_moderation_comment, F.text)
async def admin_process_comment(message: Message, state: FSMContext) -> None:
    if message.text == '❌ Bekor qilish':
        await state.clear()
        await message.answer("❌ Izoh yozish bekor qilindi.", reply_markup=admin_main_keyboard())
        return

    data = await state.get_data()
    complaint_id = data.get('moderating_complaint_id')
    comment_text = message.text.strip()

    c = await get_complaint_by_id(complaint_id)
    if not c:
        await state.clear()
        await message.answer("⚠️ Murojaat topilmadi.", reply_markup=admin_main_keyboard())
        return

    # Update in DB
    await update_complaint_status_by_admin(
        complaint_id=complaint_id,
        new_status=c.status,
        comment=comment_text
    )

    # Notify user with comment
    await notify_complaint_status_changed(
        telegram_id=c.user.telegram_id,
        ticket_id=c.ticket_id,
        new_status=c.status,
        moderation_comment=comment_text,
    )

    await state.clear()
    await message.answer(
        f"✅ <b>Foydalanuvchiga izoh muvaffaqiyatli yuborildi!</b>\n\n"
        f"🎫 Chipta: <code>{c.ticket_id}</code>\n"
        f"💬 Izoh: <i>{comment_text}</i>",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )


# ─── 3. Search (ID / User) ────────────────────────────────────────────────

@router.message(F.text.in_(["🔍 Qidirish (ID/User)", "/find", "/search"]))
async def admin_search_start(message: Message, state: FSMContext) -> None:
    if not await _check_admin(message):
        return

    await state.set_state(AdminStates.waiting_for_search_query)
    await message.answer(
        "🔍 <b>Qidiruv:</b>\n\n"
        "Qidirmoqchi bo'lgan ma'lumotingizni kiriting:\n"
        "• Chipta ID (masalan: <code>SES-2026-000001</code> yoki <code>000001</code>)\n"
        "• Foydalanuvchi Telegram ID (masalan: <code>1374355427</code>)\n"
        "• Foydalanuvchi username yoki ismi",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(AdminStates.waiting_for_search_query, F.text)
async def admin_search_process(message: Message, state: FSMContext) -> None:
    if message.text == '❌ Bekor qilish':
        await state.clear()
        await message.answer("Qidiruv bekor qilindi.", reply_markup=admin_main_keyboard())
        return

    query = message.text.strip()
    results = await search_complaint_or_user(query)

    complaints = results['complaints']
    users = results['users']

    if not complaints and not users:
        await message.answer(f"❌ <b>«{query}»</b> bo'yicha hech qanday murojaat yoki foydalanuvchi topilmadi.", parse_mode="HTML")
        return

    lines = [f"🔍 <b>Qidiruv natijalari («{query}»):</b>\n"]

    if complaints:
        lines.append("📋 <b>Topilgan murojaatlar:</b>")
        for c in complaints:
            lines.append(
                f"• 🎫 <b>{c.ticket_id}</b> ({format_complaint_status(c.status)})\n"
                f"  👤 {c.user.full_name} | 📅 {format_date(c.created_at)}\n"
                f"  <i>Ko'rish: /view_{c.id}</i>\n"
            )

    if users:
        lines.append("👤 <b>Topilgan foydalanuvchilar:</b>")
        for u in users:
            lines.append(
                f"• <b>{u.full_name}</b> (@{u.username or 'yo\'q'})\n"
                f"  ID: <code>{u.telegram_id}</code> | Rol: <b>{u.role}</b>\n"
                f"  Qo'shilgan: {format_date(u.created_at)}\n"
            )

    await state.clear()
    await message.answer('\n'.join(lines), reply_markup=admin_main_keyboard(), parse_mode="HTML")


@router.message(F.text.regexp(r'^/view_(\d+)$'))
async def admin_quick_view(message: Message) -> None:
    if not await _check_admin(message):
        return

    match = F.text.regexp(r'^/view_(\d+)$')
    complaint_id = int(message.text.replace('/view_', ''))
    c = await get_complaint_by_id(complaint_id)
    if not c:
        await message.answer("Murojaat topilmadi.")
        return

    caption = (
        f"🎫 <b>Murojaat:</b> <code>{c.ticket_id}</code>\n"
        f"📊 <b>Holat:</b> {format_complaint_status(c.status)}\n"
        f"👤 <b>Foydalanuvchi:</b> {c.user.full_name} (@{c.user.username or 'yo\'q'})\n"
        f"🆔 <b>User ID:</b> <code>{c.user.telegram_id}</code>\n"
        f"📅 <b>Sana:</b> {format_date(c.created_at)}\n\n"
        f"📝 <b>Tavsif:</b>\n{c.description}"
    )
    kb = admin_complaint_actions_keyboard(
        complaint_id=c.id,
        current_status=c.status,
        latitude=float(c.latitude) if c.latitude else None,
        longitude=float(c.longitude) if c.longitude else None,
    )
    if c.photo_file_id:
        await message.answer_photo(photo=c.photo_file_id, caption=caption, reply_markup=kb, parse_mode="HTML")
    else:
        await message.answer(caption, reply_markup=kb, parse_mode="HTML")


# ─── 4. Broadcast / Xabar tarqatish ───────────────────────────────────────

@router.message(F.text.in_(["📢 Xabar tarqatish", "/broadcast"]))
async def admin_broadcast_start(message: Message, state: FSMContext) -> None:
    if not await _check_admin(message):
        return

    await state.set_state(AdminStates.waiting_for_broadcast_message)
    await message.answer(
        "📢 <b>Barcha foydalanuvchilarga xabar tarqatish:</b>\n\n"
        "Barcha faol bot foydalanuvchilariga yuboriladigan xabar matnini kiriting.\n"
        "<i>HTML formatlash qo'llab-quvvatlanadi (qalin, kursiv, havolalar).</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(AdminStates.waiting_for_broadcast_message, F.text)
async def admin_broadcast_preview(message: Message, state: FSMContext) -> None:
    if message.text == '❌ Bekor qilish':
        await state.clear()
        await message.answer("Xabar tarqatish bekor qilindi.", reply_markup=admin_main_keyboard())
        return

    bcast_text = message.text
    await state.update_data(broadcast_text=bcast_text)
    await state.set_state(AdminStates.waiting_for_broadcast_confirm)

    user_ids = await get_all_active_user_ids()

    await message.answer(
        f"📝 <b>Xabar namunasi:</b>\n\n"
        f"{bcast_text}\n\n"
        f"👥 <b>Qabul qiluvchilar soni:</b> {len(user_ids)} nafar foydalanuvchi.\n\n"
        f"Haqiqatan ham ushbu xabarni barchaga tarqatmoqchimisiz?",
        reply_markup=admin_broadcast_confirm_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "adm_bcast_send", AdminStates.waiting_for_broadcast_confirm)
async def admin_broadcast_execute(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _check_admin(callback):
        return

    data = await state.get_data()
    bcast_text = data.get('broadcast_text')
    await state.clear()

    user_ids = await get_all_active_user_ids()
    await callback.message.edit_text("⏳ <b>Xabar yuborilmoqda...</b>", parse_mode="HTML")

    success_count = 0
    fail_count = 0

    for uid in user_ids:
        res = await notify_general_message(uid, bcast_text)
        if res:
            success_count += 1
        else:
            fail_count += 1
        await asyncio.sleep(0.04)  # throttle

    await callback.message.answer(
        f"📢 <b>Xabarnoma tarqatish yakunlandi!</b>\n\n"
        f"✅ Muvaffaqiyatli yetkazildi: <b>{success_count}</b> ta\n"
        f"❌ Xatolik yuz berdi: <b>{fail_count}</b> ta",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "adm_bcast_cancel")
async def admin_broadcast_cancel_cb(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("❌ Xabar tarqatish bekor qilindi.")
    await callback.answer()


# ─── 5. Store Safety Control ──────────────────────────────────────────────

@router.message(F.text.in_(["🏪 Do'konlar nazorati", "/stores_admin"]))
async def admin_stores_menu(message: Message) -> None:
    if not await _check_admin(message):
        return

    await message.answer(
        "🏪 <b>Do'konlar xavfsizligini boshqarish</b>\n\n"
        "Qaysi toifadagi do'konlarni ko'rmoqchisiz?",
        reply_markup=admin_stores_filter_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("adm_stores_"))
async def admin_stores_list(callback: CallbackQuery) -> None:
    if not await _check_admin(callback):
        return

    status = callback.data.split('_')[2]
    if status == 'back':
        await callback.message.edit_text("Qaysi toifadagi do'konlarni ko'rmoqchisiz?", reply_markup=admin_stores_filter_keyboard())
        await callback.answer()
        return

    stores = await get_stores_by_safety(status)
    if not stores:
        await callback.message.edit_text(
            f"Ushbu toifada do'konlar topilmadi.",
            reply_markup=admin_stores_filter_keyboard()
        )
        await callback.answer()
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    for s in stores:
        buttons.append([
            InlineKeyboardButton(text=f"🏪 {s.name} ({s.address[:20]})", callback_data=f"adm_editstore_{s.id}")
        ])
    buttons.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_stores_back")
    ])

    await callback.message.edit_text(
        f"<b>{status} toifasidagi do'konlar:</b>\nHolatini o'zgartirish uchun do'konni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_editstore_"))
async def admin_store_edit(callback: CallbackQuery) -> None:
    if not await _check_admin(callback):
        return

    store_id = int(callback.data.split('_')[2])
    from apps.stores.models import Store
    from asgiref.sync import sync_to_async

    @sync_to_async
    def get_store():
        try:
            return Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return None

    store = await get_store()
    if not store:
        await callback.answer("Do'kon topilmadi.", show_alert=True)
        return

    text = (
        f"🏪 <b>{store.name}</b>\n"
        f"📍 Manzil: {store.address}\n"
        f"📊 Joriy xavfsizlik holati: <b>{store.get_safety_status_display()}</b>\n\n"
        f"Yangi xavfsizlik darajasini belgilang:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=admin_store_edit_keyboard(store.id, store.safety_status),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_setstore_"))
async def admin_store_save(callback: CallbackQuery) -> None:
    if not await _check_admin(callback):
        return

    parts = callback.data.split('_')
    store_id = int(parts[2])
    new_status = parts[3]

    store = await update_store_safety(store_id, new_status)
    if not store:
        await callback.answer("Xatolik: do'kon topilmadi.", show_alert=True)
        return

    await callback.answer(f"✅ «{store.name}» xavfsizlik holati «{store.get_safety_status_display()}» ga o'zgartirildi!")
    await callback.message.edit_text(
        f"✅ <b>{store.name}</b> do'koni xavfsizlik darajasi <b>{store.get_safety_status_display()}</b> ga yangilandi.",
        reply_markup=admin_stores_filter_keyboard(),
        parse_mode="HTML"
    )


# ─── 6. Web Admin & Return ────────────────────────────────────────────────

@router.message(F.text == "🌐 Web Admin Panel")
async def admin_web_link(message: Message) -> None:
    if not await _check_admin(message):
        return

    await message.answer(
        "🌐 <b>Django Web Admin Panel</b>\n\n"
        "To'liq boshqaruv, grafiklar va hisobotlar uchun brauzer orqali kiring:\n"
        "🔗 <b>URL:</b> <a href=\"http://127.0.0.1:8000/admin/\">http://127.0.0.1:8000/admin/</a>\n\n"
        "👤 <b>Login:</b> <code>admin</code>\n"
        "🔑 <b>Parol:</b> <code>1</code>",
        parse_mode="HTML"
    )


@router.message(F.text == "👤 Foydalanuvchi menyusiga qaytish")
async def admin_return_to_user(message: Message) -> None:
    await message.answer("Asosiy foydalanuvchi menyusiga qaytdingiz.", reply_markup=role_keyboard())
