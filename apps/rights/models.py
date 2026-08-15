from django.db import models

class ConsumerRight(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Iste'molchi huquqi"
        verbose_name_plural = "Iste'molchi huquqlari"
        ordering = ['order', 'title']
    
    def __str__(self) -> str:
        return self.title
