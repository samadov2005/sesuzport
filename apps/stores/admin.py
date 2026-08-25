from django.contrib import admin
from django.utils.html import format_html
from .models import Store, SafetyStatus

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'safety_status_badge', 'rating', 'phone', 'is_active', 'location_link']
    search_fields = ['name', 'address', 'phone']
    list_filter = ['safety_status', 'is_active']
    actions = ['set_safety_green', 'set_safety_yellow', 'set_safety_red', 'activate_stores', 'deactivate_stores']
    list_per_page = 25

    @admin.action(description="🟢 Tanlanganlarni «Yashil (Xavfsiz)» holatiga o'tkazish")
    def set_safety_green(self, request, queryset):
        count = queryset.update(safety_status=SafetyStatus.GREEN)
        self.message_user(request, f"{count} ta do'kon «Yashil (Xavfsiz)» deb belgilandi.")

    @admin.action(description="🟡 Tanlanganlarni «Sariq (Diqqat)» holatiga o'tkazish")
    def set_safety_yellow(self, request, queryset):
        count = queryset.update(safety_status=SafetyStatus.YELLOW)
        self.message_user(request, f"{count} ta do'kon «Sariq (Diqqat)» deb belgilandi.")

    @admin.action(description="🔴 Tanlanganlarni «Qizil (Xavfli)» holatiga o'tkazish")
    def set_safety_red(self, request, queryset):
        count = queryset.update(safety_status=SafetyStatus.RED)
        self.message_user(request, f"{count} ta do'kon «Qizil (Xavfli)» deb belgilandi.")

    @admin.action(description="✅ Tanlanganlarni faol qilish")
    def activate_stores(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="🚫 Tanlanganlarni nofaol qilish")
    def deactivate_stores(self, request, queryset):
        queryset.update(is_active=False)
    
    def location_link(self, obj):
        if obj.latitude and obj.longitude:
            return format_html('<a href="https://maps.google.com/?q={},{}&t=m" target="_blank" style="background:#2563eb;color:#fff;padding:2px 8px;border-radius:6px;text-decoration:none;font-size:11px">📍 Xarita</a>', obj.latitude, obj.longitude)
        return "-"
    location_link.short_description = "Manzil"
    
    def safety_status_badge(self, obj):
        colors = {
            SafetyStatus.GREEN: '#10b981',
            SafetyStatus.YELLOW: '#f59e0b',
            SafetyStatus.RED: '#ef4444',
        }
        color = colors.get(obj.safety_status, '#6b7280')
        return format_html('<span style="background:{};color:#fff;padding:3px 8px;border-radius:10px;font-size:11px;font-weight:600">{}</span>', color, obj.get_safety_status_display())
    safety_status_badge.short_description = "Xavfsizlik"
