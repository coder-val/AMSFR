# Generated by Django 4.1.4 on 2023-01-05 04:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
            options={
                'db_table': 'departments',
            },
        ),
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
            options={
                'db_table': 'designations',
            },
        ),
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('holiday', models.CharField(max_length=50)),
                ('date', models.DateField()),
            ],
            options={
                'db_table': 'holidays',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('in_am', models.TimeField()),
                ('out_am', models.TimeField()),
                ('in_pm', models.TimeField()),
                ('out_pm', models.TimeField()),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'schedules',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('firstname', models.CharField(max_length=30)),
                ('middlename', models.CharField(max_length=30)),
                ('lastname', models.CharField(max_length=30)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('MALE', 'M'), ('FEMALE', 'F')], max_length=6)),
                ('mobile_number', models.CharField(blank=True, max_length=11, null=True)),
                ('Barangay', models.CharField(blank=True, max_length=30, null=True)),
                ('Municipality', models.CharField(blank=True, max_length=30, null=True)),
                ('Province', models.CharField(blank=True, max_length=30, null=True)),
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('biometric_id', models.ImageField(upload_to='')),
                ('date_employed', models.DateField(blank=True, null=True)),
                ('employment_status', models.CharField(max_length=8)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employees.department')),
                ('designation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employees.designation')),
                ('reportsTo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'employees',
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(max_length=30)),
                ('in_am', models.TimeField(blank=True, null=True)),
                ('out_am', models.TimeField(blank=True, null=True)),
                ('in_pm', models.TimeField(blank=True, null=True)),
                ('out_pm', models.TimeField(blank=True, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('remarks', models.CharField(blank=True, max_length=1, null=True)),
                ('reference', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employees.employee')),
            ],
            options={
                'db_table': 'attendance',
            },
        ),
    ]
