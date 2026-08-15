from django.db import models

class UserRole(models.TextChoices):
    CONSUMER = 'CONSUMER', 'Iste\'molchi'
    ENTREPRENEUR = 'ENTREPRENEUR', 'Tadbirkor'
    ADMIN = 'ADMIN', 'Administrator'
    MODERATOR = 'MODERATOR', 'Moderator'

class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    # Custom full name entered by user during onboarding (may differ from Telegram name)
    full_name_input = models.CharField(max_length=255, null=True, blank=True, verbose_name="To'liq ism (foydalanuvchi kiritgan)")
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="Asosiy telefon raqam")
    phone_number2 = models.CharField(max_length=20, null=True, blank=True, verbose_name="Qo'shimcha telefon raqam")
    is_registered = models.BooleanField(default=False, verbose_name="Ro'yxatdan o'tgan")
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CONSUMER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['-created_at']
    
    @property
    def full_name(self) -> str:
        parts = [self.first_name]
        if self.last_name:
            parts.append(self.last_name)
        return ' '.join(parts)
    
    def __str__(self) -> str:
        return f"{self.full_name} (@{self.username or self.telegram_id})"
