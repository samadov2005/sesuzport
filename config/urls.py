from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import custom admin site and auto-register all models to it
from config.admin import sesport_admin

# Auto-discover and register all models from the default admin into sesport_admin
admin.autodiscover()
for model, model_admin in admin.site._registry.items():
    try:
        sesport_admin.register(model, type(model_admin))
    except Exception:
        pass  # Already registered

from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', sesport_admin.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
