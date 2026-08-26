import json
import base64
import math
import uuid
import os
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings

from apps.users.models import TelegramUser, UserRole
from apps.complaints.models import Complaint, ComplaintStatus
from apps.stores.models import Store, SafetyStatus
from apps.cashback.models import CashbackAccount, CashbackTransaction
from apps.rights.models import ConsumerRight
from apps.support.models import SupportConfiguration
from .auth import generate_auth_token, mobile_auth_required


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
            # Deterministic positive integer based on phone digits
            digits = ''.join(c for c in phone if c.isdigit())
            telegram_id = int(digits[-9:]) if len(digits) >= 9 else int(uuid.uuid4().int % 1000000000)
            while TelegramUser.objects.filter(telegram_id=telegram_id).exists():
                telegram_id += 1

        first_name = full_name.split()[0] if full_name else 'Foydalanuvchi'
        last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''

        user = TelegramUser.objects.create(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            full_name_input=full_name or first_name,
            phone_number=phone,
            is_registered=True,
            language=language if language in ['uz', 'ru'] else 'uz',
            role=UserRole.CONSUMER,
            is_active=True
        )
    else:
        # Update user data
        if full_name:
            user.full_name_input = full_name
        if language in ['uz', 'ru']:
            user.language = language
        user.is_registered = True
        user.last_activity = timezone.now()
        user.save()

    token = generate_auth_token(user)

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
        }
    })


@require_http_methods(["GET"])
@mobile_auth_required
def get_user_profile(request):
    """Get current user's profile and stats."""
    user = request.mobile_user
    
    cashback_account = CashbackAccount.objects.filter(user=user).first()
    balance = float(cashback_account.balance) if cashback_account else 0.0
    
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

    # Save photo or assign unique photo identifier
    photo_file_id = f"MOBILE_IMG_{uuid.uuid4().hex[:12].upper()}"
    
    if image_base64:
        try:
            if ',' in image_base64:
                image_base64 = image_base64.split(',', 1)[1]
            image_bytes = base64.b64decode(image_base64)
            
            # Save temporary file if archive forward is configured
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            temp_filename = f"{photo_file_id}.jpg"
            temp_filepath = os.path.join(settings.MEDIA_ROOT, temp_filename)
            with open(temp_filepath, 'wb') as f:
                f.write(image_bytes)
                
            photo_file_id = f"photo_{temp_filename}"
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
    
    results = []
    for c in complaints:
        results.append({
            'id': c.id,
            'ticket_id': c.ticket_id,
            'description': c.description,
            'status': c.status,
            'status_display': c.get_status_display(),
            'moderation_comment': c.moderation_comment or '',
            'latitude': float(c.latitude),
            'longitude': float(c.longitude),
            'created_at': c.created_at.strftime('%d.%m.%Y %H:%M'),
            'resolved_at': c.resolved_at.strftime('%d.%m.%Y %H:%M') if c.resolved_at else None,
        })
        
    return JsonResponse({
        'success': True,
        'count': len(results),
        'complaints': results
    })


@require_http_methods(["GET"])
@mobile_auth_required
def get_complaint_detail(request, ticket_id):
    """Get single complaint detail by ticket_id."""
    user = request.mobile_user
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
            'moderation_comment': complaint.moderation_comment or '',
            'latitude': float(complaint.latitude),
            'longitude': float(complaint.longitude),
            'created_at': complaint.created_at.strftime('%d.%m.%Y %H:%M'),
            'resolved_at': complaint.resolved_at.strftime('%d.%m.%Y %H:%M') if complaint.resolved_at else None,
        }
    })


# ──────────────────────────────────────────────────────────────────────────────
# 3. STORES (DO'KONLAR & XARITA)
# ──────────────────────────────────────────────────────────────────────────────

def _calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula to compute distance in km between two GPS coordinates."""
    r = 6371.0  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 2)


@require_http_methods(["GET"])
def get_stores_list(request):
    """List stores with optional status filter, search, and nearby distance calculation."""
    qs = Store.objects.filter(is_active=True)
    
    status_filter = request.GET.get('status')
    if status_filter in ['GREEN', 'YELLOW', 'RED']:
        qs = qs.filter(safety_status=status_filter)
        
    query = request.GET.get('q', '').strip()
    if query:
        qs = qs.filter(name__icontains=query) | qs.filter(address__icontains=query)
        
    user_lat = request.GET.get('lat')
    user_lon = request.GET.get('lng') or request.GET.get('lon')
    
    stores_data = []
    for s in qs:
        lat = float(s.latitude) if s.latitude else None
        lon = float(s.longitude) if s.longitude else None
        
        distance_km = None
        if user_lat and user_lon and lat and lon:
            try:
                distance_km = _calculate_distance(float(user_lat), float(user_lon), lat, lon)
            except Exception:
                pass
                
        stores_data.append({
            'id': s.id,
            'name': s.name,
            'address': s.address,
            'latitude': lat,
            'longitude': lon,
            'phone': s.phone or '',
            'rating': float(s.rating),
            'safety_status': s.safety_status,
            'safety_status_display': s.get_safety_status_display(),
            'distance_km': distance_km
        })
        
    if user_lat and user_lon:
        stores_data.sort(key=lambda x: (x['distance_km'] is None, x['distance_km'] or 9999))
        
    return JsonResponse({
        'success': True,
        'count': len(stores_data),
        'stores': stores_data
    })


# ──────────────────────────────────────────────────────────────────────────────
# 4. CASHBACK (KESHBEK)
# ──────────────────────────────────────────────────────────────────────────────

@require_http_methods(["GET"])
@mobile_auth_required
def get_cashback_info(request):
    """Get user's cashback balance and transaction history."""
    user = request.mobile_user
    account, _ = CashbackAccount.objects.get_or_create(user=user)
    
    transactions = CashbackTransaction.objects.filter(account=account).order_by('-created_at')[:20]
    
    tx_list = []
    for tx in transactions:
        tx_list.append({
            'id': tx.id,
            'amount': float(tx.amount),
            'type': tx.transaction_type,
            'description': tx.description,
            'created_at': tx.created_at.strftime('%d.%m.%Y %H:%M'),
        })
        
    return JsonResponse({
        'success': True,
        'balance': float(account.balance),
        'total_earned': float(account.total_earned),
        'total_spent': float(account.total_spent),
        'transactions': tx_list
    })


# ──────────────────────────────────────────────────────────────────────────────
# 5. RIGHTS & SUPPORT (HUQUQLAR VA YORDAM)
# ──────────────────────────────────────────────────────────────────────────────

@require_http_methods(["GET"])
def get_rights_list(request):
    """List consumer rights articles."""
    rights = ConsumerRight.objects.filter(is_active=True).order_by('order')
    
    items = []
    for r in rights:
        items.append({
            'id': r.id,
            'title': r.title,
            'content': r.content,
            'category': r.category or 'Umumiy',
            'order': r.order,
        })
        
    return JsonResponse({
        'success': True,
        'count': len(items),
        'rights': items
    })


@require_http_methods(["GET"])
def get_support_info(request):
    """Get support contact details and FAQ."""
    support = SupportConfiguration.objects.filter(is_active=True).first()
    
    phone = support.phone if support and support.phone else "+998712000000"
    email = support.email if support and support.email else "info@sesport.uz"
    tg_admin = support.telegram_username if support and support.telegram_username else "sesport_admin"
    hours = support.working_hours if support and support.working_hours else "09:00 - 18:00 (Du-Jum)"
    
    faq_items = [
        {
            'question': "Shikoyat qanday yuboriladi va ko'rib chiqiladi?",
            'answer': "1. Ilovada «Tezkor Shikoyat» tugmasini bosing.\n2. Muammoni tanlang.\n3. Jonli kamera orqali rasmga oling.\n4. GPS lokatsiyani tasdiqlang.\nMurojaat darhol SES nazoratiga o'tadi."
        },
        {
            'question': "Keshbek qanday ishlaydi?",
            'answer': "Sifatsiz yoki muddati o'tgan mahsulotlar bo'yicha asosli shikoyat yuborgan va tasdiqlangan fuqarolarga rag'batlantiruvchi keshbek beriladi."
        },
        {
            'question': "Do'konlar xavfsizlik reytingi (Yashil/Sariq/Qizil) nima?",
            'answer': "Yashil — to'liq xavfsiz va sertifikatlangan.\nSariq — kichik kamchiliklar qayd etilgan.\nQizil — muddati o'tgan mahsulotlar yoki qoidabuzarliklar aniqlangan."
        }
    ]
    
    return JsonResponse({
        'success': True,
        'support': {
            'phone': phone,
            'short_number': '1080',
            'email': email,
            'telegram_admin': tg_admin,
            'developer': 'samadov2005',
            'working_hours': hours,
            'faq': faq_items
        }
    })
