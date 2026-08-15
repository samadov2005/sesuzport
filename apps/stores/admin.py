from django.contrib import admin
from django.utils.html import format_html
from .models import Store, SafetyStatus

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'safety_status_badge', 'rating', 'phone', 'is_active', 'location_link']
    search_fields = ['name', 'address', 'phone']
    list_filter = ['safety_status', 'is_active']
    
    def location_link(self, obj):
        if obj.latitude and obj.longitude:
            return format_html('<a href="https://maps.google.com/?q={},{}">Xarita</a>', obj.latitude, obj.longitude)
        return "-"
    location_link.short_description = "Manzil"
    
    def safety_status_badge(self, obj):
        safety_key = obj.safety_status.lower() if obj.safety_status else 'green'
        return format_html('<span class="status-badge safety-{}">{}</span>', safety_key, obj.get_safety_status_display())
    safety_status_badge.short_description = "Xavfsizlik"
