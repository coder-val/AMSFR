# Generated by Django 3.2.16 on 2023-02-05 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0013_auto_20230205_2211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='barangay',
            field=models.CharField(max_length=30, verbose_name='* Barangay'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='municipality',
            field=models.CharField(max_length=30, verbose_name='* Municipality'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='province',
            field=models.CharField(max_length=30, verbose_name='* Province'),
        ),
    ]
