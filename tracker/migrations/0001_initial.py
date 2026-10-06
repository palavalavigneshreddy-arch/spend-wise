from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='Category', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('name', models.CharField(max_length=80)), ('description', models.TextField(blank=True)), ('created_at', models.DateTimeField(auto_now_add=True)), ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to=settings.AUTH_USER_MODEL))], options={'ordering': ['name'] }),
        migrations.CreateModel(name='Budget', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('monthly_limit', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])), ('month_year', models.DateField()), ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to='tracker.category')), ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to=settings.AUTH_USER_MODEL))], options={'ordering': ['category__name'] }),
        migrations.CreateModel(name='Expense', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])), ('date', models.DateField()), ('notes', models.TextField(blank=True)), ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='expenses', to='tracker.category')), ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to=settings.AUTH_USER_MODEL))], options={'ordering': ['-date', '-id'] }),
        migrations.AddConstraint(model_name='category', constraint=models.UniqueConstraint(fields=('user', 'name'), name='unique_user_category')),
        migrations.AddConstraint(model_name='budget', constraint=models.UniqueConstraint(fields=('user', 'category', 'month_year'), name='unique_user_category_month')),
    ]
