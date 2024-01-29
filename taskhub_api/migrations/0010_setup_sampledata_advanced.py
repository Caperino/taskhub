from django.db import migrations
import datetime
from django.contrib.auth.hashers import make_password

from django.db.models import Q


def fill_employees(apps, schema_editor):
    EmployeeType = apps.get_model('taskhub_api', "EmployeeType")
    Employee = apps.get_model('taskhub_api', "Employee")
    Groups = apps.get_model('auth', "Group")
    employees = (
        ('kaptim7', 'Timo', 'Kappel', 'timo.kappel@thub.com', 'securepassword', Groups.objects.filter(Q(pk=1) | Q(pk=4)), EmployeeType.objects.get(pk=1),
        'My Address 1', '1234567890', datetime.datetime(2003,7,14), 'male', True),
        ('csihub29', 'Huba', 'Csicsics', 'huba.csicsics@thub.com', 'securepassword', Groups.objects.filter(Q(pk=3) | Q(pk=4)), EmployeeType.objects.get(pk=2),
         'My Address 2', '987654321', datetime.datetime(2002, 5, 5), 'male', True),
        ('jöbste91', 'Stefan', 'Jöbstl', 'stefan.joebstl@thub.com', 'securepassword', Groups.objects.filter(Q(pk=2) | Q(pk=4)), EmployeeType.objects.get(pk=4),
         'My Kärntner Address 3', '8716923712', datetime.datetime(2002, 8, 30), 'male', True),
        ('wolale54', 'Alexander', 'Wolf', 'alexander.wolf@thub.com', 'securepassword', Groups.objects.filter(pk=4), EmployeeType.objects.get(pk=5),
         'My Heimschuher Address 4', '672926372', datetime.datetime(2000, 9, 24), 'male', True),
    )
    e = [Employee.objects.create(username=employee[0], first_name=employee[1], last_name=employee[2], email=employee[3],
    employee_type=employee[6], address=employee[7], phone=employee[8],
    birth_date=employee[9], gender=employee[10], drivers_license_status=employee[11]) for employee in employees]
    for i in range(len(employees)):
        e[i].password = make_password(employees[i][4])
        [e[i].groups.add(group) for group in employees[i][5]]
        e[i].save()


def fill_customer(apps, schema_editor):
    Customer = apps.get_model('taskhub_api', "Customer")
    customers = (
        ('TK Inc.', 'Murmeltierstrasse 98', '1234567890', True),
        ('CS Inc.', 'Murmeltierstrasse 99', '987654321', False),
        ('SJ Inc.', 'Murmeltierstrasse 100', '8716923712', True),
        ('AW Inc.', 'Murmeltierstrasse 101', '672926372', False),
    )
    [Customer.objects.create(name=customer[0], address=customer[1], phone=customer[2], is_company=customer[3]) for customer in customers]



def fill_vehicle(apps, schema_editor):
    Vehicle = apps.get_model('taskhub_api', "Vehicle")
    VehicleType = apps.get_model('taskhub_api', "VehicleType")
    vehicles = (
        ('Mercedes Sprinter', VehicleType.objects.filter(Q(pk=3) | Q(pk=4)), 300, 3000),
        ('VW Caddy', VehicleType.objects.filter(pk__in=(3, 4, 5)), 200, 2000),
        ('VW Crafter', VehicleType.objects.filter(pk__in=(3, 5)), 400, 4000),
        ('VW T6', VehicleType.objects.filter(pk__in=(1, 5)), 250, 2500),
    )
    v = [Vehicle.objects.create(title=vehicle[0], max_load_length=vehicle[2], max_load_weight=vehicle[3]) for vehicle in vehicles]
    for vehicle in vehicles:
        for vehicle_type in vehicle[1]:
            v[vehicles.index(vehicle)].vehicle_type.add(vehicle_type)


def fill_order(apps, schema_editor):
    Order = apps.get_model('taskhub_api', "Order")
    Customer = apps.get_model('taskhub_api', "Customer")
    orders = (
        (1, 'Plane', Customer.objects.get(pk=1), datetime.datetime(2024, 1, 29), False),
        (2, 'Plakat', Customer.objects.get(pk=2), datetime.datetime(2024, 1, 15), False),
        (3, 'Folierung', Customer.objects.get(pk=3), datetime.datetime(2024, 1, 30), False),
    )
    [Order.objects.create(order_nr=order[0], title=order[1], customer=order[2], order_date=order[3], is_completed=order[4]) for order in orders]


def fill_task(apps, schema_editor):
    Task = apps.get_model('taskhub_api', "Task")
    TaskType = apps.get_model('taskhub_api', "TaskType")
    TaskStatus = apps.get_model('taskhub_api', "TaskStatus")
    Employee = apps.get_model('taskhub_api', "Employee")
    Vehicle = apps.get_model('taskhub_api', "Vehicle")
    Order = apps.get_model('taskhub_api', "Order")
    tasks = (
        (Order.objects.get(pk=1), 'Cutting', TaskType.objects.get(pk=1), TaskStatus.objects.get(pk=2),
         Employee.objects.filter(pk__in=(3, 4)), Vehicle.objects.filter(pk__in=[1]),
         datetime.datetime(2024, 1, 29), 'am', datetime.datetime(2024, 2, 2), 'pm'),
        (Order.objects.get(pk=2), 'Designen', TaskType.objects.get(pk=5), TaskStatus.objects.get(pk=3),
         Employee.objects.filter(pk__in=(1, 4)), [], datetime.datetime(2024, 1, 16),
         'am', datetime.datetime(2024, 2, 9), 'pm'),
        (Order.objects.get(pk=3), 'Ausbessern', TaskType.objects.get(pk=4), TaskStatus.objects.get(pk=1),
         Employee.objects.filter(pk__in=(3, 4)), Vehicle.objects.filter(pk__in=[3]),
         datetime.datetime(2024, 2, 1), 'am', datetime.datetime(2024, 2, 5), 'pm'),
    )
    [Task.objects.create(order=task[0], title=task[1], task_type=task[2], task_status=task[3],
                         scheduled_from=task[6], from_shift=task[7], scheduled_to=task[8], to_shift=task[9]) for task in tasks]
    for task in tasks:
        for employee in task[4]:
            Task.objects.get(order=task[0], title=task[1], task_type=task[2], task_status=task[3],
                             scheduled_from=task[6], from_shift=task[7], scheduled_to=task[8], to_shift=task[9]).employees.add(employee)
        for vehicle in task[5]:
            Task.objects.get(order=task[0], title=task[1], task_type=task[2], task_status=task[3],
                             scheduled_from=task[6], from_shift=task[7], scheduled_to=task[8], to_shift=task[9]).vehicles.add(vehicle)


class Migration(migrations.Migration):
    dependencies = [
        ('taskhub_api', '0009_alter_employee_birth_date_alter_order_order_date'),
    ]

    operations = [
        migrations.RunPython(fill_employees),
        migrations.RunPython(fill_customer),
        migrations.RunPython(fill_vehicle),
        migrations.RunPython(fill_order),
        migrations.RunPython(fill_task)
    ]
