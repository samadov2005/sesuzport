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
    list_display = [
        'ticket_id', 'user_link', 'short_description',
        'status_badge', 'created_at', 'location_link'
    ]
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['ticket_id', 'user__telegram_id', 'user__username', 'user__first_name', 'description']
    readonly_fields = [
        'ticket_id', 'user', 'photo_preview', 'location_link_detail',
        'created_at', 'updated_at', 'resolved_at'
    ]
    actions = ['mark_as_under_review', 'mark_as_approved', 'mark_as_resolved', 'mark_as_rejected']
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('📋 Murojaat ma\'lumotlari', {
            'fields': ('ticket_id', 'user', 'description')
        }),
        ('📊 Holat va Moderatsiya', {
            'fields': ('status', 'moderation_comment')
        }),
        ('📸 Isbot (Rasm)', {
            'fields': ('photo_preview',)
        }),
        ('📍 Joylashuv (GPS)', {
            'fields': ('latitude', 'longitude', 'location_link_detail')
        }),
        ('⏰ Vaqtlar', {
            'fields': ('created_at', 'updated_at', 'resolved_at')
        }),
    )
    inlines = [ComplaintStatusHistoryInline]

    @admin.action(description="🔍 Tanlanganlarni «Ko'rib chiqilmoqda» holatiga o'tkazish")
    def mark_as_under_review(self, request, queryset):
        count = queryset.update(status=ComplaintStatus.UNDER_REVIEW)
        self.message_user(request, f"{count} ta murojaat «Ko'rib chiqilmoqda» holatiga o'tkazildi.")

    @admin.action(description="⏳ Tanlanganlarni «Jarayonda (Tasdiqlangan)» holatiga o'tkazish")
    def mark_as_approved(self, request, queryset):
        count = queryset.update(status=ComplaintStatus.APPROVED)
        self.message_user(request, f"{count} ta murojaat «Jarayonda» holatiga o'tkazildi.")

    @admin.action(description="✅ Tanlanganlarni «Hal qilindi» holatiga o'tkazish")
    def mark_as_resolved(self, request, queryset):
        count = queryset.update(status=ComplaintStatus.RESOLVED, resolved_at=timezone.now())
        self.message_user(request, f"{count} ta murojaat «Hal qilindi» deb belgilandi.")

    @admin.action(description="❌ Tanlanganlarni «Rad etildi» holatiga o'tkazish")
    def mark_as_rejected(self, request, queryset):
        count = queryset.update(status=ComplaintStatus.REJECTED)
        self.message_user(request, f"{count} ta murojaat «Rad etildi» deb belgilandi.")

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Complaint.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                if obj.status == ComplaintStatus.RESOLVED and not obj.resolved_at:
                    obj.resolved_at = timezone.now()

                ComplaintStatusHistory.objects.create(
                    complaint=obj,
                    old_status=old_obj.status,
                    new_status=obj.status,
                    changed_by=request.user,
                    comment=obj.moderation_comment or f"Admin @{request.user.username} tomonidan yangilandi"
                )

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

    @admin.display(description="Foydalanuvchi")
    def user_link(self, obj):
        name = obj.user.full_name_input or obj.user.full_name or f"ID: {obj.user.telegram_id}"
        return format_html(
            '<a href="/admin/users/telegramuser/{}/change/" style="font-weight:600">👤 {}</a>',
            obj.user.id, name
        )

    @admin.display(description="Tavsif")
    def short_description(self, obj):
        desc = obj.description or ''
        return desc[:50] + '...' if len(desc) > 50 else desc

    @admin.display(description="Xarita")
    def location_link(self, obj):
        if obj.latitude and obj.longitude:
            return format_html(
                '<a href="https://maps.google.com/?q={},{}&t=m" target="_blank" style="background:#2563eb;color:#fff;padding:3px 8px;border-radius:6px;text-decoration:none;font-size:11px">📍 Xarita</a>',
                obj.latitude, obj.longitude
            )
        return "-"

    @admin.display(description="Xaritada ko'rish")
    def location_link_detail(self, obj):
        if obj.latitude and obj.longitude:
            return format_html(
                '<a href="https://maps.google.com/?q={},{}&t=m" target="_blank" style="font-weight:bold;font-size:14px;color:#2563eb">📍 Google Maps orqali joylashuvni ochish ({}, {})</a>',
                obj.latitude, obj.longitude, obj.latitude, obj.longitude
            )
        return "Joylashuv berilmagan"

    @admin.display(description="Jonli Kamera Rasmi")
    def photo_preview(self, obj):
        if obj.photo_file_id:
            return format_html(
                '<div style="background:#0f172a;color:#38bdf8;padding:10px;border-radius:8px;font-family:monospace;word-break:break-all">'
                '📸 <b>Telegram File ID:</b> <code>{}</code><br>'
                '<small style="color:#94a3b8">Ushbu rasm Telegram Arxiv kanalida va server bulutida xavfsiz saqlanmoqda.</small>'
                '</div>',
                obj.photo_file_id
            )
        return format_html('<span style="color:#94a3b8">Rasm yuklanmagan</span>')

    @admin.display(description="Holat")
    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'UNDER_REVIEW': '#3b82f6',
            'APPROVED': '#8b5cf6',
            'RESOLVED': '#10b981',
            'REJECTED': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            color, obj.get_status_display()
        )
