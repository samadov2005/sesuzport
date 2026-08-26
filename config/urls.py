from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import RedirectView

# Import custom admin site and auto-register all models to it
from config.admin import sesport_admin
from apps.complaints.views import camera_view, upload_camera_photo

# Auto-discover and register all models from the default admin into sesport_admin
admin.autodiscover()
for model, model_admin in admin.site._registry.items():
    try:
        sesport_admin.register(model, type(model_admin))
    except Exception:
        pass  # Already registered


def healthz(request):
    """Docker healthcheck uchun yengil liveness tekshiruvi (DB'ga tegmaydi)."""
    return HttpResponse('ok', content_type='text/plain')


urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('healthz/', healthz, name='healthz'),
    path('health/', healthz),  # alias
    path('admin/', sesport_admin.urls),
    path('camera/', camera_view, name='live_camera'),
    path('api/upload-camera/', upload_camera_photo, name='upload_camera_photo'),
    path('api/v1/', include('apps.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

elif getattr(settings, 'SERVE_MEDIA_FILES', False):
    import posixpath
    from django.urls import re_path
    from django.views.static import serve as _django_serve

    _RISKY_SUFFIXES = (
        '.html', '.htm', '.xhtml', '.xml', '.svg', '.js', '.mjs',
        '.php', '.py', '.pl', '.cgi', '.sh', '.jsp', '.asp', '.aspx',
    )

    def media_serve(request, path):
        response = _django_serve(request, path, document_root=settings.MEDIA_ROOT)
        response['X-Content-Type-Options'] = 'nosniff'
        response['Content-Security-Policy'] = "default-src 'none'"
        if posixpath.basename(path).lower().endswith(_RISKY_SUFFIXES):
            response['Content-Type'] = 'text/plain'
            response['Content-Disposition'] = 'attachment'
        return response

    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', media_serve, name='media'),
    ]
