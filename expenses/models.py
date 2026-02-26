from django.db import models
from datetime import date

class CreditCard(models.Model):
    card_name = models.CharField(max_length=40)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f'{self.card_name} - Limit: ${self.credit_limit}'
    
    class Meta:
        verbose_name_plural = "Credit Cards"

class Transaction(models.Model):
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=date.today)
    description = models.TextField(blank=True)
    
    class Category(models.TextChoices):
        INCOME = 'income', 'Income'
        NEED = 'need', 'Need'
        WANT = 'want', 'Want'
        SAVING = 'saving', 'Saving'
    
    category = models.CharField(max_length=10, choices=Category.choices)
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Cash'
        CREDIT_CARD = 'credit_card', 'Credit Card'
    
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )
    
    credit_card = models.ForeignKey(
        CreditCard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    
    def __str__(self):
        return f"{self.title} - ${self.amount} ({self.category})"
    
    class Meta:
        ordering = ['-date']