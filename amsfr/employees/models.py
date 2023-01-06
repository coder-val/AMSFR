from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = 'departments'

    def __str__(self):
        return self.name

class Designation(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = 'designations'

    def __str__(self):
        return self.name

class Schedule(models.Model):
    name = models.CharField(max_length=20, unique=True)
    in_am = models.TimeField()
    out_am = models.TimeField()
    in_pm = models.TimeField()
    out_pm = models.TimeField()
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'schedules'
    
    def __str__(self):
        return self.name
    
class Employee(models.Model):
    GENDER_CHOICES = [
        ('M', 'MALE'),
        ('F', 'FEMALE'),
    ]
    # account info
    user = models.ForeignKey(User, on_delete=models.CASCADE)#
    firstname = models.CharField(max_length=30)#
    middlename = models.CharField(max_length=30)#
    lastname = models.CharField(max_length=30)#
    email = models.EmailField(blank=True, null=True)#
    created = models.DateTimeField(auto_now_add=True)#

    # personal info
    birth_date = models.DateField(blank=True, null=True)#
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, blank=True, null=True)#
    mobile_number = models.CharField(max_length=11, blank=True, null=True)#
    barangay = models.CharField(max_length=30, blank=True, null=True)#
    municipality = models.CharField(max_length=30, blank=True, null=True)#
    province = models.CharField(max_length=30, blank=True, null=True)#

    # primary info
    id = models.CharField(primary_key=True, max_length=30)
    biometric_id = models.ImageField()
    department = models.ForeignKey(Department, models.SET_NULL, blank=True, null=True)#
    designation = models.ForeignKey(Designation, models.SET_NULL, blank=True, null=True)#
    # reportsTo = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)# SETTINGS
    date_employed = models.DateField(blank=True, null=True)
    # employment_status = models.CharField(max_length=8, default="active")

    class Meta:
        db_table = 'employees'
    
    def __str__(self):
        return self.id
    
class Attendance(models.Model):
    reference = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    employee_id = models.CharField(max_length=30)
    in_am = models.TimeField(null=True, blank=True)
    out_am = models.TimeField(null=True, blank=True)
    in_pm = models.TimeField(null=True, blank=True)
    out_pm = models.TimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    remarks = models.CharField(null=True, blank=True, max_length=1)

    class Meta:
        db_table = 'attendance'

class Holiday(models.Model):
    holiday = models.CharField(max_length=50)
    date = models.DateField()

    class Meta:
        db_table = 'holidays'