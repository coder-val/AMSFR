from django.forms import ModelForm
from .models import *

# class DepartmentForm(ModelForm):
#     class Meta:
#         model = Department
#         fields = '__all__'

class PositionForm(ModelForm):
    class Meta:
        model = Position
        fields = '__all__'

class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        exclude = ['user']

# class EmployeeImageForm(ModelForm):
#     class Meta:
#         model = Employee
#         fields = ['biometric_id']

class ScheduleForm(ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'
        exclude = ['is_active']