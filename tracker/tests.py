from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Category, Budget, Expense

class SpendWiseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ava', password='StrongPass123!')
        self.other = User.objects.create_user(username='ben', password='StrongPass123!')
        self.category = Category.objects.create(user=self.user, name='Food')
        self.client.login(username='ava', password='StrongPass123!')
    def test_monthly_spending_and_remaining(self):
        Budget.objects.create(user=self.user, category=self.category, monthly_limit=Decimal('10000'), month_year=date(2026, 10, 1))
        Expense.objects.create(user=self.user, category=self.category, amount=Decimal('2500'), date=date(2026, 10, 5))
        response = self.client.get(reverse('dashboard'), {'month': '2026-10'})
        self.assertContains(response, '₹2500.00'); self.assertContains(response, '₹7500.00')
    def test_thresholds_normal_warning_and_danger(self):
        Budget.objects.create(user=self.user, category=self.category, monthly_limit=Decimal('100'), month_year=date(2026, 10, 1))
        for amount, label in [(Decimal('79'), 'Normal'), (Decimal('80'), 'Warning'), (Decimal('100'), 'Limit reached')]:
            Expense.objects.all().delete(); Expense.objects.create(user=self.user, category=self.category, amount=amount, date=date(2026, 10, 5))
            self.assertContains(self.client.get(reverse('dashboard'), {'month': '2026-10'}), label)
    def test_user_isolation(self):
        foreign_category = Category.objects.create(user=self.other, name='Secret')
        foreign_expense = Expense.objects.create(user=self.other, category=foreign_category, amount=Decimal('9'), date=date(2026, 10, 1))
        self.assertNotContains(self.client.get(reverse('expenses')), 'Secret')
        self.assertEqual(self.client.get(reverse('expense_edit', args=[foreign_expense.pk])).status_code, 404)
    def test_invalid_expense_amount_returns_form_errors(self):
        response = self.client.post(reverse('expense_create'), {'amount': '-2', 'date': '2026-10-10', 'category': self.category.pk, 'notes': ''})
        self.assertEqual(response.status_code, 200); self.assertContains(response, 'greater than zero'); self.assertEqual(Expense.objects.count(), 0)
    def test_expense_creation_redirects_dashboard(self):
        response = self.client.post(reverse('expense_create'), {'amount': '125.50', 'date': '2026-10-10', 'category': self.category.pk, 'notes': 'Lunch'})
        self.assertRedirects(response, reverse('dashboard')); self.assertEqual(Expense.objects.get().amount, Decimal('125.50'))
    def test_category_with_expenses_cannot_be_deleted(self):
        Expense.objects.create(user=self.user, category=self.category, amount=Decimal('10'), date=date.today())
        response = self.client.post(reverse('category_delete', args=[self.category.pk]))
        self.assertRedirects(response, reverse('categories')); self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())
    def test_unique_monthly_budgets_update_existing(self):
        self.client.post(reverse('budgets'), {'category': self.category.pk, 'month_year': '2026-10', 'monthly_limit': '100'})
        self.client.post(reverse('budgets'), {'category': self.category.pk, 'month_year': '2026-10', 'monthly_limit': '250'})
        self.assertEqual(Budget.objects.filter(user=self.user, category=self.category, month_year=date(2026, 10, 1)).count(), 1)
        self.assertEqual(Budget.objects.get().monthly_limit, Decimal('250.00'))
