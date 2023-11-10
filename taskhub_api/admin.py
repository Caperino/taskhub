from django.contrib import admin

# Employee Model
from .models import *


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'employee_type', 'phone', 'email', 'is_active')
    list_filter = ('employee_type', 'is_active')
    search_fields = ('first_name', 'last_name', 'phone', 'email')


class AzureImageAdmin(admin.ModelAdmin):pass
class TaskAdmin(admin.ModelAdmin):pass
class TaskTypeAdmin(admin.ModelAdmin):pass
class TaskStatusAdmin(admin.ModelAdmin):pass
class OrderAdmin(admin.ModelAdmin):pass
class CustomerAdmin(admin.ModelAdmin):pass
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
