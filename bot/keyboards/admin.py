from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from apps.complaints.models import ComplaintStatus
from apps.stores.models import SafetyStatus


def admin_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⏳ Kutilayotgan shikoyatlar"),
                KeyboardButton(text="📊 Statistika")
            ],
            [
                KeyboardButton(text="🔍 Qidirish (ID/User)"),
                KeyboardButton(text="📢 Xabar tarqatish")
            ],
            [
                KeyboardButton(text="🏪 Do'konlar nazorati"),
                KeyboardButton(text="🌐 Web Admin Panel")
            ],
            [
                KeyboardButton(text="👤 Foydalanuvchi menyusiga qaytish")
            ]
        ],
        resize_keyboard=True,
        is_persistent=True
    )


def admin_pending_list_keyboard(complaints: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    
    status_icons = {
        ComplaintStatus.PENDING: "⏳",
        ComplaintStatus.UNDER_REVIEW: "🔍",
        ComplaintStatus.APPROVED: "✅",
        ComplaintStatus.REJECTED: "❌",
        ComplaintStatus.RESOLVED: "🎯",
    }

    for c in complaints:
        icon = status_icons.get(c.status, "📋")
        user_name = c.user.first_name if c.user else "Foydalanuvchi"
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {c.ticket_id} — {user_name[:12]}",
                callback_data=f"adm_view_{c.id}"
            )
        ])

    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"adm_page_{page-1}"))
    if total_pages > 1:
        nav_row.append(InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="ignore"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"adm_page_{page+1}"))

    if nav_row:
        buttons.append(nav_row)

    buttons.append([
        InlineKeyboardButton(text="🔄 Yangilash", callback_data=f"adm_page_{page}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_complaint_actions_keyboard(
    complaint_id: int,
    current_status: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> InlineKeyboardMarkup:
    rows = []

    # Row 1: Actions based on current status
    action_row1 = []
    if current_status != ComplaintStatus.UNDER_REVIEW:
        action_row1.append(
            InlineKeyboardButton(text="🔍 Ko'rilmoqda", callback_data=f"adm_setstatus_{complaint_id}_UNDER_REVIEW")
        )
    if current_status != ComplaintStatus.APPROVED:
        action_row1.append(
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"adm_setstatus_{complaint_id}_APPROVED")
        )
    if action_row1:
        rows.append(action_row1)

    # Row 2: Reject / Resolve
    action_row2 = []
    if current_status != ComplaintStatus.REJECTED:
        action_row2.append(
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"adm_setstatus_{complaint_id}_REJECTED")
        )
    if current_status != ComplaintStatus.RESOLVED:
        action_row2.append(
            InlineKeyboardButton(text="🎯 Hal qilindi", callback_data=f"adm_setstatus_{complaint_id}_RESOLVED")
        )
    if action_row2:
        rows.append(action_row2)

    # Row 3: Reply / Comment
    rows.append([
        InlineKeyboardButton(
            text="💬 Foydalanuvchiga izoh/javob yuborish",
            callback_data=f"adm_comment_{complaint_id}"
        )
    ])

    # Row 4: Map link + Back
    misc_row = []
    if latitude and longitude:
        misc_row.append(
            InlineKeyboardButton(
                text="📍 Xarita (Google Maps)",
                url=f"https://maps.google.com/?q={latitude},{longitude}"
            )
        )
    misc_row.append(
        InlineKeyboardButton(text="🔙 Ro'yxatga qaytish", callback_data="adm_page_1")
    )
    rows.append(misc_row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Barchaga yuborish", callback_data="adm_bcast_send"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="adm_bcast_cancel"),
            ]
        ]
    )


def admin_stores_filter_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔴 Xavfli do'konlar", callback_data="adm_stores_RED"),
                InlineKeyboardButton(text="🟡 Ehtiyotkor", callback_data="adm_stores_YELLOW"),
            ],
            [
                InlineKeyboardButton(text="🟢 Xavfsiz do'konlar", callback_data="adm_stores_GREEN"),
            ]
        ]
    )


def admin_store_edit_keyboard(store_id: int, current_status: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟢 Xavfsiz" if current_status != SafetyStatus.GREEN else "🟢 [Xavfsiz]",
                    callback_data=f"adm_setstore_{store_id}_GREEN"
                ),
                InlineKeyboardButton(
                    text="🟡 Ehtiyotkor" if current_status != SafetyStatus.YELLOW else "🟡 [Ehtiyotkor]",
                    callback_data=f"adm_setstore_{store_id}_YELLOW"
                ),
                InlineKeyboardButton(
                    text="🔴 Xavfli" if current_status != SafetyStatus.RED else "🔴 [Xavfli]",
                    callback_data=f"adm_setstore_{store_id}_RED"
                ),
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm_stores_back")
            ]
        ]
    )
