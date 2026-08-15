"""
SESPORT Custom Django AdminSite.
Overrides the default admin index to inject dashboard statistics.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class SesportAdminSite(admin.AdminSite):
    site_header = "SESPORT Admin"
    site_title = "SESPORT"
    index_title = "Boshqaruv paneli"
    site_url = None  # Hide "View site" link

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self._get_dashboard_context())
        return super().index(request, extra_context=extra_context)

    def _get_dashboard_context(self) -> dict:
        from django.utils import timezone
        from datetime import timedelta

        try:
            from apps.users.models import TelegramUser
            from apps.complaints.models import Complaint
            from apps.stores.models import Store
            from apps.cashback.models import CashbackAccount, CashbackTransaction
            from django.db.models import Sum, Count
            from decimal import Decimal

            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            # ── Users ────────────────────────────────────────────
            total_users = TelegramUser.objects.count()
            new_users_today = TelegramUser.objects.filter(
                created_at__gte=today_start
            ).count()

            # ── Complaints ────────────────────────────────────────
            complaints_qs = Complaint.objects.all()
            total_complaints = complaints_qs.count()
            pending = complaints_qs.filter(status='PENDING').count()
            under_review = complaints_qs.filter(status='UNDER_REVIEW').count()
            approved = complaints_qs.filter(status='APPROVED').count()
            rejected = complaints_qs.filter(status='REJECTED').count()
            resolved = complaints_qs.filter(status='RESOLVED').count()

            recent_complaints = list(
                Complaint.objects.select_related('user')
                .order_by('-created_at')[:8]
            )

            # ── Stores ────────────────────────────────────────────
            stores_qs = Store.objects.filter(is_active=True)
            total_stores = stores_qs.count()
            green = stores_qs.filter(safety_status='GREEN').count()
            yellow = stores_qs.filter(safety_status='YELLOW').count()
            red = stores_qs.filter(safety_status='RED').count()

            # ── Cashback ──────────────────────────────────────────
            cashback_accounts = CashbackAccount.objects.count()
            total_cashback_val = CashbackAccount.objects.aggregate(
                s=Sum('balance')
            )['s'] or Decimal('0')
            # Format as readable number
            total_cashback = _format_big_number(float(total_cashback_val))

            # ── Weekly complaints (last 7 days) ───────────────────
            weekly_labels = []
            weekly_data = []
            for i in range(6, -1, -1):
                day = now - timedelta(days=i)
                day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                count = Complaint.objects.filter(
                    created_at__gte=day_start,
                    created_at__lt=day_end,
                ).count()
                weekly_labels.append(day.strftime('%d.%m'))
                weekly_data.append(count)

            # ── Recent users ──────────────────────────────────────
            recent_users = list(
                TelegramUser.objects.order_by('-created_at')[:8]
            )

            return {
                # Users
                'total_users': total_users,
                'new_users_today': new_users_today,
                # Complaints
                'total_complaints': total_complaints,
                'pending_complaints': pending,
                'under_review_complaints': under_review,
                'approved_complaints': approved,
                'rejected_complaints': rejected,
                'resolved_complaints': resolved,
                'recent_complaints': recent_complaints,
                # Stores
                'total_stores': total_stores,
                'safe_stores': green,
                'green_stores': green,
                'yellow_stores': yellow,
                'red_stores': red,
                # Cashback
                'cashback_accounts': cashback_accounts,
                'total_cashback': total_cashback,
                # Weekly
                'weekly_labels': weekly_labels,
                'weekly_data': weekly_data,
                # Recent
                'recent_users': recent_users,
            }

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Dashboard context error: {e}")
            return {
                'total_users': 0, 'new_users_today': 0,
                'total_complaints': 0, 'pending_complaints': 0,
                'under_review_complaints': 0, 'approved_complaints': 0,
                'rejected_complaints': 0, 'resolved_complaints': 0,
                'total_stores': 0, 'safe_stores': 0,
                'green_stores': 0, 'yellow_stores': 0, 'red_stores': 0,
                'cashback_accounts': 0, 'total_cashback': '0',
                'weekly_labels': [], 'weekly_data': [],
                'recent_complaints': [], 'recent_users': [],
            }


def _format_big_number(n: float) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(int(n))


# Singleton instance — used as the default admin site
sesport_admin = SesportAdminSite(name='sesport_admin')
