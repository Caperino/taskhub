# External imports
import string

from django.db.models import Q
from django.shortcuts import render
import re
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import django.db.models as django_models
from django.db import IntegrityError
import random

# TaskHub imports
from TaskHub import urls
from . import renderers
from . import azure, models, constants, serializers


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
        return None


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
        customer = get_object_or_404(models.Customer, pk=pk_customer)
        return Response(serializers.CustomerSerializer(customer).data)

    def create(self, request):
        """
        Creates a new customer
        :param request:
        :return:
        """
        ser = serializers.CustomerSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.validated_data, status=201)
        else:
            return Response(ser.errors, status=400)

    def update(self, request, pk_customer):
        """
        Updates a customer
        :param request:
        :param pk:
        :return:
        """
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
        order_by = request.GET.get("order") if request.GET.get("order") in ["first_name", "last_name", "employee_type", "phone", "email", "is_active"] else "last_name"
        order_dir = request.GET.get("order_dir") if request.GET.get("order_dir") in ["asc", "desc"] else "asc"
        query_string = request.GET.get("query", "")
        employees = models.Employee.objects.filter(Q(first_name__icontains=query_string) | Q(last_name__icontains=query_string)).order_by("%s%s" % ("" if order_dir == "asc" else "-", order_by))
        return_employee_list = []
        for employee in employees:
            return_employee_list.append(serializers.manual_employee_serializer(employee))
        return Response(return_employee_list, status=200)

    def retrieve(self, request, pk=None):
        pass

    def create(self, request):
        """
        Creates a new employee
        :param request: the request
        :return:
        """
        ser = serializers.EmployeeSerializer(data=request.data)
        if ser.is_valid():
            try:
                ser.save()
            except IntegrityError as e:
                print(e)
                return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(status="error", message="username or email already exists")).data, status=400)
            return Response(ser.validated_data, status=201)
        else:
            return Response(ser.errors, status=400)

    def update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass


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
        :param request:
        :param user_pk:
        :return:
        """
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
                return Response(serializers.TaskHubApiResponseSerializer(models.TaskHubApiResponse(message="file uploaded to storage")).data, status=500)

    def download_task_image(self, request, task_pk, image_pk):
        """
        Downloads a task image from Azure Blob Storage
        :param image_pk: the primary key of the image
        :param task_pk: the primary key of the task
        :param request: the request
        :return:
        """
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


class TaskViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving tasks.
    """

    def list(self, request):
        # safely get begin and end date for request
        begin = to_date(request.GET.get("begin", ""))
        end = to_date(request.GET.get("end", ""))
        if begin is None:
            begin = datetime.today() - timedelta(weeks=1)
        if end is None:
            end = datetime.today() + timedelta(weeks=3)

    def retrieve(self, request, pk=None):
        pass

    def create(self, request):
        pass

    def update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass
