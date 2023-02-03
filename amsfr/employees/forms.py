from django.forms import ModelForm
from .models import *

class DesignationForm(ModelForm):
    class Meta:
        model = Designation
        fields = '__all__'

class PositionForm(ModelForm):
    class Meta:
        model = Position
        fields = '__all__'

class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        # exclude = ['user']

class ScheduleForm(ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'
        exclude = ['is_active']

class ThresholdForm(ModelForm):
    class Meta:
        model = Threshold
        fields = '__all__'

class SignatoryForm(ModelForm):
    class Meta:
        model = Signatory
        fields = '__all__'