from django.contrib import admin
from .models import SupportConfiguration

@admin.register(SupportConfiguration)
class SupportConfigurationAdmin(admin.ModelAdmin):
    list_display = ['phone', 'telegram_username', 'email', 'is_active', 'updated_at']
    list_filter = ['is_active']
