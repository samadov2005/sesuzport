import os
import uuid
import base64
import json
import logging
from pathlib import Path

from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def camera_view(request: HttpRequest) -> HttpResponse:
    """Render the live camera WebApp page for taking on-the-spot photos."""
    response = render(request, 'camera.html', {
        'debug': settings.DEBUG,
    })
    response['X-Frame-Options'] = 'ALLOWALL'
    response['Content-Security-Policy'] = "frame-ancestors *;"
    response['Bypass-Tunnel-Reminder'] = '1'
    return response


@csrf_exempt
def upload_camera_photo(request: HttpRequest) -> JsonResponse:
    """
    API endpoint to receive live camera photo from Telegram WebApp.
    Saves image to MEDIA_ROOT/complaints_camera/ and returns file info.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        image_data = data.get('image', '')

        if not image_data:
            return JsonResponse({'success': False, 'error': 'No image data received'}, status=400)

        # Parse base64
        if 'base64,' in image_data:
            format_header, imgstr = image_data.split('base64,')
        else:
            imgstr = image_data

        decoded_file = base64.b64decode(imgstr)

        # Ensure directory exists
        upload_dir = Path(settings.MEDIA_ROOT) / 'complaints_camera'
        upload_dir.mkdir(parents=True, exist_ok=True)

        filename = f"cam_{uuid.uuid4().hex[:12]}.jpg"
        file_path = upload_dir / filename

        with open(file_path, 'wb') as f:
            f.write(decoded_file)

        relative_url = f"{settings.MEDIA_URL}complaints_camera/{filename}"
        
        return JsonResponse({
            'success': True,
            'file_name': filename,
            'file_path': str(file_path.resolve()),
            'file_url': relative_url,
        })

    except Exception as e:
        logger.error(f"Error processing camera upload: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
