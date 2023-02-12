from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

# Create your models here.
# class Designation(models.Model):
#     name = models.CharField(max_length=50, unique=True, verbose_name="designation name")

#     class Meta:
#         db_table = 'designations'

#     def __str__(self):
#         return self.name

class Position(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="position name")

    class Meta:
        db_table = 'positions'

    def __str__(self):
        return self.name

class Schedule(models.Model):
    name = models.CharField(max_length=30, unique=True)
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
    # GENDER_CHOICES = [
    #     ('M', 'MALE'),
    #     ('F', 'FEMALE'),
    # ]


    # account info
    # user = models.ForeignKey(User, on_delete=models.CASCADE)#
    # email = models.EmailField(blank=True, null=True, unique=True)#
    # created = models.DateTimeField(auto_now_add=True)#

    # personal info
    id = models.CharField(primary_key=True, max_length=14, validators=[MinLengthValidator(13, message="ID must be at least 13 characters.")])
    firstname = models.CharField(max_length=40, verbose_name="* Firstname")#
    middlename = models.CharField(max_length=40, verbose_name="* Middlename")#
    lastname = models.CharField(max_length=40, verbose_name="* Lastname")#
    suffix = models.CharField(max_length=40, blank=True, null=True)
    birth_date = models.DateField(verbose_name="* Birthdate")#
    mobile_number = models.CharField(max_length=11, blank=True, null=True)#
    barangay = models.CharField(max_length=30, verbose_name="* Barangay")#
    municipality = models.CharField(max_length=30, verbose_name="* Municipality")#
    province = models.CharField(max_length=30, verbose_name="* Province")#
    # gender = models.CharField(choices=GENDER_CHOICES, max_length=6, blank=True, null=True)#

    # primary info
    id_picture = models.ImageField(verbose_name="Picture ID")
    position = models.ForeignKey(Position, models.SET_DEFAULT, default=None, null=True, verbose_name="* Position")#
    # designation = models.ForeignKey(Designation,models.SET_NULL, blank=True, null=True)
    date_employed = models.DateField(blank=True, null=True)
    # reportsTo = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)# SETTINGS
    # department = models.ForeignKey(Department, models.SET_NULL, blank=True, null=True)#
    # employment_status = models.CharField(max_length=8, default="active")

    #license info
    license_no = models.CharField(max_length=50, blank=True, null=True)
    registration_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)

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

class Threshold(models.Model):
    threshold = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = 'threshold'

class Signatory(models.Model):
    signatory = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'signatory'

class Holiday(models.Model):
    holiday = models.CharField(max_length=50)
    date = models.DateField()

    class Meta:
        db_table = 'holidays'