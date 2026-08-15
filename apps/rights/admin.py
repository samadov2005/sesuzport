from django.contrib import admin
from .models import ConsumerRight

@admin.register(ConsumerRight)
class ConsumerRightAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'content']
    ordering = ['order', 'title']
