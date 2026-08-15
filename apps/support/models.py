from django.db import models

class SupportConfiguration(models.Model):
    phone = models.CharField(max_length=50, blank=True)
    telegram_username = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    working_hours = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Yordam konfiguratsiyasi"
        verbose_name_plural = "Yordam konfiguratsiyasi"
    
    def __str__(self) -> str:
        return f"Yordam - {self.phone}"
    
    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).first()
