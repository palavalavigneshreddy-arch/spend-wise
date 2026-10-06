from calendar import month_name
from datetime import date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .forms import RegisterForm, CategoryForm, ExpenseForm, BudgetForm
from .models import Category, Budget, Expense


def selected_month(request):
    raw = request.GET.get('month') or request.POST.get('month')
    try:
        year, month = map(int, raw.split('-'))
        return date(year, month, 1)
    except (AttributeError, ValueError):
        today = date.today(); return today.replace(day=1)

def money(value): return value or Decimal('0.00')

def status_for(spent, limit):
    if not limit: return ('No budget set', 'neutral', 0)
    ratio = (spent / limit) * 100
    if ratio > 100: return ('Over budget', 'danger', ratio)
    if ratio >= 100: return ('Limit reached', 'danger', ratio)
    if ratio >= 80: return ('Warning', 'warning', ratio)
    return ('Normal', 'normal', ratio)

@login_required
def dashboard(request):
    month = selected_month(request)
    expenses = Expense.objects.filter(user=request.user, date__year=month.year, date__month=month.month)
    budgets = {b.category_id: b for b in Budget.objects.filter(user=request.user, month_year=month)}
    spent_by_category = {row['category_id']: money(row['total']) for row in expenses.values('category_id').annotate(total=Sum('amount'))}
    total_spending = money(expenses.aggregate(total=Sum('amount'))['total'])
    total_budget = sum((b.monthly_limit for b in budgets.values()), Decimal('0.00'))
    category_rows = []
    for category in Category.objects.filter(user=request.user):
        spent = spent_by_category.get(category.id, Decimal('0.00')); budget = budgets.get(category.id)
        label, tone, percent = status_for(spent, budget.monthly_limit if budget else None)
        category_rows.append({'category': category, 'spent': spent, 'budget': budget, 'label': label, 'tone': tone, 'percent': percent, 'remaining': (budget.monthly_limit - spent) if budget else None})
    context = {'month': month, 'month_label': f'{month_name[month.month]} {month.year}', 'month_value': month.strftime('%Y-%m'), 'total_budget': total_budget, 'total_spending': total_spending, 'remaining': total_budget - total_spending, 'category_rows': category_rows, 'recent_expenses': expenses.select_related('category')[:6]}
    return render(request, 'tracker/dashboard.html', context)

@login_required
def expenses(request):
    month = selected_month(request)
    qs = Expense.objects.filter(user=request.user).select_related('category')
    if request.GET.get('month'): qs = qs.filter(date__year=month.year, date__month=month.month)
    if request.GET.get('category'): qs = qs.filter(category_id=request.GET['category'])
    paginator = Paginator(qs, 8)
    page = paginator.get_page(request.GET.get('page'))
    edit_obj = None
    if request.GET.get('edit'): edit_obj = get_object_or_404(Expense, pk=request.GET['edit'], user=request.user)
    form = ExpenseForm(instance=edit_obj, user=request.user)
    return render(request, 'tracker/expenses.html', {'page': page, 'form': form, 'edit_obj': edit_obj, 'categories': Category.objects.filter(user=request.user), 'month_value': request.GET.get('month', month.strftime('%Y-%m'))})

@login_required
def expense_create(request):
    if request.method != 'POST': return redirect('expenses')
    form = ExpenseForm(request.POST, user=request.user)
    if form.is_valid():
        obj = form.save(commit=False); obj.user = request.user; obj.save()
        messages.success(request, 'Expense saved successfully.'); return redirect('dashboard')
    month = selected_month(request)
    qs = Expense.objects.filter(user=request.user).select_related('category')
    page = Paginator(qs, 8).get_page(1)
    return render(request, 'tracker/expenses.html', {'page': page, 'form': form, 'edit_obj': None, 'categories': Category.objects.filter(user=request.user), 'month_value': month.strftime('%Y-%m')}, status=200)

@login_required
def expense_edit(request, pk):
    obj = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=obj, user=request.user)
        if form.is_valid(): form.save(); messages.success(request, 'Expense updated.'); return redirect('expenses')
    else: form = ExpenseForm(instance=obj, user=request.user)
    qs = Expense.objects.filter(user=request.user).select_related('category')
    return render(request, 'tracker/expenses.html', {'page': Paginator(qs, 8).get_page(1), 'form': form, 'edit_obj': obj, 'categories': Category.objects.filter(user=request.user), 'month_value': obj.date.strftime('%Y-%m')})

@login_required
def expense_delete(request, pk):
    obj = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST': obj.delete(); messages.success(request, 'Expense deleted.')
    return redirect('expenses')

@login_required
def categories(request):
    edit_obj = get_object_or_404(Category, pk=request.GET['edit'], user=request.user) if request.GET.get('edit') else None
    form = CategoryForm(request.POST or None, instance=edit_obj)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False); obj.user = request.user; obj.save(); messages.success(request, 'Category saved.'); return redirect('categories')
    return render(request, 'tracker/categories.html', {'categories': Category.objects.filter(user=request.user), 'form': form, 'edit_obj': edit_obj})

@login_required
def category_edit(request, pk): return redirect(f'/categories/?edit={pk}')

@login_required
def category_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk, user=request.user)
    if obj.expenses.exists(): messages.error(request, 'This category cannot be deleted because it contains expenses.')
    elif request.method == 'POST': obj.delete(); messages.success(request, 'Category deleted.')
    return redirect('categories')

@login_required
def budgets(request):
    month = selected_month(request); edit_obj = get_object_or_404(Budget, pk=request.GET['edit'], user=request.user) if request.GET.get('edit') else None
    form = BudgetForm(request.POST or None, instance=edit_obj, user=request.user)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        obj, _ = Budget.objects.update_or_create(user=request.user, category=data['category'], month_year=data['month_year'], defaults={'monthly_limit': data['monthly_limit']})
        messages.success(request, 'Monthly budget saved.'); return redirect(f'/budgets/?month={data["month_year"]:%Y-%m}')
    rows = Budget.objects.filter(user=request.user, month_year=month).select_related('category')
    return render(request, 'tracker/budgets.html', {'month': month, 'month_value': month.strftime('%Y-%m'), 'form': form, 'edit_obj': edit_obj, 'rows': rows, 'total': rows.aggregate(total=Sum('monthly_limit'))['total'] or Decimal('0.00')})

@login_required
def budget_delete(request, pk):
    obj = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST': obj.delete(); messages.success(request, 'Budget deleted.')
    return redirect('budgets')

def register(request):
    if request.user.is_authenticated: return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid(): login(request, form.save()); return redirect('dashboard')
    return render(request, 'registration/register.html', {'form': form})
