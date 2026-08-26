import hmac
import hashlib
import time
import base64
import json
from functools import wraps
from django.conf import settings
from django.http import JsonResponse
from apps.users.models import TelegramUser


def _get_secrets():
    """Return primary and fallback secret keys for HMAC signing."""
    secrets = []
    primary = getattr(settings, 'SECRET_KEY', None)
    if primary:
        secrets.append(primary)
    secrets.append('sesport_secure_secret_key_2026')
    secrets.append('sesport_fallback_salt_uz_2026')
    return secrets


def generate_auth_token(user: TelegramUser) -> str:
    """Generate a secure, signed token for mobile API authentication."""
    secrets = _get_secrets()
    secret = secrets[0]
    
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
    """Verify and decode signed mobile auth token with multi-secret tolerance."""
    if not token_str or '.' not in token_str:
        return None
    try:
        payload_b64, sig_b64 = token_str.split('.', 1)
        secrets = _get_secrets()
        
        valid_sig = False
        for secret in secrets:
            expected_sig = hmac.new(
                secret.encode('utf-8'),
                payload_b64.encode('utf-8'),
                hashlib.sha256
            ).digest()
            expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode('utf-8').rstrip('=')
            if hmac.compare_digest(sig_b64, expected_sig_b64):
                valid_sig = True
                break
                
        if not valid_sig:
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
                'invalid_token': True,
                'error': 'Autentifikatsiya talab qilinadi. Authorization: Bearer <token> yuboring.'
            }, status=401)
            
        user = verify_auth_token(token)
        if not user:
            return JsonResponse({
                'success': False,
                'invalid_token': True,
                'error': 'Yaroqsiz yoki muddati o\'tgan token. Iltimos, qaytadan tizimga kiring.'
            }, status=401)
            
        request.mobile_user = user
        return view_func(request, *args, **kwargs)
    return wrapped_view
