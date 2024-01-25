from . import models
from rest_framework import serializers
from django.contrib.auth.models import Group
from django.db.utils import IntegrityError
from django.contrib.auth.password_validation import validate_password


class StringListField(serializers.ListField):
    child = serializers.CharField()


class IntegerListField(serializers.ListField):
    child = serializers.IntegerField()


class TaskHubApiResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for TaskHubApiResponse
    """
    class Meta:
        model = models.TaskHubApiResponse
        fields = ['status', 'message']


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for Costumer
    """
    class Meta:
        model = models.Customer
        fields = "__all__"


class AzureImageSerializer(serializers.ModelSerializer):
    """
    Serializer for EmployeeType
    """
    class Meta:
        model = models.AzureImage
        fields = "__all__"


class EmployeeTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for EmployeeType
    """
    class Meta:
        model = models.EmployeeType
        fields = "__all__"


class EmployeeGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for EmployeeGroup
    """
    class Meta:
        model = Group
        fields = "__all__"


# optimized
class VehicleSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    max_load_length = serializers.IntegerField(required=True)
    max_load_weight = serializers.IntegerField(required=True)
    vehicle_type = IntegerListField(required=True)

    def create(self, validated_data):
        """
        Create and return a new `Vehicle` instance, given the validated data.
        """
        vh_types = models.VehicleType.objects.filter(pk__in=validated_data["vehicle_type"])
        if len(validated_data["vehicle_type"]) != len(vh_types):
            raise IntegrityError("Invalid vehicle type id included")
        obj = models.Vehicle.objects.create(
            title=validated_data["title"],
            max_load_length=validated_data["max_load_length"],
            max_load_weight=validated_data["max_load_weight"]
        )
        obj.vehicle_type.add(*vh_types)
        obj.save()
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `Vehicle` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            if attr == "vehicle_type" and value is not None:
                vh_types = models.VehicleType.objects.filter(pk__in=value)
                if len(value) != len(vh_types):
                    raise IntegrityError("Invalid vehicle type id included")
                instance.vehicle_type.clear()
                instance.vehicle_type.add(*vh_types)
            elif value is not None:
                setattr(instance, attr, value)
        instance.save()
        return instance


def manual_vehicle_serializer(data: models.Vehicle):
    """
    Manual serializer for Vehicle
    """
    vh_types = [{"id": vh_type.pk, "title": vh_type.title} for vh_type in data.vehicle_type.all()]
    return {
        "id": data.pk,
        "title": data.title,
        "max_load_length": data.max_load_length,
        "max_load_weight": data.max_load_weight,
        "vehicle_type": vh_types
    }


# optimized
class OrderSerializer(serializers.Serializer):
    """
    Serializer for Order
    """
    order_nr = serializers.IntegerField(required=True)
    title = serializers.CharField(required=True)
    order_date = serializers.DateTimeField(required=False)
    customer = serializers.IntegerField(required=True)
    is_completed = serializers.BooleanField(required=False)

    def create(self, validated_data):
        """
        Create and return a new `Order` instance, given the validated data.
        """
        #customer = models.Customer.objects.filter(pk=validated_data["customer"]).first()
        #if customer is None:
            #raise IntegrityError("Invalid customer id")
        obj = models.Order.objects.create(
            order_nr=validated_data["order_nr"],
            title=validated_data["title"],
            customer_id=validated_data["customer"],
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `Order` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            if attr == "customer" and value is not None:
                #customer = models.Customer.objects.filter(pk=value).first()
                #if customer is None:
                    #raise IntegrityError("Invalid customer id")
                instance.customer_id = value
            elif value is not None:
                setattr(instance, attr, value)
        instance.save()
        return instance


def manual_order_serializer(data: models.Order):
    """
    Manual serializer for Order
    """
    return {
        "id": data.pk,
        "order_nr": data.order_nr,
        "title": data.title,
        "order_date": data.order_date,
        "customer": {
            "id": data.customer.pk,
            "name": data.customer.name,
            "address": data.customer.address,
            "phone": data.customer.phone,
            "is_company": data.customer.is_company
        },
        "is_completed": data.is_completed
    }


# optimized
class EmployeeSerializer(serializers.Serializer):
    """
    Serializer for Employee
    """
    username = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=False)
    groups = StringListField(required=True, allow_null=True, allow_empty=True)
    is_active = serializers.BooleanField(required=False)
    employee_type = serializers.IntegerField(required=True, allow_null=True)
    address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    birth_date = serializers.DateTimeField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    drivers_license_status = serializers.BooleanField(required=False, allow_null=True)

    def create(self, validated_data):
        """
        Create and return a new `Employee` instance, given the validated data.
        """

        # Groups
        requested_groups = Group.objects.filter(pk__in=validated_data.get("groups", []))
        if len(validated_data.get("groups", None)) != len(requested_groups):
            print("Invalid group id included")
            raise IntegrityError("Invalid group id included")

        obj = models.Employee(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            username=validated_data["username"],
            address=validated_data.get("address", None),
            phone=validated_data.get("phone", None),
            birth_date=validated_data.get("birth_date", None),
            gender=validated_data.get("gender", None),
            drivers_license_status=validated_data.get("drivers_license_status", False),
            is_active=validated_data.get('is_active', True),
            employee_type_id=validated_data["employee_type"]
        )
        # PW
        if validated_data.get("password", None) is not None:
            validate_password(validated_data["password"], obj)
            obj.set_password(validated_data["password"])
        else:
            raise IntegrityError("Password is required")

        # save and add groups
        obj.save()
        obj.groups.add(*requested_groups)

        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `Employee` instance, given the validated data.
        """
        groups_to_add = []
        for attr, value in validated_data.items():
            if attr == "password":
                validate_password(validated_data["password"], instance)
                instance.set_password(value)
            elif attr == "groups" and value is not None:
                groups_to_add += Group.objects.filter(pk__in=value)
                #if len(value) != len(groups_to_add):
                    #raise serializers.ValidationError("Invalid group id included")
            elif attr == "employee_type" and value is not None:
                instance.employee_type_id = value
            elif value is not None:
                setattr(instance, attr, value)
        instance.save()
        instance.groups.clear()
        instance.groups.add(*groups_to_add)
        return instance


def manual_employee_serializer(data: models.Employee):
    """
    Manual serializer for Employee
    """
    group_list = [{"id": group.pk, "name": group.name} for group in data.groups.all()]
    if data.employee_type is None:
        employee_type = None
    else:
        employee_type = {
            "id": data.employee_type.pk,
            "title": data.employee_type.title,
            "description": data.employee_type.description
        }
    return {
        "id": data.pk,
        "username": data.username,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "password": None,
        "groups": group_list,
        "is_active": data.is_active,
        "employee_type": employee_type,
        "address": data.address,
        "phone": data.phone,
        "birth_date": data.birth_date,
        "gender": data.gender,
        "drivers_license_status": data.drivers_license_status,
        "has_image": data.pfp_name is not None
    }


class TaskTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for TaskType
    """
    class Meta:
        model = models.TaskType
        fields = "__all__"


class TaskStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for TaskStatus
    """
    class Meta:
        model = models.TaskStatus
        fields = "__all__"


class VehicleTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for VehicleType
    """
    class Meta:
        model = models.VehicleType
        fields = "__all__"


# optimized
class TaskSerializer(serializers.Serializer):
    """
    Serializer for Task
    """
    title = serializers.CharField(required=True)
    task_type = serializers.IntegerField(required=True)
    task_status = serializers.IntegerField(required=True)
    vehicles = IntegerListField(required=True, allow_empty=True)
    # images = IntegerListField(required=False, allow_empty=True)
    order = serializers.IntegerField(required=True)
    employees = IntegerListField(required=True, allow_empty=True)
    scheduled_from = serializers.DateTimeField(required=True)
    from_shift = serializers.CharField(required=True)
    scheduled_to = serializers.DateTimeField(required=True)
    to_shift = serializers.CharField(required=True)

    def create(self, validated_data):
        """
        Create and return a new `Task` instance, given the validated data.
        """
        emp = models.Employee.objects.filter(pk__in=validated_data["employees"])
        if len(validated_data["employees"]) != len(emp):
            raise IntegrityError("Invalid employee id included")
        vh = models.Vehicle.objects.filter(pk__in=validated_data["vehicles"])
        if len(validated_data["vehicles"]) != len(vh):
            raise IntegrityError("Invalid vehicle id included")

        obj = models.Task.objects.create(
            title=validated_data["title"],
            scheduled_from=validated_data["scheduled_from"],
            from_shift=validated_data["from_shift"],
            scheduled_to=validated_data["scheduled_to"],
            to_shift=validated_data["to_shift"],
            task_type_id=validated_data["task_type"],
            task_status_id=validated_data["task_status"],
            order_id=validated_data["order"]
        )
        obj.employees.add(*emp)
        obj.vehicles.add(*vh)
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `Task` instance, given the validated data.
        """
        employees_to_add = []
        vehicles_to_add = []
        for attr, value in validated_data.items():
            if attr == "task_type" and value is not None:
                instance.task_type_id = value
            elif attr == "task_status" and value is not None:
                instance.task_status_id = value
            elif attr == "order" and value is not None:
                instance.order_id = value
            elif attr == "employees" and value is not None:
                res = models.Employee.objects.filter(pk__in=value)
                if len(value) != len(res):
                    raise serializers.ValidationError("Invalid employee id included")
                employees_to_add += res
            elif attr == "vehicles" and value is not None:
                res = models.Vehicle.objects.filter(pk__in=value)
                if len(value) != len(res):
                    raise serializers.ValidationError("Invalid vehicle id included")
                vehicles_to_add += res
            elif value is not None:
                setattr(instance, attr, value)
        instance.save()
        instance.employees.clear()
        instance.employees.add(*employees_to_add)
        instance.vehicles.clear()
        instance.vehicles.add(*vehicles_to_add)
        return instance


def manual_task_serializer(data: models.Task):
    """
    Manual serializer for Task
    """
    emp_list = [{"id": emp.pk, "username": "%s %s" % (emp.first_name, emp.last_name)} for emp in data.employees.all()]
    vh_list = [{"id": vh.pk, "title": vh.title} for vh in data.vehicles.all()]
    img_list = [{"id": img.pk, "title": img.image_name} for img in data.images.all()]
    return {
        "id": data.pk,
        "title": data.title,
        "task_type": {
            "id": data.task_type.pk,
            "title": data.task_type.title
        },
        "task_status": {
            "id": data.task_status.pk,
            "title": data.task_status.title
        },
        "order": {
            "id": data.order.pk,
            "order_nr": data.order.order_nr,
            "title": data.order.title,
            "order_date": data.order.order_date,
            "customer": {
                "id": data.order.customer.pk,
                "name": data.order.customer.name,
                "address": data.order.customer.address,
                "phone": data.order.customer.phone,
                "is_company": data.order.customer.is_company
            },
            "is_completed": data.order.is_completed
        },
        "employees": emp_list,
        "vehicles": vh_list,
        "images": img_list,
        "scheduled_from": data.scheduled_from,
        "from_shift": data.from_shift,
        "scheduled_to": data.scheduled_to,
        "to_shift": data.to_shift
    }


def manual_task_serializer_minimal(data: models.Task):
    """
    To provide an option for less data transfer (e.g. list view)
    :param data:
    :return:
    """
    return {
        "id": data.pk,
        "title": data.title,
        "task_type": data.task_type.title,
        "task_status": data.task_status.title,
        "scheduled_to": data.scheduled_to,
    }
