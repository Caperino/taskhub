# External imports
import string
import traceback

from django.db.models import Q
from django.contrib.auth.models import Group
from django.shortcuts import render
import re
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import django.db.models as django_models
from rest_framework import serializers as drf_serializers
import random

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# TaskHub imports
from TaskHub import urls
from . import renderers
from . import azure, models, constants, serializers

# DOCS
# https://docs.djangoproject.com/en/4.2/ref/models/querysets/


# Helpers
def get_unique_string(in_string: str, size: int = 6, chars: str = string.ascii_uppercase + string.digits) -> str:
    """
    Generates a unique string from a given string
    :param in_string: the string to generate from
    :param size: how many characters to generate
    :param chars: which characters to use
    :return: the unique string
    """
    return "%s_%s" % (in_string, ''.join(random.choice(chars) for _ in range(size)))


def validate_image_upload_type(file_name: str) -> bool:
    """
    Validates the image upload type by extension (not by content)
    :param file_name: the name to validate
    :return: True if valid, False if not
    """
    if not file_name.split(".")[-1].lower() in constants.VALID_IMAGE_EXTENSIONS:
        return False
    return True


def to_date(date_string: str) -> datetime | None:
    """
    Converts a date string to a datetime object
    :param date_string: the date string
    :return: the datetime object
    """
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except:
        print("Invalid date string: " + date_string)
        return None


def authorize_action(request, necessary_groups: list) -> constants.AuthorisationError | None:
    """
    Authorizes an action (i.e. endpoint) for a user
    :param necessary_groups: all possible groups that have access to this endpoint
    :param request: the request
    :return: True if authorized, False if not
    """
    return None
    if request.user.is_authenticated:
        status = False
        for group in request.user.groups.all():
            if group.name in necessary_groups:
                status = True
                break
        return None if status else constants.AuthorisationError.FORBIDDEN
    else:
        return constants.AuthorisationError.UNAUTHORIZED


def authorize_action_advanced(request, necessary_groups: list, pks: list = []) -> constants.AuthorisationError | None:
    """
    Authorizes an action (i.e. endpoint) for a user
    :param pks: a dynamically generated list of users who are allowed to access this endpoint in addition to the groups
    :param necessary_groups: all possible groups that have access to this endpoint
    :param request: the request
    :return: True if authorized, False if not

    Receiver Code:
    match authorize_action_advanced(request, list(constants.UserGroups.ADMINISTRATOR.value)):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
    """
    #return None
    # Basic Authenticated Check
    if request.user.is_authenticated:
        # Check for access via group (adm, man, sup)
        status = False
        print(necessary_groups)
        for group in request.user.groups.all():
            print(group.name)
            if group.name in necessary_groups:
                status = True
                break
        # Check for access via user (e.g. employee can only access his own profile)
        if not status:
            for pk in pks:
                if request.user.pk == pk:
                    status = True
                    break
        return None if status else constants.AuthorisationError.FORBIDDEN
    else:
        return constants.AuthorisationError.UNAUTHORIZED


class ApiView(viewsets.ViewSet):
    """
    A simple ViewSet for listing all available endpoints.
    """

    def list(self, request):
        endpoints = []
        for pattern in urls.urlpatterns:
            endpoint = str(pattern.pattern)
            # Include only api/ views and include only top-level endpoints:
            if "api/" in endpoint and re.search("<.*>", endpoint) is None:
                endpoints.append("http://localhost:8000/%s" % endpoint)
        return Response(endpoints)


class CustomerViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving costumers.
    """
    # TODO: SECURITY
    def list(self, request):
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value, constants.UserGroups.SUPERVISOR.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        is_company: str = request.GET.get("company", "")
        query_string = request.GET.get("query", "")
        if is_company.lower() == "true":
            customers = models.Customer.objects.filter(name__icontains=query_string, is_company=True)
        elif is_company.lower() == "false":
            customers = models.Customer.objects.filter(name__icontains=query_string, is_company=False)
        else:
            customers = models.Customer.objects.filter(name__icontains=query_string)
        return Response(serializers.CustomerSerializer(customers, many=True).data)

    def retrieve(self, request, pk_customer):
        """
        Retrieves a customer
        :param request:
        :param pk_customer:
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value, constants.UserGroups.SUPERVISOR.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        customer = get_object_or_404(models.Customer, pk=pk_customer)
        return Response(serializers.CustomerSerializer(customer).data)

    def create(self, request):
        """
        Creates a new customer
        :param request:
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        ser = serializers.CustomerSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.validated_data, status=201)
        else:
            return Response(ser.errors, status=400)

    def update(self, request, pk_customer):
        """
        Updates a customer
        :param request: the request
        :param pk_customer: the id of the requested customer
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        customer = get_object_or_404(models.Customer, pk=pk_customer)
        ser = serializers.CustomerSerializer(customer, data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.validated_data, status=200)
        else:
            return Response(ser.errors, status=400)

    def delete(self, request, pk_customer):
        """
        Deletes a customer
        :param pk_customer: the primary key of the customer
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        customer = get_object_or_404(models.Customer, pk=pk_customer)
        try:
            customer.delete()
            return Response(None, status=204)
        except django_models.ProtectedError as e:
            print(e)
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="customer has still orders assigned")).data, status=400)
        except Exception as e:
            print(e)
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="an unforeseen error happened, please try again")).data, status=500)


class EmployeeTypeViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving employee types.
    """

    def list(self, request):
        """
        Lists all employee types
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request,
                                        [constants.UserGroups.EMPLOYEE.value, constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass

        return Response(serializers.EmployeeTypeSerializer(models.EmployeeType.objects.all(), many=True).data)


class EmployeeGroupViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving employee groups.
    """

    def list(self, request):
        """
        Lists all employee groups
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request,
                                        [constants.UserGroups.EMPLOYEE.value, constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass

        return Response(serializers.EmployeeGroupSerializer(Group.objects.all(), many=True).data)


class EmployeeViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving employees.
    """
    # TODO: SECURITY
    def list(self, request):
        """
        Lists all employees
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.ADMINISTRATOR.value, constants.UserGroups.MANAGER.value, constants.UserGroups.SUPERVISOR.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass

        order_by = request.GET.get("order") if request.GET.get("order") in ["first_name", "last_name", "employee_type", "phone", "email", "is_active"] else "last_name"
        order_dir = request.GET.get("order_dir") if request.GET.get("order_dir") in ["asc", "desc"] else "asc"
        query_string = request.GET.get("query", "")
        employees = models.Employee.objects.filter(Q(first_name__icontains=query_string) | Q(last_name__icontains=query_string)).order_by("%s%s" % ("" if order_dir == "asc" else "-", order_by))
        return_employee_list = []
        for employee in employees:
            return_employee_list.append(serializers.manual_employee_serializer(employee))
        return Response(return_employee_list, status=200)

    def retrieve(self, request, employee_pk):
        """
        Retrieves an employee
        :param request: the request
        :param employee_pk: the primary key of the employee
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.ADMINISTRATOR.value, constants.UserGroups.MANAGER.value, constants.UserGroups.SUPERVISOR.value], [int(employee_pk)]):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        employee = get_object_or_404(models.Employee, pk=employee_pk)
        return Response(serializers.manual_employee_serializer(employee), status=200)

    def create(self, request):
        """
        Creates a new employee
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.ADMINISTRATOR.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        ser = serializers.EmployeeSerializer(data=request.data)
        if ser.is_valid():
            try:
                emp = ser.save()
            except Exception as e:
                return Response(e.args, status=400)
            return Response(serializers.manual_employee_serializer(emp), status=201)
        else:
            return Response(ser.errors, status=400)

    def update(self, request, employee_pk):
        """
        Updates an employee
        :param request: the request
        :param employee_pk: the primary key of the employee
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.ADMINISTRATOR.value], [int(employee_pk)]):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        employee = get_object_or_404(models.Employee, pk=employee_pk)
        ser = serializers.EmployeeSerializer(employee, data=request.data, partial=True)
        if ser.is_valid():
            try:
                if request.user.pk == int(employee_pk) and not "1" in ser.validated_data['groups']:
                    ser.validated_data['groups'].append("1")
                emp = ser.save()
            except Exception as e:
                print(e)
                if 'FOREIGN KEY' in str(e.args[0]):
                    return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message='invalid association found')).data, status=400)
                elif 'This password is too short' in str(e.args[0]):
                    return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message='password too short')).data, status=400)
                else:
                    return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message='username or mail already exists')).data, status=400)
            return Response(serializers.manual_employee_serializer(emp), status=200)
        else:
            return Response(ser.errors, status=400)

    def delete(self, request, employee_pk):
        """
        Deletes an employee
        :param request: the request
        :param employee_pk: the primary key of the employee
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.ADMINISTRATOR.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        if request.user.pk == int(employee_pk):
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="you can't delete yourself")).data, status=418)
        try:
            models.Employee.objects.filter(pk=employee_pk).delete()
            return Response(None, status=204)
        except django_models.ProtectedError as e:
            print(e)
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="employee has still tasks assigned")).data, status=400)
        except Exception as e:
            print(e)
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="an unforeseen error happened, please try again")).data, status=500)


class ImageUploadViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for uploading images.

    File Properties:
    file = request.FILES['filename']
    file.name           # Gives name
    file.content_type   # Gives Content type text/html etc
    file.size           # Gives file's size in byte
    file.read()         # Reads file

    Iterate over Multi-Uploads:
    for file in request.FILES.getlist('file'):
        print(file.name)
        print(file.size)
        print(file.content_type)
        print(file.read())
    """
    renderer_classes = [renderers.PNGRenderer, renderers.JPEGRenderer, JSONRenderer]

    def download_pfp(self, request, user_pk):
        """
        Downloads a profile picture from Azure Blob Storage
        :param request: the request
        :param user_pk: the primary key of the user
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.EMPLOYEE.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        em = get_object_or_404(models.Employee, pk=user_pk)
        if em.pfp_name is None:
            return Response({"status": "no profile picture"}, status=404)
        else:
            try:
                c = azure.download_profile_picture(em.pfp_name.image_name)
                return Response(c, status=200)
            except Exception as e:
                print(e)
                # TODO: mail notification
                return Response({"status": "error"}, status=500)

    def upload_pfp(self, request, user_pk):
        """
        Uploads a profile picture to Azure Blob Storage
        :param user_pk: the primary key of the user
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.ADMINISTRATOR.value], [int(user_pk)]):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        em = get_object_or_404(models.Employee, pk=user_pk)
        for file in request.FILES.getlist('upload'):
            if file.size > 3000000:
                return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="file too large")).data, status=400)
            elif not validate_image_upload_type(file.name):
                return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="invalid file type")).data, status=400)

            # read file and create AzureImage
            c = file.read()
            un_name = get_unique_string(file.name)
            azure.upload_profile_picture(un_name, c)
            az_img = models.AzureImage.objects.create(image_name=un_name)

            # exchange old image with new one and delete old one
            if em.pfp_name is not None:
                try:
                    azure.delete_profile_picture(em.pfp_name.image_name)
                    em.pfp_name.delete()
                except Exception as e:
                    print(e)
                    # TODO: mail notification
            em.pfp_name = az_img

            # save changes in Employee
            em.save()

            # logging and response
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(message="file uploaded to storage")).data, status=201)
        return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="no file detected")).data, status=400)

    def delete_pfp(self, request, user_pk):
        """
        Deletes a profile picture from Azure Blob Storage
        :param user_pk: the primary key of the user
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.ADMINISTRATOR.value], [int(user_pk)]):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        em = get_object_or_404(models.Employee, pk=user_pk)
        if em.pfp_name is None:
            return Response(None, status=204)
        else:
            try:
                azure.delete_profile_picture(em.pfp_name.image_name)
                em.pfp_name.delete()
                return Response(None, status=204)
            except Exception as e:
                print(e)
                # TODO: mail notification
                return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(message="error ocurred when deleting image")).data, status=500)

    def download_task_image(self, request, task_pk, image_pk):
        """
        Downloads a task image from Azure Blob Storage
        :param image_pk: the primary key of the image
        :param task_pk: the primary key of the task
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.EMPLOYEE.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        try:
            selected_image = models.Task.objects.get(pk=task_pk).images.get(pk=image_pk)
        except Exception as e:
            print(e)
            return Response({"status": "image not found"}, status=404)

        try:
            c = azure.download_task_image(selected_image.image_name)
            return Response(c, status=200)
        except Exception as e:
            print(e)
            # TODO: mail notification
            return Response({"status": "error"}, status=500)

    def upload_task_image(self, request, task_pk):
        """
        Uploads a task image to Azure Blob Storage
        :param task_pk: the primary key of the task
        :param request: the request
        :return:
        """
        try:
            task = models.Task.objects.get(pk=task_pk)
        except Exception as e:
            print(e)
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="task not found")).data, status=404, content_type="application/json")
        # SECURITY DEBUG UNFINISHED
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], task.employees.all().values_list("pk", flat=True)):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass

        count = 0
        uploaded_files: list = []
        for file in request.FILES.getlist('upload'):
            count += 1
            if file.size > 3000000:
                task.save()
                return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="file too large, already uploaded: " + " ".join(uploaded_files))).data, status=400, content_type="application/json")
            elif not validate_image_upload_type(file.name):
                task.save()
                return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="invalid file type, already uploaded: " + " ".join(uploaded_files))).data, status=400, content_type="application/json")

            # read file and create AzureImage
            c = file.read()
            un_name = get_unique_string(file.name)
            azure.upload_task_image(un_name, c)
            az_img = models.AzureImage.objects.create(image_name=un_name)

            # add image object to task
            task.images.add(az_img)
            uploaded_files.append(file.name)

        if count is 0:
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="no images detected")).data, status=400, content_type="application/json")
        # save changes in Task
        task.save()
        return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(message="%d images uploaded" % count)).data, status=201, content_type="application/json")

    def delete_task_image(self, request, task_pk, image_pk):
        """
        Deletes a profile picture from Azure Blob Storage
        :param image_pk: the primary key of the image
        :param task_pk: the primary key of the task
        :param request: the request
        :return:
        """
        try:
            task = get_object_or_404(models.Task, pk=task_pk)
            # Security
            match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value],
                                            task.employees.all().values_list("pk", flat=True)):
                case constants.AuthorisationError.FORBIDDEN:
                    return Response(serializers.TaskHubApiResponseSerializer(
                        models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
                case constants.AuthorisationError.UNAUTHORIZED:
                    return Response(serializers.TaskHubApiResponseSerializer(
                        models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
                case None:
                    pass
            imgs = task.images.filter(pk=image_pk)
            if imgs.count() != 1:
                return Response(None, status=404)
            selected_image = imgs[0]
            azure.delete_task_image(selected_image.image_name)
            task.images.remove(selected_image)
            selected_image.delete()
            return Response(None, status=204)
        except Exception as e:
            print(e)
            # TODO: mail notification
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="image deletion failed")).data, status=500)


class TaskTypeViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving task types.
    """

    def list(self, request):
        """
        Lists all task types
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.EMPLOYEE.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass
        return Response(serializers.TaskTypeSerializer(models.TaskType.objects.all(), many=True).data)

    def retrieve(self, request, pk_task_type):
        """
        Retrieves a task type
        :param request: the request
        :param pk_task_type: the primary key of the task type
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.EMPLOYEE.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass
        task_type = get_object_or_404(models.TaskType, pk=pk_task_type)
        return Response(serializers.TaskTypeSerializer(task_type).data)


class TaskStatusViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving task statuses.
    """

    def list(self, request):
        """
        Lists all task statuses
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.EMPLOYEE.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass
        return Response(serializers.TaskStatusSerializer(models.TaskStatus.objects.all(), many=True).data)

    def retrieve(self, request, pk_task_status):
        """
        Retrieves a task status
        :param request: the request
        :param pk_task_status: the primary key of the task status
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.EMPLOYEE.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass
        task_status = get_object_or_404(models.TaskStatus, pk=pk_task_status)
        return Response(serializers.TaskStatusSerializer(task_status).data)


class VehicleTypeViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving vehicle types.
    """

    def list(self, request):
        """
        Lists all vehicle types
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.EMPLOYEE.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass
        return Response(serializers.VehicleTypeSerializer(models.VehicleType.objects.all(), many=True).data)

    def retrieve(self, request, pk_vehicle_type):
        """
        Retrieves a vehicle type
        :param request: the request
        :param pk_vehicle_type: the primary key of the vehicle type
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.EMPLOYEE.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass
        vehicle_type = get_object_or_404(models.VehicleType, pk=pk_vehicle_type)
        return Response(serializers.VehicleTypeSerializer(vehicle_type).data)


class VehicleViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving vehicles.
    """

    def list(self, request):
        """
        Lists all vehicles
        :param request: the request
        :return:
        """
        filters = {
            "vehicle_type__pk": request.GET.get("type", None),
            "title__icontains": request.GET.get("title", None),
            "max_load_length__gte": request.GET.get("length", None),
            "max_load_weight__gte": request.GET.get("weight", None)
        }
        for key in ("vehicle_type__pk", "max_load_length__gte", "max_load_weight__gte"):
            v = filters[key]
            if v is not None:
                try:
                    filters[key] = int(v)
                except:
                    filters[key] = None
        filters = {k: v for k, v in filters.items() if v is not None}

        match authorize_action_advanced(request, [constants.UserGroups.EMPLOYEE.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass

        vehicles = models.Vehicle.objects.filter(**filters).order_by("title")
        vehicles_serialized = []
        for vehicle in vehicles:
            vehicles_serialized.append(serializers.manual_vehicle_serializer(vehicle))
        return Response(vehicles_serialized)

    def retrieve(self, request, pk_vehicle):
        """
        Retrieves a vehicle
        :param request: the request
        :param pk_vehicle: the primary key of the vehicle
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.EMPLOYEE.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass
        vehicle = get_object_or_404(models.Vehicle, pk=pk_vehicle)
        return Response(serializers.manual_vehicle_serializer(vehicle))

    def create(self, request):
        """
        Creates a new vehicle
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass

        ser = serializers.VehicleSerializer(data=request.data)
        if ser.is_valid():
            try:
                ser.save()
            except Exception as e:
                return Response(e.args, status=400)
            return Response(ser.validated_data, status=201)
        else:
            return Response(ser.errors, status=400)

    def update(self, request, pk_vehicle):
        """
        Updates a vehicle
        :param request: the request
        :param pk_vehicle: the primary key of the vehicle
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass

        vehicle = get_object_or_404(models.Vehicle, pk=pk_vehicle)
        ser = serializers.VehicleSerializer(vehicle, data=request.data, partial=True)
        if ser.is_valid():
            try:
                ser.save()
            except Exception as e:
                return Response(e.args, status=400)
            return Response(ser.validated_data, status=200)
        else:
            return Response(ser.errors, status=400)

    def delete(self, request, pk_vehicle):
        """
        Deletes a vehicle
        :param request: the request
        :param pk_vehicle: the primary key of the vehicle
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass

        try:
            models.Vehicle.objects.filter(pk=pk_vehicle).delete()
            return Response(None, status=204)
        except django_models.ProtectedError as e:
            print(e)
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="vehicle has still tasks assigned")).data, status=400)
        except Exception as e:
            print(e)
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="an unforeseen error happened, please try again")).data, status=500)


class OrderViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving orders.
    """

    def list(self, request):
        """
        Lists all orders
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value, constants.UserGroups.SUPERVISOR.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass
        orders = models.Order.objects.all()
        output = []
        for order in orders:
            output.append(serializers.manual_order_serializer(order))
        return Response(output)

    def retrieve(self, request, pk_order):
        """
        Retrieves an order
        :param request: the request
        :param pk_order: the primary key of the order
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value, constants.UserGroups.SUPERVISOR.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass
        order = get_object_or_404(models.Order, pk=pk_order)
        return Response(serializers.manual_order_serializer(order))

    def create(self, request):
        """
        Creates a new order
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass

        ser = serializers.OrderSerializer(data=request.data)
        if ser.is_valid():
            try:
                ser.save()
            except Exception as e:
                return Response(e.args, status=400)
            return Response(ser.validated_data, status=201)
        else:
            return Response(ser.errors, status=400)

    def update(self, request, pk_order):
        """
        Updates an order
        :param request: the request
        :param pk_order: the primary key of the order
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass

        order = get_object_or_404(models.Order, pk=pk_order)
        ser = serializers.OrderSerializer(order, data=request.data, partial=True)
        if ser.is_valid():
            try:
                ser.save()
            except Exception as e:
                return Response(e.args, status=400)
            return Response(ser.validated_data, status=200)
        else:
            return Response(ser.errors, status=400)

    def delete(self, request, pk_order):
        """
        Deletes an order
        :param request: the request
        :param pk_order: the primary key of the order
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass

        try:
            models.Order.objects.filter(pk=pk_order).delete()
            return Response(None, status=204)
        except django_models.ProtectedError as e:
            print(e)
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="order has still tasks assigned")).data, status=400)
        except Exception as e:
            print(e)
            return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="an unforeseen error happened, please try again")).data, status=500)


class TaskViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving tasks.
    """

    def list(self, request):
        match authorize_action_advanced(request, [constants.UserGroups.EMPLOYEE.value, constants.UserGroups.MANAGER.value, constants.UserGroups.SUPERVISOR.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(
                        models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(
                        models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass
        # safely get begin and end date for request
        begin = to_date(request.GET.get("begin", ""))
        end = to_date(request.GET.get("end", ""))
        if begin is None:
            begin = datetime.today() - timedelta(weeks=1)
        if end is None:
            end = datetime.today() + timedelta(weeks=3)
        g = request.user.groups.filter(name__in=(constants.UserGroups.MANAGER.value, constants.UserGroups.SUPERVISOR.value))
        if g.count() == 1:
            print("manager access")
            emp_filter = 'INVALID_DATA'
        else:
            print("employee access")
            emp_filter = request.user.pk
        task_filter = {
            "employees__pk": emp_filter,
            "scheduled_to__gte": begin,
            "scheduled_to__lte": end
        }
        filters = {k: v for k, v in task_filter.items() if v != 'INVALID_DATA' and v is not None}
        tasks = models.Task.objects.filter(**filters)
        output = []
        for task in tasks:
            output.append(serializers.manual_task_serializer_minimal(task))
        return Response(output)

    def retrieve(self, request, pk_task):
        """
        Retrieves a task
        :param request: the request
        :param pk_task: the primary key of the task
        :return:
        """
        task_filter = {
            "pk": pk_task
        }
        filters = task_filter
        tasks = models.Task.objects.filter(**filters)
        if tasks.count() != 1:
            return Response(None, status=404)

        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value, constants.UserGroups.SUPERVISOR.value], tasks[0].employees.all().values_list("pk", flat=True)):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="forbidden")).data,
                    status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(
                    serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="unauthorized")).data,
                    status=401)
            case None:
                pass
        return Response(serializers.manual_task_serializer(tasks[0]))

    def create(self, request):
        """
        Creates a new task
        :param request: the request
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass

        ser = serializers.TaskSerializer(data=request.data)
        if ser.is_valid():
            try:
                if ser.validated_data['scheduled_from'] > ser.validated_data['scheduled_to']:
                    return Response({"time span": "begin after end detected"}, status=400)
                elif ser.validated_data['from_shift'] not in ("am", "pm") or ser.validated_data['to_shift'] not in ("am", "pm"):
                    return Response({"from_shift or to_shift": "invalid input detected, please only use 'am' or 'pm'"}, 400)
                ser.save()
            except Exception as e:
                return Response(e.args, status=400)
            return Response(ser.validated_data, status=201)
        else:
            return Response(ser.errors, status=400)

    def update(self, request, pk_task):
        """
        Updates a task
        :param request: the request
        :param pk_task: the primary key of the task
        :return:
        """
        task = get_object_or_404(models.Task, pk=pk_task)
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], task.employees.all().values_list("pk", flat=True)):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass

        ser = serializers.TaskSerializer(task, data=request.data, partial=True)
        if ser.is_valid():
            try:
                if 'scheduled_from' in ser.validated_data:
                    fr = ser.validated_data['scheduled_from']
                else:
                    fr = None
                if 'scheduled_to' in ser.validated_data:
                    to = ser.validated_data['scheduled_to']
                else:
                    to = None

                if fr is not None and to is not None:
                    if ser.validated_data['scheduled_from'] > ser.validated_data['scheduled_to']:
                        return Response({"time span": "begin after end detected"}, status=400)
                elif fr is not None and fr > task.scheduled_to:
                    return Response({"time span": "begin after end detected"}, status=400)
                elif to is not None and task.scheduled_from > to:
                    return Response({"time span": "begin after end detected"}, status=400)

                if 'from_shift' in ser.validated_data and ser.validated_data['from_shift'] not in ("am", "pm"):
                    return Response(
                        {"from_shift": "invalid input detected, please only use 'am' or 'pm'"}, 400)
                elif 'to_shift' in ser.validated_data and ser.validated_data['to_shift'] not in ("am", "pm"):
                    return Response(
                        {"to_shift": "invalid input detected, please only use 'am' or 'pm'"}, 400)
                ser.save()
            except Exception as e:
                print(e.args)
                if 'FOREIGN KEY' in str(e.args[0]):
                    return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message='invalid association found')).data, status=400)
                elif 'UNIQUE' in str(e.args[0]):
                    return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message='task already exists')).data, status=400)
                else:
                    return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message=str(e.args[0]))).data, status=400)
            return Response(ser.validated_data, status=200)
        else:
            return Response(ser.errors, status=400)

    def delete(self, request, pk_task):
        """
        Deletes a task
        :param request: the request
        :param pk_task: the primary key of the task
        :return:
        """
        match authorize_action_advanced(request, [constants.UserGroups.MANAGER.value], []):
            case constants.AuthorisationError.FORBIDDEN:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="forbidden")).data, status=403)
            case constants.AuthorisationError.UNAUTHORIZED:
                return Response(serializers.TaskHubApiResponseSerializer(
                    models.TaskHubApiResponse(status="error", message="unauthorized")).data, status=401)
            case None:
                pass

        try:
            models.Task.objects.filter(pk=pk_task).delete()
            return Response(None, status=204)
        except Exception as e:
            print(e)
            return Response(serializers.TaskHubApiResponseSerializer(
                models.TaskHubApiResponse(
                    status="error",
                    message="an unforeseen error happened, please try again")).data,
                            status=500)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['groups'] = list(user.groups.all().values_list("name", flat=True))
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer