from django.contrib import admin
from .models import Category, Budget, Expense
admin.site.register([Category, Budget, Expense])
