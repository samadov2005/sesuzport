def format_complaint_status(status: str) -> str:
    statuses = {
        'PENDING': '⏳ Moderatsiya kutilmoqda',
        'UNDER_REVIEW': "🔍 Ko'rib chiqilmoqda",
        'APPROVED': '✅ Tasdiqlandi',
        'REJECTED': '❌ Rad etildi',
        'RESOLVED': '✅ Hal qilindi',
    }
    return statuses.get(status, status)


def format_store_safety(safety: str) -> str:
    statuses = {
        'GREEN': '🟢 Xavfsiz',
        'YELLOW': "🟡 Ehtiyotkor bo'l",
        'RED': '🔴 Xavfli',
    }
    return statuses.get(safety, safety)


def format_store_safety_short(safety: str) -> str:
    icons = {'GREEN': '🟢', 'YELLOW': '🟡', 'RED': '🔴'}
    return icons.get(safety, '⚪')


def format_date(dt) -> str:
    if not dt:
        return ''
    return dt.strftime('%d.%m.%Y')


def format_datetime(dt) -> str:
    if not dt:
        return ''
    return dt.strftime('%d.%m.%Y %H:%M')


def format_money(amount) -> str:
    if amount is None:
        return "0 so'm"
    try:
        val = float(amount)
        return f"{val:,.0f} so'm".replace(',', ' ')
    except (TypeError, ValueError):
        return "0 so'm"


def format_transaction_type(tx_type: str) -> str:
    types = {
        'EARN': '➕ Olindi',
        'SPEND': '➖ Sarflandi',
        'ADJUSTMENT': '🔄 Tuzatish',
    }
    return types.get(tx_type, tx_type)


def format_complaint_confirmation(
    ticket_id: str,
    description: str,
    latitude,
    longitude,
) -> str:
    desc_preview = description[:200] + ('...' if len(description) > 200 else '')
    maps_url = f"https://maps.google.com/?q={latitude},{longitude}"
    return (
        f"✅ <b>Murojaatingiz qabul qilindi!</b>\n\n"
        f"🎫 <b>Murojaat ID:</b> <code>{ticket_id}</code>\n\n"
        f"📦 <b>Mahsulot tavsifi:</b>\n{desc_preview}\n\n"
        f"📍 <b>Do'kon joylashuvi:</b>\n"
        f"<a href='{maps_url}'>{latitude}, {longitude}</a>\n\n"
        f"📊 <b>Holat:</b> ⏳ Moderatsiya kutilmoqda\n\n"
        f"Murojaatingiz moderator tomonidan ko'rib chiqiladi.\n"
        f"Natija bo'yicha sizga Telegram orqali xabar beriladi."
    )


def format_complaint_detail(complaint) -> str:
    maps_url = f"https://maps.google.com/?q={complaint.latitude},{complaint.longitude}"
    text = (
        f"🎫 <b>Murojaat ID:</b> <code>{complaint.ticket_id}</code>\n"
        f"📊 <b>Holat:</b> {format_complaint_status(complaint.status)}\n"
        f"📅 <b>Sana:</b> {format_date(complaint.created_at)}\n\n"
        f"📦 <b>Tavsif:</b>\n{complaint.description}\n\n"
        f"📍 <b>Do'kon joylashuvi:</b>\n<a href='{maps_url}'>Xaritada ko'rish</a>"
    )
    if complaint.moderation_comment:
        text += f"\n\n💬 <b>Moderator izohi:</b>\n{complaint.moderation_comment}"
    return text


def format_store_card(store, distance_km: float | None = None) -> str:
    safety = format_store_safety(store.safety_status)
    icon = format_store_safety_short(store.safety_status)
    
    dist_str = ""
    if distance_km is not None:
        if distance_km < 1.0:
            meters = int(distance_km * 1000)
            dist_str = f"\n📏 Masofa: <b>{meters} metr</b>"
        else:
            dist_str = f"\n📏 Masofa: <b>{distance_km:.1f} km</b>"

    maps_link = ""
    if store.latitude and store.longitude:
        maps_url = f"https://maps.google.com/?q={store.latitude},{store.longitude}"
        maps_link = f"\n🗺 <a href='{maps_url}'>Google Xaritalarda ochish</a>"

    text = (
        f"{icon} <b>{store.name}</b>\n"
        f"📍 {store.address}\n"
        f"🛡 Xavfsizlik: {safety}\n"
        f"⭐ Reyting: {store.rating}/5.0"
        f"{dist_str}"
    )
    if store.phone:
        text += f"\n📞 {store.phone}"
    text += maps_link
    return text


def format_cashback_info(data: dict) -> str:
    lines = [
        "💳 <b>Keshbek balansi</b>\n",
        f"💰 Joriy balans: <b>{format_money(data['balance'])}</b>\n",
        f"📅 Bu oy: <b>+{format_money(data['monthly_earned'])}</b>\n",
        f"📊 Jami olindi: <b>{format_money(data['total_earned'])}</b>",
        f"🔻 Jami sarflandi: <b>{format_money(data['total_spent'])}</b>",
    ]
    recent = data.get('recent_transactions', [])
    if recent:
        lines.append("\n\n📋 <b>So'nggi tranzaksiyalar:</b>")
        for tx in recent[:5]:
            sign = '+' if tx.transaction_type == 'EARN' else '-'
            lines.append(
                f"  {format_transaction_type(tx.transaction_type)} "
                f"{sign}{format_money(tx.amount)} — {tx.description[:40]}"
            )
    return '\n'.join(lines)


def format_my_complaints_list(complaints: list) -> str:
    if not complaints:
        return "Sizda hali murojaatlar yo'q."
    lines = ["📁 <b>Mening murojaatlarim:</b>\n"]
    for c in complaints:
        lines.append(
            f"🎫 <code>{c.ticket_id}</code>\n"
            f"   📊 {format_complaint_status(c.status)}\n"
            f"   📅 {format_date(c.created_at)}\n"
        )
    return '\n'.join(lines)
