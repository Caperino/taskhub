"""
URL configuration for TaskHub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import taskhub_api.views
from taskhub_api import views as available_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # JWT Token URLs
    path('api/', available_views.ApiView.as_view({'get': "list"})),
    path('api/token/', taskhub_api.views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # IMAGE ENDPOINTS
    path('api/users/<user_pk>/image',
         available_views.ImageUploadViewSet.as_view({"get": "download_pfp", "post": "upload_pfp", "delete": "delete_pfp"}),
         name="direct_pfp"),
    path('api/tasks/<task_pk>/images',
         available_views.ImageUploadViewSet.as_view({"post": "upload_task_image"}),
         name="direct_task_image_upload"),
    path('api/tasks/<task_pk>/images/<image_pk>',
         available_views.ImageUploadViewSet.as_view({"get": "download_task_image", "delete": "delete_task_image"}),
         name="direct_task_image"),
    # CUSTOMER
    path('api/customers',
         available_views.CustomerViewSet.as_view({"get": "list", "post": "create"}),
         name="customers"),
    path('api/customers/<pk_customer>',
         available_views.CustomerViewSet.as_view({"get": "retrieve", "put": "update", "delete": "delete"}),
         name="direct_customer"),
    # EMPLOYEE
    path('api/employees',
         available_views.EmployeeViewSet.as_view({"get": "list", "post": "create"}),
         name="employees"),
    path('api/employees/<employee_pk>',
         available_views.EmployeeViewSet.as_view({"get": "retrieve", "put": "update", "delete": "delete"}),
         name="direct_employee"),
    # EMPLOYEE TYPES
    path('api/employeetypes',
         available_views.EmployeeTypeViewSet.as_view({"get": "list"}),
         name="employee_types"),
    # EMPLOYEE GROUPS
    path('api/employeegroups',
         available_views.EmployeeGroupViewSet.as_view({"get": "list"}),
         name="employee_groups"),
    # VEHICLE TYPES
    path('api/vehicletypes',
         available_views.VehicleTypeViewSet.as_view({"get": "list"}),
         name="vehicle_types"),
    path('api/vehicletypes/<pk_vehicle_type>',
         available_views.VehicleTypeViewSet.as_view({"get": "retrieve"}),
         name="direct_vehicle_type"),
    path('api/vehicles',
         available_views.VehicleViewSet.as_view({"get": "list", "post": "create"}),
         name="vehicles"),
    path('api/vehicles/<pk_vehicle>',
         available_views.VehicleViewSet.as_view({"get": "retrieve", "put": "update", "delete": "delete"}),
         name="direct_vehicle"),
    # TASK TYPES
    path('api/tasktypes',
         available_views.TaskTypeViewSet.as_view({"get": "list"}),
         name="task_types"),
    path('api/tasktypes/<pk_task_type>',
         available_views.TaskTypeViewSet.as_view({"get": "retrieve"}),
         name="direct_task_type"),
    path('api/taskstatuses',
         available_views.TaskStatusViewSet.as_view({"get": "list"}),
         name="task_statuses"),
    path('api/taskstatuses/<pk_task_status>',
         available_views.TaskStatusViewSet.as_view({"get": "retrieve"}),
         name="direct_task_status"),
    path('api/tasks',
         available_views.TaskViewSet.as_view({"get": "list", "post": "create"}),
         name="tasks"),
    path('api/tasks/<pk_task>',
         available_views.TaskViewSet.as_view({"get": "retrieve", "put": "update", "delete": "delete"}),
         name="direct_task"),
    # ORDERS
    path('api/orders',
         available_views.OrderViewSet.as_view({"get": "list", "post": "create"}),
         name="orders"),
    path('api/orders/<pk_order>',
         available_views.OrderViewSet.as_view({"get": "retrieve", "put": "update", "delete": "delete"}),
         name="direct_order"),

    # health checks
    # TODO: add funny health checks
]
