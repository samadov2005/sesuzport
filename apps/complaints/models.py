from django.db import models

class ComplaintStatus(models.TextChoices):
    PENDING = 'PENDING', 'Kutilmoqda'
    UNDER_REVIEW = 'UNDER_REVIEW', "Ko'rib chiqilmoqda"
    APPROVED = 'APPROVED', 'Tasdiqlandi'
    REJECTED = 'REJECTED', 'Rad etildi'
    RESOLVED = 'RESOLVED', "Hal qilindi"

class Complaint(models.Model):
    ticket_id = models.CharField(max_length=20, unique=True, db_index=True, editable=False)
    user = models.ForeignKey('users.TelegramUser', on_delete=models.PROTECT, related_name='complaints')
    description = models.TextField(max_length=3000)
    photo_file_id = models.CharField(max_length=512)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=20, choices=ComplaintStatus.choices, default=ComplaintStatus.PENDING, db_index=True)
    moderation_comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Murojaat"
        verbose_name_plural = "Murojaatlar"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = self._generate_ticket_id()
        super().save(*args, **kwargs)
    
    @classmethod
    def _generate_ticket_id(cls) -> str:
        from django.utils import timezone
        year = timezone.now().year
        prefix = f'SES-{year}-'
        last_complaint = cls.objects.filter(ticket_id__startswith=prefix).order_by('-ticket_id').first()
        if last_complaint and last_complaint.ticket_id:
            try:
                seq = int(last_complaint.ticket_id.split('-')[-1]) + 1
            except (ValueError, IndexError):
                seq = cls.objects.filter(ticket_id__startswith=prefix).count() + 1
        else:
            seq = 1
        
        while cls.objects.filter(ticket_id=f'{prefix}{seq:06d}').exists():
            seq += 1
        return f'{prefix}{seq:06d}'
    
    def __str__(self) -> str:
        return self.ticket_id

class ComplaintStatusHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=ComplaintStatus.choices)
    new_status = models.CharField(max_length=20, choices=ComplaintStatus.choices)
    changed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Holat tarixi"
        verbose_name_plural = "Holat tarixi"
        ordering = ['-created_at']
