# Generated by Django 4.1.3 on 2023-11-10 14:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskhub_api', '0003_taskhubapiresponse_task_images_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='employees',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='task',
            name='images',
            field=models.ManyToManyField(blank=True, to='taskhub_api.azureimage'),
        ),
        migrations.AlterField(
            model_name='task',
            name='vehicles',
            field=models.ManyToManyField(blank=True, to='taskhub_api.vehicle'),
        ),
    ]