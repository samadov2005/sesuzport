from asgiref.sync import sync_to_async
from django.utils import timezone
from django.db.models import Q

from apps.users.models import TelegramUser, UserRole
from apps.complaints.models import Complaint, ComplaintStatus, ComplaintStatusHistory
from apps.stores.models import Store, SafetyStatus
from django.core.paginator import Paginator


@sync_to_async
def is_admin_user(telegram_id: int) -> bool:
    """Check if the user has ADMIN or MODERATOR role in the database.
    This is the single source of truth — managed via Django Admin panel.
    """
    return TelegramUser.objects.filter(
        telegram_id=telegram_id,
        role__in=[UserRole.ADMIN, UserRole.MODERATOR],
        is_active=True
    ).exists()


@sync_to_async
def get_admin_dashboard_stats() -> dict:
    """Get fast real-time summary stats for the Telegram admin dashboard."""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_users = TelegramUser.objects.count()
    new_users_today = TelegramUser.objects.filter(created_at__gte=today_start).count()

    complaints = Complaint.objects.all()
    total_complaints = complaints.count()
    pending = complaints.filter(status=ComplaintStatus.PENDING).count()
    under_review = complaints.filter(status=ComplaintStatus.UNDER_REVIEW).count()
    approved = complaints.filter(status=ComplaintStatus.APPROVED).count()
    rejected = complaints.filter(status=ComplaintStatus.REJECTED).count()
    resolved = complaints.filter(status=ComplaintStatus.RESOLVED).count()
    complaints_today = complaints.filter(created_at__gte=today_start).count()

    stores = Store.objects.filter(is_active=True)
    total_stores = stores.count()
    green_stores = stores.filter(safety_status=SafetyStatus.GREEN).count()
    yellow_stores = stores.filter(safety_status=SafetyStatus.YELLOW).count()
    red_stores = stores.filter(safety_status=SafetyStatus.RED).count()

    return {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'total_complaints': total_complaints,
        'complaints_today': complaints_today,
        'pending': pending,
        'under_review': under_review,
        'approved': approved,
        'rejected': rejected,
        'resolved': resolved,
        'total_stores': total_stores,
        'green_stores': green_stores,
        'yellow_stores': yellow_stores,
        'red_stores': red_stores,
    }


@sync_to_async
def get_pending_complaints(page: int = 1, page_size: int = 5) -> tuple[list[Complaint], int]:
    """Get complaints waiting for review (PENDING or UNDER_REVIEW)."""
    qs = Complaint.objects.filter(
        status__in=[ComplaintStatus.PENDING, ComplaintStatus.UNDER_REVIEW]
    ).select_related('user').order_by('-created_at')

    paginator = Paginator(qs, page_size)
    total_pages = paginator.num_pages
    try:
        complaints = list(paginator.page(page).object_list)
    except Exception:
        complaints = []
    return complaints, total_pages


@sync_to_async
def search_complaint_or_user(query: str) -> dict:
    """Search for complaints or users by ID, ticket_id, or username."""
    query = query.strip()
    result = {'complaints': [], 'users': []}

    # 1. Search Complaints
    complaints_qs = Complaint.objects.filter(
        Q(ticket_id__icontains=query) |
        Q(description__icontains=query) |
        Q(user__username__icontains=query)
    ).select_related('user').order_by('-created_at')[:5]
    result['complaints'] = list(complaints_qs)

    # 2. Search Users
    user_q = Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
    if query.isdigit():
        user_q |= Q(telegram_id=int(query))
    users_qs = TelegramUser.objects.filter(user_q).order_by('-created_at')[:5]
    result['users'] = list(users_qs)

    return result


@sync_to_async
def get_all_active_user_ids() -> list[int]:
    """Get all telegram IDs of active users for broadcast."""
    return list(TelegramUser.objects.filter(is_active=True).values_list('telegram_id', flat=True))


@sync_to_async
def get_stores_by_safety(status: str) -> list[Store]:
    """Get stores filtered by safety status."""
    return list(Store.objects.filter(safety_status=status, is_active=True).order_by('name')[:15])


@sync_to_async
def update_store_safety(store_id: int, new_status: str) -> Store | None:
    """Update a store's safety status."""
    try:
        store = Store.objects.get(id=store_id)
        store.safety_status = new_status
        store.save()
        return store
    except Store.DoesNotExist:
        return None
