from django.db import models

class SafetyStatus(models.TextChoices):
    GREEN = 'GREEN', 'Xavfsiz'
    YELLOW = 'YELLOW', "Ehtiyotkor bo'l"
    RED = 'RED', 'Xavfli'

class Store(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    safety_status = models.CharField(max_length=10, choices=SafetyStatus.choices, default=SafetyStatus.GREEN)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Do'kon"
        verbose_name_plural = "Do'konlar"
        ordering = ['name']
    
    def __str__(self) -> str:
        return self.name
