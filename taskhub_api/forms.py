from django import forms
from .models import *


class EmployeeForm(forms.Form):
    """
    A form for creating a new employee.
    Strongly differs from the model!
    """
    # direct mapping to the model:
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(max_length=150)
    is_active = forms.BooleanField()

    # additional fields:
    profile_image = forms.ImageField(required=False)
    # employee_type is a list of PKs, not the actual objects
    employee_type = forms.ModelMultipleChoiceField(queryset=EmployeeType.objects.all())


