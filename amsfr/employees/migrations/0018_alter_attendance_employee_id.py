# Generated by Django 4.1.4 on 2022-12-26 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0017_alter_attendance_employee_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='employee_id',
            field=models.CharField(max_length=30),
        ),
    ]