from django.contrib import admin

# Employee Model
from .models import *


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'last_name', 'employee_type', 'phone', 'email', 'is_active')
    list_filter = ('employee_type', 'is_active')
    search_fields = ('first_name', 'last_name', 'phone', 'email')


class AzureImageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'image_name')
    list_filter = ('image_name',)
    search_fields = ('image_name',)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('pk', 'task_type', 'task_status', 'order', 'scheduled_from', 'scheduled_to')
    list_filter = ('task_type', 'task_status', 'order')
    search_fields = ('task_type', 'task_status', 'order', 'pk')


class TaskTypeAdmin(admin.ModelAdmin):pass
class TaskStatusAdmin(admin.ModelAdmin):pass
class OrderAdmin(admin.ModelAdmin):pass


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'is_company')
    list_filter = ('is_company',)


class EmployeeTypeAdmin(admin.ModelAdmin):pass
class VehicleAdmin(admin.ModelAdmin):pass
class VehicleTypeAdmin(admin.ModelAdmin):pass


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(AzureImage, AzureImageAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskType, TaskTypeAdmin)
admin.site.register(TaskStatus, TaskStatusAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(EmployeeType, EmployeeTypeAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(VehicleType, VehicleTypeAdmin)
