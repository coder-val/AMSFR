from django.db import models

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
    id = models.CharField(primary_key=True, max_length=30)
    lastname = models.CharField(max_length=30)
    firstname = models.CharField(max_length=30)
    middlename = models.CharField(max_length=30)
    department = models.ForeignKey(Department, models.SET_NULL, blank=True, null=True)
    designation = models.ForeignKey(Designation, models.SET_NULL, blank=True, null=True)
    id_picture = models.ImageField()

    class Meta:
        db_table = 'employees'
    
    def __str__(self):
        return self.id
    
class Attendance(models.Model):
    employee_id = models.CharField(max_length=30)
    in_am = models.TimeField(null=True, blank=True)
    out_am = models.TimeField(null=True, blank=True)
    in_pm = models.TimeField(null=True, blank=True)
    out_pm = models.TimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'attendance'

class Holiday(models.Model):
    date = models.DateField(null=True, blank=True)
    holiday = models.CharField(max_length=50)

    class Meta:
        db_table = 'holidays'