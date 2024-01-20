# Generated by Django 4.1.3 on 2024-01-20 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskhub_api', '0005_alter_taskstatus_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasktype',
            name='title',
            field=models.CharField(choices=[('assembly', 'assembly'), ('delivery', 'delivery'), ('installation', 'installation'), ('repair', 'repair'), ('service', 'service')], max_length=20),
        ),
    ]