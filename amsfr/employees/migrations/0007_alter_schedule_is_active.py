# Generated by Django 4.1.4 on 2022-12-16 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0006_schedule_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='is_active',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
