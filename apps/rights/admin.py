from django.contrib import admin
from .models import ConsumerRight

@admin.register(ConsumerRight)
class ConsumerRightAdmin(admin.ModelAdmin):
    list_display = ['order', 'title', 'category_badge', 'is_active', 'updated_at']
    list_editable = ['order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'content', 'category']
    ordering = ['order', 'title']
    list_per_page = 25

    def category_badge(self, obj):
        category = obj.category or 'Umumiy'
        return format_html('<span style="background:#3b82f6;color:#fff;padding:2px 8px;border-radius:8px;font-size:11px">{}</span>', category)
    category_badge.short_description = "Kategoriya"
