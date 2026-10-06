from decimal import Decimal
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Category, Budget, Expense

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'description')
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ('amount', 'date', 'category', 'notes')
        widgets = {'date': forms.DateInput(attrs={'type': 'date'}), 'notes': forms.Textarea(attrs={'rows': 3})}
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user) if user else Category.objects.none()
        self.fields['amount'].widget.attrs.update({'placeholder': '0.00', 'min': '0.01', 'step': '0.01'})
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= Decimal('0'): raise forms.ValidationError('Amount must be greater than zero.')
        return amount

class BudgetForm(forms.ModelForm):
    month_year = forms.DateField(input_formats=['%Y-%m', '%Y-%m-%d'])
    class Meta:
        model = Budget
        fields = ('category', 'month_year', 'monthly_limit')
        widgets = {'month_year': forms.DateInput(attrs={'type': 'month'}), 'monthly_limit': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'})}
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user) if user else Category.objects.none()
    def clean_month_year(self):
        value = self.cleaned_data['month_year']
        return value.replace(day=1)
    def clean_monthly_limit(self):
        value = self.cleaned_data['monthly_limit']
        if value <= Decimal('0'): raise forms.ValidationError('Monthly limit must be greater than zero.')
        return value
