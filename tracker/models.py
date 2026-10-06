from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

class Category(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['user', 'name'], name='unique_user_category')]
    def __str__(self): return self.name

class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    monthly_limit = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    month_year = models.DateField()
    class Meta:
        ordering = ['category__name']
        constraints = [models.UniqueConstraint(fields=['user', 'category', 'month_year'], name='unique_user_category_month')]
    def __str__(self): return f'{self.category} · {self.month_year:%b %Y}'

class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date = models.DateField()
    notes = models.TextField(blank=True)
    class Meta:
        ordering = ['-date', '-id']
    def __str__(self): return f'{self.category} · ₹{self.amount}'
