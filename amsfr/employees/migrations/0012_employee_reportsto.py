# Generated by Django 4.1.4 on 2022-12-18 21:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0011_alter_holiday_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='reportsTo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.employee'),
        ),
    ]