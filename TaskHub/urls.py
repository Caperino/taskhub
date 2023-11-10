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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Image Action URLs
    path('api/users/<user_pk>/image',
         available_views.ImageUploadViewSet.as_view({"get": "download_pfp", "post": "upload_pfp", "delete": "delete_pfp"}),
         name="direct_pfp"),
    path('api/tasks/<task_pk>/images',
         available_views.ImageUploadViewSet.as_view({"post": "upload_task_image"}),
         name="direct_task_image_upload"),
    path('api/tasks/<task_pk>/images/<image_pk>',
         available_views.ImageUploadViewSet.as_view({"get": "download_task_image", "delete": "delete_task_image"}),
         name="direct_task_image"),
    path('api/customers',
         available_views.CustomerViewSet.as_view({"get": "list", "post": "create"}),
         name="customers"),
    path('api/customers/<pk_customer>',
         available_views.CustomerViewSet.as_view({"get": "retrieve", "put": "update", "delete": "delete"}),
         name="direct_customer"),
]
