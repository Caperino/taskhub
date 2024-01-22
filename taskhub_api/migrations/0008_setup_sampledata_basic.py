from django.db import migrations


def fill_task_types(apps, schema_editor):
    types = ('assembly', 'delivery', 'installation', 'repair', 'service')
    TaskType = apps.get_model('taskhub_api', "TaskType")
    [TaskType.objects.create(title=new_type) for new_type in types]


def fill_task_status(apps, schema_editor):
    status = ('queued', 'in progress', 'done')
    TaskStatus = apps.get_model('taskhub_api', "TaskStatus")
    [TaskStatus.objects.create(title=new_state) for new_state in status]


def fill_employee_types(apps, schema_editor):
    types = ('Office', 'Assembly', 'Printing', 'Sales', 'Contact')
    EmployeeType = apps.get_model('taskhub_api', "EmployeeType")
    [EmployeeType.objects.create(title=new_type) for new_type in types]


def fill_vehicle_types(apps, schema_editor):
    types = ('Sedan', 'Combi', 'Truck', 'Roof Storage', 'Business')
    VehicleType = apps.get_model('taskhub_api', "VehicleType")
    [VehicleType.objects.create(title=new_type) for new_type in types]


def fill_groups(apps, schema_editor):
    groups = ('Administrator', 'Manager', 'Supervisor', 'Employee')
    Group = apps.get_model('auth', 'Group')
    [Group.objects.create(name=new_group) for new_group in groups]


class Migration(migrations.Migration):
    dependencies = [
        ('taskhub_api', '0007_alter_employee_gender'),
    ]

    operations = [
        migrations.RunPython(fill_task_types),
        migrations.RunPython(fill_task_status),
        migrations.RunPython(fill_vehicle_types),
        migrations.RunPython(fill_employee_types),
        migrations.RunPython(fill_groups)
    ]
