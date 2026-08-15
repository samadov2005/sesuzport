from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Complaint, ComplaintStatusHistory

@receiver(pre_save, sender=Complaint)
def track_status_change(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Complaint.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            # Logic here if needed. Status change history is already handled in admin.py.
            # Post save could send notifications.
            pass
