from asgiref.sync import sync_to_async
from apps.complaints.models import Complaint, ComplaintStatus, ComplaintStatusHistory
from apps.users.models import TelegramUser
from django.core.paginator import Paginator
from django.utils import timezone


@sync_to_async
def create_complaint(
    telegram_id: int,
    description: str,
    photo_file_id: str,
    latitude: float,
    longitude: float,
    user_info: dict | None = None,
) -> Complaint:
    """Create a new complaint. Ensures TelegramUser exists and auto-generates ticket_id."""
    user_info = user_info or {}
    user, _ = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'first_name': user_info.get('first_name') or 'Foydalanuvchi',
            'last_name': user_info.get('last_name') or '',
            'username': user_info.get('username') or '',
            'last_activity': timezone.now(),
        }
    )
    
    return Complaint.objects.create(
        user=user,
        description=description,
        photo_file_id=photo_file_id,
        latitude=latitude,
        longitude=longitude,
        status=ComplaintStatus.PENDING,
    )


@sync_to_async
def update_complaint_status_by_admin(
    complaint_id: int,
    new_status: str,
    comment: str | None = None,
) -> Complaint | None:
    """Update complaint status and record history."""
    try:
        complaint = Complaint.objects.select_related('user').get(id=complaint_id)
    except Complaint.DoesNotExist:
        return None

    old_status = complaint.status
    complaint.status = new_status
    if comment:
        complaint.moderation_comment = comment
    if new_status == ComplaintStatus.RESOLVED and not complaint.resolved_at:
        complaint.resolved_at = timezone.now()
    
    complaint.save()

    ComplaintStatusHistory.objects.create(
        complaint=complaint,
        old_status=old_status,
        new_status=new_status,
        comment=comment or "Telegram bot orqali o'zgartirildi",
    )
    return complaint


@sync_to_async
def get_user_complaints(
    telegram_id: int,
    page: int = 1,
    page_size: int = 5,
) -> tuple[list[Complaint], int]:
    """Return paginated list of user complaints and total pages."""
    qs = Complaint.objects.filter(user__telegram_id=telegram_id).order_by('-created_at')
    paginator = Paginator(qs, page_size)
    total_pages = paginator.num_pages
    try:
        complaints = list(paginator.page(page).object_list)
    except Exception:
        complaints = []
    return complaints, total_pages


@sync_to_async
def get_complaint_by_ticket_id(ticket_id: str, telegram_id: int | None = None) -> Complaint | None:
    """Get a complaint by ticket_id."""
    try:
        if telegram_id:
            return Complaint.objects.get(ticket_id=ticket_id, user__telegram_id=telegram_id)
        return Complaint.objects.get(ticket_id=ticket_id)
    except Complaint.DoesNotExist:
        return None


@sync_to_async
def get_complaint_by_id(complaint_id: int, telegram_id: int | None = None) -> Complaint | None:
    """Get a complaint by DB id with user preloaded."""
    try:
        qs = Complaint.objects.select_related('user')
        if telegram_id:
            return qs.get(id=complaint_id, user__telegram_id=telegram_id)
        return qs.get(id=complaint_id)
    except Complaint.DoesNotExist:
        return None
