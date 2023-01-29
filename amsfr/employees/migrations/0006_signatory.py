# Generated by Django 3.2.16 on 2023-01-28 17:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0005_employee_designation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Signatory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signatory', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
            ],
        ),
    ]
