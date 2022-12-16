from django.forms import ModelForm
from .models import *

class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = '__all__'

class DesignationForm(ModelForm):
    class Meta:
        model = Designation
        fields = '__all__'

class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        # exclude = ['id_picture']

class ScheduleForm(ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'
        exclude = ['is_active']