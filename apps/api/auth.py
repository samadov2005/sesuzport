import hmac
import hashlib
import time
import base64
import json
from functools import wraps
from django.conf import settings
from django.http import JsonResponse
from apps.users.models import TelegramUser


def generate_auth_token(user: TelegramUser) -> str:
    """Generate a secure, signed token for mobile API authentication."""
    secret = getattr(settings, 'SECRET_KEY', 'sesport_secure_secret_key_2026')
    payload = {
        'user_id': user.id,
        'telegram_id': user.telegram_id,
        'phone': user.phone_number,
        'role': user.role,
        'exp': int(time.time()) + (365 * 24 * 3600)  # 1 year validity
    }
    payload_json = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode('utf-8').rstrip('=')
    
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_b64.encode('utf-8'),
        hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    return f"{payload_b64}.{sig_b64}"


def verify_auth_token(token_str: str) -> TelegramUser | None:
    """Verify and decode signed mobile auth token."""
    if not token_str or '.' not in token_str:
        return None
    try:
        payload_b64, sig_b64 = token_str.split('.', 1)
        secret = getattr(settings, 'SECRET_KEY', 'sesport_secure_secret_key_2026')
        
        # Verify signature
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            payload_b64.encode('utf-8'),
            hashlib.sha256
        ).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode('utf-8').rstrip('=')
        
        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return None
            
        # Decode payload
        padding = '=' * (4 - len(payload_b64) % 4) if len(payload_b64) % 4 else ''
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode('utf-8')
        payload = json.loads(payload_json)
        
        if payload.get('exp', 0) < int(time.time()):
            return None
            
        return TelegramUser.objects.filter(id=payload.get('user_id'), is_active=True).first()
    except Exception:
        return None


def mobile_auth_required(view_func):
    """Decorator to protect mobile REST API endpoints."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = ''
        if auth_header.startswith('Bearer '):
            token = auth_header[7:].strip()
        elif auth_header.startswith('Token '):
            token = auth_header[6:].strip()
            
        if not token:
            return JsonResponse({
                'success': False,
                'error': 'Autentifikatsiya talab qilinadi. Authorization: Bearer <token> yuboring.'
            }, status=401)
            
        user = verify_auth_token(token)
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Yaroqsiz yoki muddati o\'tgan token.'
            }, status=401)
            
        request.mobile_user = user
        return view_func(request, *args, **kwargs)
    return wrapped_view
