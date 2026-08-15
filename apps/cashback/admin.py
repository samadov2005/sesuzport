from django.contrib import admin
from .models import CashbackAccount, CashbackTransaction

class CashbackTransactionInline(admin.TabularInline):
    model = CashbackTransaction
    extra = 0
    readonly_fields = ['amount', 'transaction_type', 'description', 'created_at']

@admin.register(CashbackAccount)
class CashbackAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'total_earned', 'total_spent', 'updated_at']
    search_fields = ['user__username', 'user__telegram_id']
    readonly_fields = ['user', 'balance', 'total_earned', 'total_spent']
    inlines = [CashbackTransactionInline]

@admin.register(CashbackTransaction)
class CashbackTransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'transaction_type', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['account__user__username', 'account__user__telegram_id', 'description']
