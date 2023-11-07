from django.db import models

# Create your models here.
def current_date():
    from datetime import date
    return date.today()


# ORDERS
class Order(models.Model):
    order_nr = models.IntegerField()
    title = models.CharField(max_length=1024)
    customer = models.ForeignKey("Customer", on_delete=models.PROTECT)
    order_date = models.DateField(default=current_date)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Customer(models.Model):
    name = models.CharField(max_length=1024)
    address = models.CharField(max_length=1024)
    phone = models.CharField(max_length=20)
    is_company = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# TASKS
class Task(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    title = models.CharField(max_length=1024)
    task_type = models.ForeignKey("TaskType", on_delete=models.PROTECT)
    task_status = models.ForeignKey("TaskStatus", on_delete=models.PROTECT)
    employees = models.ManyToManyField("Employee")
    vehicles = models.ManyToManyField("Vehicle")
    scheduled_from = models.DateTimeField()
    from_shift = models.ForeignKey("Shift", on_delete=models.PROTECT)
    scheduled_to = models.DateTimeField()
    to_shift = models.ForeignKey("Shift", on_delete=models.PROTECT)

    def __str__(self):
        return self.title


class TaskType(models.Model):
    """
    A task type is a type of a task.
    possibilities: assembly, delivery, installation, repair, service
    """
    TASK_TYPES = (
	('as', 'assembly'),
	('de', 'delivery'),
	('in', 'installation'),
	('re', 'repair'),
	('se', 'service')
    )
    title = models.CharField(max_length=2, choices=TASK_TYPES)


class TaskStatus(models.Model):
    """
    A task status is a status of a task.
    possibilities: queued, in progress, done
    """
    TASK_STATUS = (
	('qu', 'queued'),
	('ip', 'in progress'),
	('do', 'done')
    )
    title = models.CharField(max_length=2, choices=TASK_STATUS)


class AzureImage(models.Model):
    """
    An azure image is an image of a task.
    """
    image = models.CharField(max_length=1024)
    task = models.ForeignKey(Task, on_delete=models.PROTECT)


class Shift(models.Model):
    """
    A shift is a period of time, when employees are working.
    possibilities: morning, afternoon
    """
    SHIFT_TYPE = (
	('mo', 'morning'),
	('an', 'afternoon')
    )
    title = models.CharField(max_length=30)
    short_name = models.CharField(max_length=2, db_index=True, choices=SHIFT_TYPE)


# EMPLOYEES
class Employee(models.Model):

    GENDER_CHOICES = (
        ('m', 'male'),
        ('f', 'female'),
        ('x', 'diverse'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    mail = models.CharField(max_length=320)
    password = models.CharField(max_length=128)
    employee_type = models.ForeignKey("EmployeeType", on_delete=models.PROTECT)
    address = models.CharField(max_length=1024, null=True)
    phone = models.CharField(max_length=20, null=True)
    birth_date = models.DateField(null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    drivers_license_status = models.BooleanField(null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class EmployeeType(models.Model):
    title = models.CharField(max_length=60)
    description = models.CharField(max_length=1024)

    def __str__(self):
        return self.title


# OTHER
class Vehicle(models.Model):
    title = models.CharField(max_length=60)
    vehicle_type = models.ManyToManyField("VehicleType")
    max_load_length = models.IntegerField()
    max_load_weight = models.IntegerField()

    def __str__(self):
        return self.title


class VehicleType(models.Model):
    title = models.CharField(max_length=60)
    description = models.CharField(max_length=1024)

    def __str__(self):
        return self.title