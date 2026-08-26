import json
import base64
import math
import uuid
import os
import urllib.request
import urllib.parse
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Count

from apps.users.models import TelegramUser, UserRole
from apps.complaints.models import Complaint, ComplaintStatus
from apps.stores.models import Store, SafetyStatus
from apps.cashback.models import CashbackAccount, CashbackTransaction, TransactionType
from apps.rights.models import ConsumerRight
from apps.support.models import SupportConfiguration
from .auth import generate_auth_token, mobile_auth_required


# ──────────────────────────────────────────────────────────────────────────────
# TELEGRAM NOTIFIER HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def send_telegram_photo(bot_token: str, chat_id: str | int, photo_bytes: bytes, caption: str):
    """Send photo to Telegram chat or channel using standard urllib multipart."""
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    body = bytearray()
    
    # chat_id field
    body.extend(f"--{boundary}\r\n".encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode('utf-8'))
    
    # caption field
    body.extend(f"--{boundary}\r\n".encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode('utf-8'))
    
    # parse_mode field
    body.extend(f"--{boundary}\r\n".encode('utf-8'))
    body.extend(b'Content-Disposition: form-data; name="parse_mode"\r\n\r\nHTML\r\n')
    
    # photo file field
    body.extend(f"--{boundary}\r\n".encode('utf-8'))
    body.extend(b'Content-Disposition: form-data; name="photo"; filename="complaint.jpg"\r\n')
    body.extend(b'Content-Type: image/jpeg\r\n\r\n')
    body.extend(photo_bytes)
    body.extend(b'\r\n')
    
    body.extend(f"--{boundary}--\r\n".encode('utf-8'))
    
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body)),
            'User-Agent': 'SESPORT-Backend/1.0',
        },
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        if result.get('ok'):
            photos = result.get('result', {}).get('photo', [])
            if photos:
                return photos[-1].get('file_id')
    return None


def send_telegram_message(bot_token: str, chat_id: str | int, text: str):
    """Send HTML text message to Telegram chat/channel."""
    data = json.dumps({'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}).encode('utf-8')
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=data,
        headers={'Content-Type': 'application/json', 'User-Agent': 'SESPORT-Backend/1.0'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))


def notify_telegram_complaint(complaint: Complaint, photo_bytes: bytes | None = None):
    """Notify Telegram Archive Channel, Admins, and User about new complaint."""
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        return

    user_name = complaint.user.full_name_input or complaint.user.full_name or "Noma'lum"
    user_phone = complaint.user.phone_number or "Noma'lum"
    
    caption = (
        f"🛡 <b>#Yangi_Shikoyat | SESPORT Mobil Ilova</b>\n\n"
        f"🎫 <b>Chipta ID:</b> <code>#{complaint.ticket_id}</code>\n"
        f"👤 <b>Murojaatchi:</b> {user_name}\n"
        f"📞 <b>Telefon:</b> <code>{user_phone}</code>\n"
        f"📝 <b>Holat:</b> {complaint.description}\n"
        f"📍 <b>GPS Koordinata:</b> <code>{complaint.latitude}, {complaint.longitude}</code>\n"
        f"🗺 <a href=\"https://maps.google.com/?q={complaint.latitude},{complaint.longitude}\">Google Xaritada ochish</a>\n"
        f"⏰ <b>Vaqt:</b> {complaint.created_at.strftime('%d.%m.%Y %H:%M')}"
    )

    archive_channel = os.getenv('ARCHIVE_CHANNEL_ID') or os.getenv('MEDIA_CHANNEL_ID')
    
    # 1. Forward to Archive Channel
    if archive_channel:
        try:
            if photo_bytes:
                file_id = send_telegram_photo(bot_token, archive_channel, photo_bytes, caption)
                if file_id and not complaint.photo_file_id:
                    complaint.photo_file_id = file_id
                    complaint.save(update_fields=['photo_file_id'])
            else:
                send_telegram_message(bot_token, archive_channel, caption)
        except Exception as e:
            print(f"[Telegram Notify Channel Error] {e}")

    # 2. Forward to Telegram Admins
    admin_users = TelegramUser.objects.filter(role__in=[UserRole.ADMIN, UserRole.MODERATOR]).exclude(telegram_id=None)
    for admin in admin_users:
        try:
            if photo_bytes:
                send_telegram_photo(bot_token, admin.telegram_id, photo_bytes, caption)
            else:
                send_telegram_message(bot_token, admin.telegram_id, caption)
        except Exception:
            pass

    # 3. Confirmation to the user if registered via Telegram
    if complaint.user.telegram_id and complaint.user.telegram_id > 100000:
        user_msg = (
            f"✅ <b>Murojaatingiz qabul qilindi!</b>\n\n"
            f"🎫 Chipta raqami: <code>#{complaint.ticket_id}</code>\n"
            f"Inspektorlar ko'rib chiqishni boshladi. Holat o'zgarganda sizga xabar beriladi."
        )
        try:
            send_telegram_message(bot_token, complaint.user.telegram_id, user_msg)
        except Exception:
            pass


# ──────────────────────────────────────────────────────────────────────────────
# 1. AUTH & PROFILE
# ──────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def auth_login_or_register(request):
    """Mobile Login or Registration by phone number."""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Yaroqsiz JSON ma\'lumot.'}, status=400)
        
    phone = str(data.get('phone_number', '')).strip().replace(' ', '').replace('-', '')
    full_name = str(data.get('full_name', '')).strip()
    language = str(data.get('language', 'uz')).strip()
    telegram_id = data.get('telegram_id')

    if not phone or len(phone) < 9:
        return JsonResponse({
            'success': False,
            'error': 'To\'g\'ri telefon raqam kiritilishi shart (masalan: +998901234567).'
        }, status=400)

    # Normalize phone
    if not phone.startswith('+') and phone.startswith('998'):
        phone = '+' + phone

    # Search existing user by phone or telegram_id
    user = TelegramUser.objects.filter(phone_number=phone).first()
    
    if not user and telegram_id:
        user = TelegramUser.objects.filter(telegram_id=telegram_id).first()

    if not user:
        # Create virtual telegram_id for mobile users if not provided
        if not telegram_id:
            digits = ''.join(c for c in phone if c.isdigit())
            telegram_id = int(digits[-9:]) if len(digits) >= 9 else int(uuid.uuid4().int % 1000000000)

        user = TelegramUser.objects.create(
            telegram_id=telegram_id,
            phone_number=phone,
            first_name=full_name or "Foydalanuvchi",
            full_name_input=full_name or "Foydalanuvchi",
            language=language or "uz",
            role=UserRole.CONSUMER
        )
        # Create cashback account
        CashbackAccount.objects.get_or_create(user=user)
    else:
        if full_name and not user.full_name_input:
            user.full_name_input = full_name
            user.save(update_fields=['full_name_input'])

    token = generate_auth_token(user)
    cashback_acc, _ = CashbackAccount.objects.get_or_create(user=user)

    return JsonResponse({
        'success': True,
        'token': token,
        'user': {
            'id': user.id,
            'telegram_id': user.telegram_id,
            'full_name': user.full_name_input or user.full_name,
            'phone_number': user.phone_number,
            'language': user.language,
            'role': user.role,
            'is_admin': user.role in [UserRole.ADMIN, UserRole.MODERATOR],
            'cashback_balance': float(cashback_acc.balance),
        }
    })


@require_http_methods(["GET"])
@mobile_auth_required
def get_user_profile(request):
    """Return user profile, role, cashback balance and activity stats."""
    user = request.mobile_user
    cashback_acc, _ = CashbackAccount.objects.get_or_create(user=user)
    balance = float(cashback_acc.balance)

    total_complaints = Complaint.objects.filter(user=user).count()
    resolved_complaints = Complaint.objects.filter(user=user, status=ComplaintStatus.RESOLVED).count()

    return JsonResponse({
        'success': True,
        'user': {
            'id': user.id,
            'telegram_id': user.telegram_id,
            'full_name': user.full_name_input or user.full_name,
            'phone_number': user.phone_number,
            'language': user.language,
            'role': user.role,
            'is_admin': user.role in [UserRole.ADMIN, UserRole.MODERATOR],
            'cashback_balance': balance,
            'stats': {
                'total_complaints': total_complaints,
                'resolved_complaints': resolved_complaints,
            }
        }
    })


# ──────────────────────────────────────────────────────────────────────────────
# 2. COMPLAINTS (SHIKOYATLAR)
# ──────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
@mobile_auth_required
def create_complaint(request):
    """Submit a complaint with live camera photo, GPS location, and reason."""
    user = request.mobile_user
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Noto\'g\'ri JSON ma\'lumot.'}, status=400)
        
    description = str(data.get('description', '')).strip()
    image_base64 = data.get('image', '')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not description or len(description) < 5:
        return JsonResponse({
            'success': False,
            'error': 'Iltimos, murojaat sababini batafsil yozing (kamida 5 ta belgi).'
        }, status=400)
        
    if latitude is None or longitude is None:
        return JsonResponse({
            'success': False,
            'error': 'GPS lokatsiya koordinatalari (kenglik va uzunlik) talab qilinadi.'
        }, status=400)

    try:
        lat_dec = Decimal(str(latitude))
        lng_dec = Decimal(str(longitude))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Koordinatalar formati noto\'g\'ri.'}, status=400)

    photo_file_id = f"MOBILE_IMG_{uuid.uuid4().hex[:12].upper()}"
    image_bytes = None
    
    if image_base64:
        try:
            if ',' in image_base64:
                image_base64 = image_base64.split(',', 1)[1]
            image_bytes = base64.b64decode(image_base64)
            
            # Save local copy
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            temp_filename = f"{photo_file_id}.jpg"
            temp_filepath = os.path.join(settings.MEDIA_ROOT, temp_filename)
            with open(temp_filepath, 'wb') as f:
                f.write(image_bytes)
        except Exception:
            pass

    complaint = Complaint.objects.create(
        user=user,
        description=description,
        photo_file_id=photo_file_id,
        latitude=lat_dec,
        longitude=lng_dec,
        status=ComplaintStatus.PENDING
    )

    # Trigger Telegram Channel & Bot Forwarding
    try:
        notify_telegram_complaint(complaint, image_bytes)
    except Exception as notify_err:
        print(f"[Complaint Notify Error] {notify_err}")

    return JsonResponse({
        'success': True,
        'ticket_id': complaint.ticket_id,
        'message': 'Murojaatingiz muvaffaqiyatli qabul qilindi va ko\'rib chiqilmoqda.',
        'complaint': {
            'id': complaint.id,
            'ticket_id': complaint.ticket_id,
            'status': complaint.status,
            'status_display': complaint.get_status_display(),
            'created_at': complaint.created_at.strftime('%d.%m.%Y %H:%M'),
        }
    })


@require_http_methods(["GET"])
@mobile_auth_required
def get_my_complaints(request):
    """List complaints submitted by current user."""
    user = request.mobile_user
    complaints = Complaint.objects.filter(user=user).order_by('-created_at')

    data = []
    for c in complaints:
        data.append({
            'id': c.id,
            'ticket_id': c.ticket_id,
            'description': c.description,
            'status': c.status,
            'status_display': c.get_status_display(),
            'photo_file_id': c.photo_file_id or '',
            'latitude': float(c.latitude),
            'longitude': float(c.longitude),
            'moderation_comment': c.moderation_comment or '',
            'created_at': c.created_at.strftime('%d.%m.%Y %H:%M'),
            'updated_at': c.updated_at.strftime('%d.%m.%Y %H:%M'),
        })

    return JsonResponse({'success': True, 'count': len(data), 'complaints': data})


@require_http_methods(["GET"])
@mobile_auth_required
def get_complaint_detail(request, ticket_id):
    """Get single complaint status and inspector notes."""
    user = request.mobile_user
    
    # Allow admins to view any complaint, users to view their own
    if user.role in [UserRole.ADMIN, UserRole.MODERATOR]:
        complaint = Complaint.objects.filter(ticket_id=ticket_id).first()
    else:
        complaint = Complaint.objects.filter(ticket_id=ticket_id, user=user).first()

    if not complaint:
        return JsonResponse({'success': False, 'error': 'Murojaat topilmadi.'}, status=404)

    return JsonResponse({
        'success': True,
        'complaint': {
            'id': complaint.id,
            'ticket_id': complaint.ticket_id,
            'description': complaint.description,
            'status': complaint.status,
            'status_display': complaint.get_status_display(),
            'photo_file_id': complaint.photo_file_id or '',
            'latitude': float(complaint.latitude),
            'longitude': float(complaint.longitude),
            'moderation_comment': complaint.moderation_comment or '',
            'user': {
                'full_name': complaint.user.full_name_input or complaint.user.full_name,
                'phone_number': complaint.user.phone_number,
            },
            'created_at': complaint.created_at.strftime('%d.%m.%Y %H:%M'),
            'updated_at': complaint.updated_at.strftime('%d.%m.%Y %H:%M'),
        }
    })


# ──────────────────────────────────────────────────────────────────────────────
# 3. STORES & SAFETY RATINGS
# ──────────────────────────────────────────────────────────────────────────────

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance between two points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


@require_http_methods(["GET"])
def get_stores_list(request):
    """List stores with safety ratings, search, and distance calculator."""
    status = request.GET.get('status')
    query = request.GET.get('q', '').strip()
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')

    stores = Store.objects.filter(is_active=True)

    if status and status in [SafetyStatus.GREEN, SafetyStatus.YELLOW, SafetyStatus.RED]:
        stores = stores.filter(safety_status=status)

    if query:
        stores = stores.filter(name__icontains=query) | stores.filter(address__icontains=query)

    data = []
    u_lat = float(user_lat) if user_lat else None
    u_lng = float(user_lng) if user_lng else None

    for s in stores:
        distance_km = None
        s_lat = float(s.latitude) if s.latitude else None
        s_lng = float(s.longitude) if s.longitude else None

        if u_lat and u_lng and s_lat and s_lng:
            distance_km = haversine_distance(u_lat, u_lng, s_lat, s_lng)

        data.append({
            'id': s.id,
            'name': s.name,
            'address': s.address,
            'safety_status': s.safety_status,
            'safety_status_display': s.get_safety_status_display(),
            'rating': float(s.rating) if s.rating else 5.0,
            'latitude': s_lat,
            'longitude': s_lng,
            'distance_km': distance_km,
            'phone': s.phone or '',
        })

    if u_lat and u_lng:
        data.sort(key=lambda x: x['distance_km'] if x['distance_km'] is not None else 999999)

    return JsonResponse({'success': True, 'count': len(data), 'stores': data})


# ──────────────────────────────────────────────────────────────────────────────
# 4. CASHBACK & REWARDS
# ──────────────────────────────────────────────────────────────────────────────

@require_http_methods(["GET"])
@mobile_auth_required
def get_cashback_info(request):
    """Return user's cashback balance and transaction history."""
    user = request.mobile_user
    cashback_acc, _ = CashbackAccount.objects.get_or_create(user=user)

    transactions = CashbackTransaction.objects.filter(account=cashback_acc).order_by('-created_at')[:30]

    tx_data = []
    for tx in transactions:
        tx_data.append({
            'id': tx.id,
            'amount': float(tx.amount),
            'type': tx.transaction_type,
            'description': tx.description or '',
            'created_at': tx.created_at.strftime('%d.%m.%Y %H:%M'),
        })

    return JsonResponse({
        'success': True,
        'balance': float(cashback_acc.balance),
        'total_earned': float(cashback_acc.total_earned),
        'total_spent': float(cashback_acc.total_spent),
        'transactions': tx_data,
    })


# ──────────────────────────────────────────────────────────────────────────────
# 5. RIGHTS & SUPPORT
# ──────────────────────────────────────────────────────────────────────────────

@require_http_methods(["GET"])
def get_rights_list(request):
    """List consumer rights articles."""
    rights = ConsumerRight.objects.all().order_by('order', 'id')
    data = []
    for r in rights:
        data.append({
            'id': r.id,
            'title': r.title,
            'category': r.category,
            'content': r.content,
            'order': r.order,
        })
    return JsonResponse({'success': True, 'count': len(data), 'rights': data})


@require_http_methods(["GET"])
def get_support_info(request):
    """Return support contact info and FAQs."""
    support_cfg = SupportConfiguration.objects.first()

    phone = support_cfg.hotline_phone if support_cfg else '1080'
    admin_contact = os.getenv('SUPPORT_TELEGRAM_ADMIN', 'sesport_admin')
    dev_contact = 'samadov2005'

    faq_list = [
        {
            'question': 'Shikoyat yuborishda nimalarga e\'tibor berish kerak?',
            'answer': 'Qoidabuzarlik yoki muddati o\'tgan mahsulotni to\'g\'ridan-to\'g\'ri jonli kamera orqali rasmga oling va GPS joylashuvni aniq belgilang.'
        },
        {
            'question': 'Keshbek ballari qachon beriladi?',
            'answer': 'Yuborgan shikoyatingiz inspektorlar tomonidan tekshirilib, o\'rinli deb topilgach, balansingizga avtomatik rag\'batlantiruvchi ballar qo\'shiladi.'
        },
        {
            'question': 'Do\'konlarning yashil va qizil reytingi nimani bildiradi?',
            'answer': '🟢 Yashil — Sanitariya talablariga to\'liq javob beruvchi xavfsiz maskan. 🔴 Qizil — Qoidabuzarliklar aniqlangan va nazoratdagi savdo shoxobchasi.'
        }
    ]

    return JsonResponse({
        'success': True,
        'support': {
            'phone': phone,
            'telegram_admin': admin_contact,
            'developer': dev_contact,
            'faq': faq_list,
        }
    })


# ──────────────────────────────────────────────────────────────────────────────
# 6. ADMIN & MODERATION DASHBOARD API
# ──────────────────────────────────────────────────────────────────────────────

@require_http_methods(["GET"])
@mobile_auth_required
def get_admin_stats(request):
    """Return platform statistics for admins/moderators."""
    user = request.mobile_user
    if user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
        return JsonResponse({'success': False, 'error': 'Ruxsat berilmagan.'}, status=403)

    total_complaints = Complaint.objects.count()
    pending = Complaint.objects.filter(status=ComplaintStatus.PENDING).count()
    under_review = Complaint.objects.filter(status=ComplaintStatus.UNDER_REVIEW).count()
    resolved = Complaint.objects.filter(status=ComplaintStatus.RESOLVED).count()
    rejected = Complaint.objects.filter(status=ComplaintStatus.REJECTED).count()
    total_users = TelegramUser.objects.count()
    total_stores = Store.objects.count()

    return JsonResponse({
        'success': True,
        'stats': {
            'total_complaints': total_complaints,
            'pending': pending,
            'under_review': under_review,
            'resolved': resolved,
            'rejected': rejected,
            'total_users': total_users,
            'total_stores': total_stores,
        }
    })


@require_http_methods(["GET"])
@mobile_auth_required
def get_admin_complaints(request):
    """List complaints for moderation filterable by status."""
    user = request.mobile_user
    if user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
        return JsonResponse({'success': False, 'error': 'Ruxsat berilmagan.'}, status=403)

    status = request.GET.get('status')
    complaints = Complaint.objects.select_related('user').order_by('-created_at')

    if status and status in [ComplaintStatus.PENDING, ComplaintStatus.UNDER_REVIEW, ComplaintStatus.APPROVED, ComplaintStatus.RESOLVED, ComplaintStatus.REJECTED]:
        complaints = complaints.filter(status=status)

    data = []
    for c in complaints[:50]:
        data.append({
            'id': c.id,
            'ticket_id': c.ticket_id,
            'description': c.description,
            'status': c.status,
            'status_display': c.get_status_display(),
            'photo_file_id': c.photo_file_id or '',
            'latitude': float(c.latitude),
            'longitude': float(c.longitude),
            'moderation_comment': c.moderation_comment or '',
            'user': {
                'full_name': c.user.full_name_input or c.user.full_name,
                'phone_number': c.user.phone_number,
                'telegram_id': c.user.telegram_id,
            },
            'created_at': c.created_at.strftime('%d.%m.%Y %H:%M'),
            'updated_at': c.updated_at.strftime('%d.%m.%Y %H:%M'),
        })

    return JsonResponse({'success': True, 'complaints': data})


@csrf_exempt
@require_http_methods(["POST"])
@mobile_auth_required
def moderate_complaint(request, complaint_id):
    """Moderate a complaint (Resolve, Under Review, Reject, or Award Points)."""
    user = request.mobile_user
    if user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
        return JsonResponse({'success': False, 'error': 'Ruxsat berilmagan.'}, status=403)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Noto\'g\'ri JSON.'}, status=400)

    new_status = data.get('status')
    comment = str(data.get('moderation_comment', '')).strip()
    points = data.get('points', 0)

    valid_statuses = [
        ComplaintStatus.PENDING,
        ComplaintStatus.UNDER_REVIEW,
        ComplaintStatus.APPROVED,
        ComplaintStatus.RESOLVED,
        ComplaintStatus.REJECTED
    ]

    if new_status not in valid_statuses:
        return JsonResponse({'success': False, 'error': 'Noto\'g\'ri status.'}, status=400)

    complaint = Complaint.objects.filter(id=complaint_id).first()
    if not complaint:
        return JsonResponse({'success': False, 'error': 'Murojaat topilmadi.'}, status=404)

    complaint.status = new_status
    if comment:
        complaint.moderation_comment = comment
    complaint.save(update_fields=['status', 'moderation_comment', 'updated_at'])

    # Award Cashback if resolved
    if new_status == ComplaintStatus.RESOLVED and points and points > 0:
        cashback_acc, _ = CashbackAccount.objects.get_or_create(user=complaint.user)
        cashback_acc.balance += Decimal(str(points))
        cashback_acc.total_earned += Decimal(str(points))
        cashback_acc.save(update_fields=['balance', 'total_earned', 'updated_at'])

        CashbackTransaction.objects.create(
            account=cashback_acc,
            amount=Decimal(str(points)),
            transaction_type=TransactionType.EARNED,
            description=f"#{complaint.ticket_id} murojaati tasdiqlanganligi uchun rag'batlantirish"
        )

    # Send update message to user via Telegram if available
    bot_token = os.getenv('BOT_TOKEN')
    if bot_token and complaint.user.telegram_id and complaint.user.telegram_id > 100000:
        status_name = complaint.get_status_display()
        msg_text = (
            f"🔔 <b>Murojaatingiz yangilandi!</b>\n\n"
            f"🎫 Chipta: <code>#{complaint.ticket_id}</code>\n"
            f"📊 Yangi holat: <b>{status_name}</b>\n"
        )
        if comment:
            msg_text += f"💬 Inspektor izohi: <i>{comment}</i>\n"
        if new_status == ComplaintStatus.RESOLVED and points and points > 0:
            msg_text += f"🎁 Sizga <b>+{points} ball</b> keshbek hisoblandi!"

        try:
            send_telegram_message(bot_token, complaint.user.telegram_id, msg_text)
        except Exception:
            pass

    return JsonResponse({
        'success': True,
        'message': f"Murojaat #{complaint.ticket_id} muvaffaqiyatli yangilandi.",
        'complaint': {
            'id': complaint.id,
            'ticket_id': complaint.ticket_id,
            'status': complaint.status,
            'status_display': complaint.get_status_display(),
            'moderation_comment': complaint.moderation_comment or '',
        }
    })
