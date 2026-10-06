from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tracker.models import Category, Budget, Expense

class Command(BaseCommand):
    help = 'Create or refresh the SpendWise demo account data.'

    def handle(self, *args, **options):
        User = get_user_model()
        user, _ = User.objects.get_or_create(username='demo_user', defaults={'email': 'demo@example.com'})
        user.set_password('SpendWiseDemo123!'); user.save()
        today = date.today(); month = today.replace(day=1)
        records = {
            'Food': ('Meals, groceries & coffee', Decimal('12000'), [('Weekly groceries', Decimal('2350'), 1), ('Coffee with friends', Decimal('480'), 2), ('Dinner out', Decimal('1450'), 4)]),
            'Transport': ('Getting around town', Decimal('6000'), [('Metro recharge', Decimal('1200'), 2), ('Cab ride', Decimal('680'), 5)]),
            'Bills': ('Recurring household bills', Decimal('9000'), [('Internet bill', Decimal('899'), 3), ('Electricity bill', Decimal('1870'), 5)]),
            'Shopping': ('Personal and home shopping', Decimal('7500'), [('New running shoes', Decimal('3200'), 1), ('Home essentials', Decimal('950'), 4)]),
            'Health': ('Wellness and self-care', Decimal('5000'), [('Pharmacy', Decimal('620'), 2)]),
        }
        for name, (description, limit, expenses) in records.items():
            category, _ = Category.objects.get_or_create(user=user, name=name, defaults={'description': description})
            category.description = description; category.save()
            Budget.objects.update_or_create(user=user, category=category, month_year=month, defaults={'monthly_limit': limit})
            for title, amount, day in expenses:
                expense_date = month + timedelta(days=min(day - 1, 27))
                Expense.objects.get_or_create(user=user, category=category, date=expense_date, notes=title, defaults={'amount': amount})
        self.stdout.write(self.style.SUCCESS('Demo account seeded with categories, budgets, and expenses.'))
