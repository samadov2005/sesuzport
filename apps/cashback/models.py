from django.db import models

class TransactionType(models.TextChoices):
    EARN = 'EARN', 'Olish'
    SPEND = 'SPEND', 'Sarflash'
    ADJUSTMENT = 'ADJUSTMENT', 'Tuzatish'

class CashbackAccount(models.Model):
    user = models.OneToOneField('users.TelegramUser', on_delete=models.CASCADE, related_name='cashback_account')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Keshbek hisobi"
        verbose_name_plural = "Keshbek hisoblari"
    
    def __str__(self) -> str:
        return f"{self.user} - {self.balance} so'm"

class CashbackTransaction(models.Model):
    account = models.ForeignKey(CashbackAccount, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=15, choices=TransactionType.choices)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Keshbek tranzaksiyasi"
        verbose_name_plural = "Keshbek tranzaksiyalari"
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.account.user} - {self.amount} ({self.transaction_type})"
