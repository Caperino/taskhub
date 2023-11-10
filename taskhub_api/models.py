from django.db import models
from django.contrib.auth.models import AbstractUser


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
    """
    A customer is a person or a company, who is ordering something.
    """
    name = models.CharField(max_length=1024)
    address = models.CharField(max_length=1024)
    phone = models.CharField(max_length=20)
    is_company = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# TASKS
class Task(models.Model):
    """
    A task is an activity, which is assigned to an employee.
    """
    SHIFT_CHOICES = (
        ('am', 'am'),
        ('pm', 'pm')
    )

    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    title = models.CharField(max_length=1024)
    task_type = models.ForeignKey("TaskType", on_delete=models.PROTECT)
    task_status = models.ForeignKey("TaskStatus", on_delete=models.PROTECT)
    employees = models.ManyToManyField("Employee", blank=True)
    vehicles = models.ManyToManyField("Vehicle", blank=True)
    images = models.ManyToManyField("AzureImage", blank=True)
    scheduled_from = models.DateTimeField()
    from_shift = models.CharField(max_length=2, choices=SHIFT_CHOICES)
    scheduled_to = models.DateTimeField()
    to_shift = models.CharField(max_length=2, choices=SHIFT_CHOICES)

    def __str__(self):
        return "%s - %s" % (self.title, self.order)


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
    An Azure Image is an image, which is stored in the Azure Cloud.
    """
    image_name = models.CharField(max_length=128)

    def __str__(self):
        return self.image_name


# EMPLOYEES
class Employee(AbstractUser):
    """
    An employee is a person, who is working for the company.
    This class is also used for the user authentication.
    inherited fields from AbstractUser:
    username
    first_name
    last_name
    email
    password
    groups
    user_permissions
    is_staff
    is_active
    is_superuser
    last_login
    date_joined

    needed fields:
    username, first_name, last_name, email, password, groups
    """

    GENDER_CHOICES = (
        ('m', 'male'),
        ('f', 'female'),
        ('x', 'diverse'),
    )

    pfp_name = models.ForeignKey("AzureImage", on_delete=models.SET_NULL, null=True, blank=True)
    employee_type = models.ForeignKey("EmployeeType", on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=1024, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    drivers_license_status = models.BooleanField(null=True, blank=True)

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


class TaskHubApiResponse(models.Model):
    """
    A simple API response class
    """
    status = models.CharField(max_length=60, default="success")
    message = models.CharField(max_length=1024, default="")
