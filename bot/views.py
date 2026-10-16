from __future__ import annotations
import json
import logging
import os
from asgiref.sync import sync_to_async
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from aiogram.types import Update

from bot.dispatcher import get_bot, get_dispatcher

logger = logging.getLogger(__name__)


@csrf_exempt
async def bot_webhook_view(request):
    """
    Telegram webhook update handler.
    Telegram sends updates here via HTTPS POST.
    Native async Django view for optimal throughput.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST allowed")

    # Optional secret verification
    secret = os.getenv('WEBHOOK_SECRET', '').strip()
    if secret:
        token_header = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
        if token_header != secret:
            logger.warning("Telegram webhook: invalid secret token header")
            return HttpResponseForbidden("Forbidden")

    try:
        body = request.body.decode('utf-8')
        if not body:
            return JsonResponse({'ok': False, 'error': 'Empty body'}, status=400)
        data = json.loads(body)
    except Exception as exc:
        logger.error(f"Telegram webhook JSON parse error: {exc}")
        return HttpResponseBadRequest("Invalid JSON")

    bot = get_bot()
    dp = get_dispatcher()

    try:
        update = Update.model_validate(data, context={"bot": bot})
        await dp.feed_update(bot=bot, update=update)
        return JsonResponse({'ok': True})
    except Exception as exc:
        logger.exception(f"Error processing Telegram update in webhook: {exc}")
        # Always return 200/OK to Telegram so it doesn't repeatedly hammer the server
        return JsonResponse({'ok': False, 'error': str(exc)})


@sync_to_async
def _check_database():
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            return True, None
    except Exception as exc:
        return False, str(exc)


async def bot_status_view(request):
    """Diagnostic view to check bot and webhook status."""
    db_ok, db_err = await _check_database()
    bot = get_bot()

    try:
        me = await bot.get_me()
        webhook_info = await bot.get_webhook_info()
        tele_info = {
            'bot': {
                'id': me.id,
                'username': me.username,
                'first_name': me.first_name,
            },
            'webhook': {
                'url': webhook_info.url,
                'has_custom_certificate': webhook_info.has_custom_certificate,
                'pending_update_count': webhook_info.pending_update_count,
                'last_error_date': str(webhook_info.last_error_date) if webhook_info.last_error_date else None,
                'last_error_message': webhook_info.last_error_message,
            }
        }
    except Exception as exc:
        tele_info = {'error': str(exc)}

    return JsonResponse({
        'status': 'healthy' if db_ok else 'unhealthy',
        'database': {'connected': db_ok, 'error': db_err},
        'telegram': tele_info,
        'environment': {
            'use_webhook': os.getenv('USE_WEBHOOK', 'false'),
            'webapp_url': os.getenv('WEBAPP_URL', os.getenv('RENDER_EXTERNAL_URL', 'https://sesuzport.onrender.com')),
        }
    })


async def bot_set_webhook_view(request):
    """Helper to register Telegram webhook to this server URL."""
    base_url = (os.getenv('WEBAPP_URL') or os.getenv('RENDER_EXTERNAL_URL') or 'https://sesuzport.onrender.com').strip().rstrip('/')
    if not base_url.startswith('http'):
        base_url = f"https://{base_url}"
    webhook_url = f"{base_url}/bot/webhook/"
    secret = os.getenv('WEBHOOK_SECRET', '').strip() or None

    bot = get_bot()

    try:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=secret,
            drop_pending_updates=False,
            allowed_updates=['message', 'callback_query']
        )
        info = await bot.get_webhook_info()
        return JsonResponse({
            'success': True,
            'message': f"Webhook successfully registered to {webhook_url}",
            'webhook_info': {
                'url': info.url,
                'pending_update_count': info.pending_update_count,
            }
        })
    except Exception as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=500)


async def bot_delete_webhook_view(request):
    """Helper to delete Telegram webhook and switch back to long-polling."""
    bot = get_bot()

    try:
        await bot.delete_webhook(drop_pending_updates=False)
        info = await bot.get_webhook_info()
        return JsonResponse({
            'success': True,
            'message': "Webhook successfully deleted. Long-polling can now be used.",
            'webhook_info': {
                'url': info.url,
            }
        })
    except Exception as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=500)
