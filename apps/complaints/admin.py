import asyncio
import logging

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import Complaint, ComplaintStatusHistory, ComplaintStatus

logger = logging.getLogger(__name__)

class ComplaintStatusHistoryInline(admin.TabularInline):
    model = ComplaintStatusHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'changed_by', 'comment', 'created_at']
    can_delete = False

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'user', 'status_badge', 'created_at', 'updated_at', 'location_link']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['ticket_id', 'user__telegram_id', 'user__username', 'description']
    readonly_fields = ['ticket_id', 'user', 'photo_preview', 'location_link_detail', 'created_at', 'updated_at', 'resolved_at']
    fieldsets = (
        ('Complaint Info', {
            'fields': ('ticket_id', 'user', 'description')
        }),
        ('Status', {
            'fields': ('status', 'moderation_comment')
        }),
        ('Evidence', {
            'fields': ('photo_preview',)
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'location_link_detail')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at')
        }),
    )
    inlines = [ComplaintStatusHistoryInline]
    date_hierarchy = 'created_at'

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Complaint.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                # Set resolved_at if transitioning to RESOLVED
                if obj.status == ComplaintStatus.RESOLVED and not obj.resolved_at:
                    obj.resolved_at = timezone.now()

                ComplaintStatusHistory.objects.create(
                    complaint=obj,
                    old_status=old_obj.status,
                    new_status=obj.status,
                    changed_by=request.user,
                    comment=obj.moderation_comment
                )

                # Send Telegram notification to user
                try:
                    from bot.services.notification_service import notify_complaint_status_changed
                    telegram_id = obj.user.telegram_id
                    asyncio.run(
                        notify_complaint_status_changed(
                            telegram_id=telegram_id,
                            ticket_id=obj.ticket_id,
                            new_status=obj.status,
                            moderation_comment=obj.moderation_comment,
                        )
                    )
                except Exception as exc:
                    logger.error(f"Failed to send status notification for {obj.ticket_id}: {exc}")

        super().save_model(request, obj, form, change)

    def location_link(self, obj):
        return format_html('<a href="https://maps.google.com/?q={},{}">Xarita</a>', obj.latitude, obj.longitude)
    location_link.short_description = "Manzil"

    def location_link_detail(self, obj):
        return self.location_link(obj)
    location_link_detail.short_description = "Xaritada ko'rish"

    def photo_preview(self, obj):
        return f"Telegram File ID: {obj.photo_file_id}"
    photo_preview.short_description = "Rasm"

    def status_badge(self, obj):
        status_key = obj.status.lower() if obj.status else 'pending'
        return format_html('<span class="status-badge status-{}">{}</span>', status_key, obj.get_status_display())
    status_badge.short_description = "Holat"
