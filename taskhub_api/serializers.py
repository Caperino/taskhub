from . import models
from rest_framework import serializers
from django.contrib.auth.models import Group
from django.db.utils import IntegrityError


class StringListField(serializers.ListField):
    child = serializers.CharField()

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
    birth_date = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    drivers_license_status = serializers.BooleanField(required=False, allow_null=True)

    def create(self, validated_data):
        """
        Create and return a new `Employee` instance, given the validated data.
        """
        # TODO: SECURITY for group assignment
        # TODO: PASSWORD handling is incomplete

        # EmployeeType
        requested_employee_type = models.EmployeeType.objects.filter(pk=validated_data["employee_type"]).first()
        if requested_employee_type is None:
            print("Invalid employee type id")
            raise IntegrityError("Invalid employee type id")
        # Groups
        requested_groups = Group.objects.filter(pk__in=validated_data["groups"])
        if len(validated_data["groups"]) != len(requested_groups):
            print("Invalid group id included")
            raise IntegrityError("Invalid group id included")

        obj = models.Employee.objects.create(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            username=validated_data["username"],
            address=validated_data["address"],
            phone=validated_data["phone"],
            birth_date=validated_data["birth_date"],
            gender=validated_data["gender"],
            drivers_license_status=validated_data["drivers_license_status"],
            is_active=validated_data["is_active"]
        )
        # PW
        if validated_data["password"] is not None:
            obj.set_password(validated_data["password"])
        else:
            raise IntegrityError("Password is required")
        # EmployeeType and Groups
        obj.employee_type = requested_employee_type
        [obj.groups.add(group) for group in requested_groups]

        obj.save()
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `Employee` instance, given the validated data.
        """
        for attr, value in validated_data.items():
            if attr == "password":
                instance.set_password(value)
            elif attr == "groups" and value is not None:
                groups = [group for group in Group.objects.filter(pk__in=value)]
                if len(value) != len(groups):
                    raise serializers.ValidationError("Invalid group id included")
                instance.groups.clear()
                [instance.groups.add(group) for group in groups]
            elif attr == "employee_type" and value is not None:
                res = models.EmployeeType.objects.filter(pk=value).first()
                if res is None:
                    raise serializers.ValidationError("Invalid employee type id")
                instance.employee_type = res
            elif value is not None:
                setattr(instance, attr, value)
        instance.save()
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
        "pk": data.pk,
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
        "drivers_license_status": data.drivers_license_status
    }
