from django.contrib import admin
from django.utils.html import format_html
from .models import TelegramUser, UserRole


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        'telegram_id', 'display_name', 'username_link',
        'phone_number', 'role_badge', 'registration_badge',
        'is_active', 'created_at',
    ]
    list_filter = ['role', 'is_active', 'is_registered', 'language', 'created_at']
    search_fields = [
        'telegram_id', 'username', 'first_name', 'last_name',
        'full_name_input', 'phone_number', 'phone_number2',
    ]
    readonly_fields = ['telegram_id', 'created_at', 'last_activity']
    actions = ['make_admin', 'make_moderator', 'make_entrepreneur', 'make_consumer', 'activate_users', 'deactivate_users']
    ordering = ['-created_at']
    list_per_page = 30

    @admin.action(description="🛡 Tanlanganlarni «ADMIN» qilish")
    def make_admin(self, request, queryset):
        count = queryset.update(role=UserRole.ADMIN)
        self.message_user(request, f"{count} ta foydalanuvchiga ADMIN huquqi berildi.")

    @admin.action(description="👮 Tanlanganlarni «MODERATOR» qilish")
    def make_moderator(self, request, queryset):
        count = queryset.update(role=UserRole.MODERATOR)
        self.message_user(request, f"{count} ta foydalanuvchiga MODERATOR huquqi berildi.")

    @admin.action(description="💼 Tanlanganlarni «TADBIRKOR» qilish")
    def make_entrepreneur(self, request, queryset):
        count = queryset.update(role=UserRole.ENTREPRENEUR)
        self.message_user(request, f"{count} ta foydalanuvchiga TADBIRKOR maqomi berildi.")

    @admin.action(description="👤 Tanlanganlarni «ISTE'MOLCHI» qilish")
    def make_consumer(self, request, queryset):
        count = queryset.update(role=UserRole.CONSUMER)
        self.message_user(request, f"{count} ta foydalanuvchiga ISTE'MOLCHI maqomi berildi.")

    @admin.action(description="✅ Tanlanganlarni faollashtirish (Activate)")
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} ta foydalanuvchi faollashtirildi.")

    @admin.action(description="🚫 Tanlanganlarni bloklash (Deactivate)")
    def deactivate_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} ta foydalanuvchi bloklandi.")

    fieldsets = (
        ("🆔 Telegram ma'lumotlari", {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name')
        }),
        ("👤 Ro'yxatdan o'tish ma'lumotlari", {
            'fields': ('full_name_input', 'phone_number', 'phone_number2', 'is_registered', 'language')
        }),
        ("🔐 Tizim", {
            'fields': ('role', 'is_active', 'created_at', 'last_activity')
        }),
    )

    @admin.display(description="To'liq ismi")
    def display_name(self, obj):
        name = obj.full_name_input or obj.full_name
        return format_html('<b>{}</b>', name)

    @admin.display(description='Username')
    def username_link(self, obj):
        if obj.username:
            return format_html(
                '<a href="https://t.me/{}" target="_blank">@{}</a>',
                obj.username, obj.username
            )
        return format_html('<span style="color:#aaa">—</span>')

    @admin.display(description='Rol')
    def role_badge(self, obj):
        colors = {
            UserRole.ADMIN: '#e74c3c',
            UserRole.MODERATOR: '#e67e22',
            UserRole.ENTREPRENEUR: '#3498db',
            UserRole.CONSUMER: '#27ae60',
        }
        labels = {
            UserRole.ADMIN: '🛡 Admin',
            UserRole.MODERATOR: '👮 Moderator',
            UserRole.ENTREPRENEUR: '💼 Tadbirkor',
            UserRole.CONSUMER: '👤 Iste\'molchi',
        }
        color = colors.get(obj.role, '#95a5a6')
        label = labels.get(obj.role, obj.role)
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:12px">{}</span>',
            color, label
        )

    @admin.display(description='Til')
    def language_badge(self, obj):
        if obj.language == 'ru':
            return format_html('<span>🇷🇺 Русский</span>')
        return format_html('<span>🇺🇿 O\'zbekcha</span>')

    @admin.display(description="Ro'yxat")
    def registration_badge(self, obj):
        if obj.is_registered:
            return format_html(
                '<span style="color:#27ae60;font-weight:bold">✅ Ha</span>'
            )
        return format_html(
            '<span style="color:#e74c3c">⏳ Yo\'q</span>'
        )
