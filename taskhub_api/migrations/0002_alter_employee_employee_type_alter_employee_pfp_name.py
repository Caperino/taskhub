# Generated by Django 4.1.3 on 2023-11-09 19:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taskhub_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='employee_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='taskhub_api.employeetype'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='pfp_name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='taskhub_api.azureimage'),
        ),
    ]
