from django.shortcuts import render, redirect
from django.conf import settings
from .models import *
from .forms import *
from datetime import timedelta
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib import messages
from .faceRecognition import *
from .attendance import *
import datetime as dt
import shutil, os
from workalendar.asia import Philippines
import pandas as pd

def convert_time(time):
    if time >= dt.time(1,0,0) and time < dt.time(11,59,59):
        str_time = time.strftime("%H:%M:%S")
        real_time = dt.datetime.now().strptime(str_time, "%H:%M:%S")
        convert = real_time + timedelta(hours=12)
        return convert
    return time

# Create your views here.
def home(request):
    context = {}
    template = "employees/home.html"
    return render(request, template, context)

# DEPARTMENT ################################################################
def department(request):
    departments = Department.objects.all()
    context = {'departments': departments}
    return render(request, 'employees/department.html', context)

def create_dept(request):
    context = {}
    form = DepartmentForm()
    template = 'employees/department/create.html'

    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department')

    context = {'form' : form}
    return render(request, template, context)

def update_dept(request, pk):
    context = {}
    department = Department.objects.get(id=pk)
    form = DepartmentForm(instance=department)
    template = 'employees/department/update.html'
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department')
    
    context = {'form': form}
    return render(request, template, context)

def delete_dept(request, pk):
    department = Department.objects.get(id=pk)
    template = 'employees/department/delete.html'

    if request.method == 'POST':
        department.delete()
        return redirect('department')
    
    return render(request, template, {'department': department})

# DESIGNATION ################################################################
def designation(request):
    designations = Designation.objects.all()
    context = {'designations': designations}
    template = "employees/designation.html"
    return render(request, template, context)

def create_desig(request):
    context = {}
    form = DesignationForm()
    template = 'employees/designation/create.html'

    if request.method == 'POST':
        form = DesignationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('designation')

    context = {'form' : form}
    return render(request, template, context)

def update_desig(request, pk):
    context = {}
    designation = Designation.objects.get(id=pk)
    form = DesignationForm(instance=designation)
    template = 'employees/designation/update.html'
    if request.method == 'POST':
        form = DesignationForm(request.POST, instance=designation)
        if form.is_valid():
            form.save()
            return redirect('designation')
    
    context = {'form': form}
    return render(request, template, context)

def delete_desig(request, pk):
    designation = Designation.objects.get(id=pk)
    template = 'employees/designation/delete.html'

    if request.method == 'POST':
        designation.delete()
        return redirect('designation')
    
    return render(request, template, {'designation': designation})

# SCHEDULE #####################################################################
def activate(request, pk):
    Schedule.objects.filter(id=pk).update(is_active=True)
    Schedule.objects.filter(is_active=True).exclude(id=pk).update(is_active=False)
    return redirect(schedule)

def schedule(request):
    schedules = Schedule.objects.all()
    context = {'schedules': schedules}
    template = "employees/schedule.html"
    return render(request, template, context)

def create_sched(request):
    context = {}
    # form = ScheduleForm()
    template = 'employees/schedule/create.html'

    if request.method == 'POST':
        # form = ScheduleForm(request.POST)
        # if form.is_valid():
            # name = form.cleaned_data['name']
            # in_am = form.cleaned_data['in_am']
            # out_am = form.cleaned_data['out_am']
            # in_pm = convert_time(form.cleaned_data['in_pm'])
            # out_pm = convert_time(form.cleaned_data['out_pm'])
            # sched = Schedule(name = name, in_am = in_am, out_am = out_am, in_pm = in_pm, out_pm = out_pm)
            # sched.save()
            # form.save()
            name = request.POST['name']
            in_am = request.POST['in_am']
            out_am = request.POST['out_am']
            in_pm = request.POST['in_pm']
            out_pm = request.POST['out_pm']
            Schedule.objects.create(name=name,in_am=in_am,out_am=out_am,in_pm=in_pm,out_pm=out_pm)
            messages.success(request, "Schedule created successfully!")
            return redirect('create_sched')

    # context = {'form' : form}
    return render(request, template, context)

def update_sched(request, pk):
    context = {}
    schedule = Schedule.objects.get(id=pk)
    form = ScheduleForm(instance=schedule)
    template = 'employees/schedule/update.html'
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            # name = form.cleaned_data['name']
            # in_am = form.cleaned_data['in_am']
            # out_am = form.cleaned_data['out_am']
            # in_pm = convert_time(form.cleaned_data['in_pm'])
            # out_pm = convert_time(form.cleaned_data['out_pm'])
            # Schedule.objects.update(name = name, in_am = in_am, out_am = out_am, in_pm = in_pm, out_pm = out_pm)
            # sched = Schedule(name = name, in_am = in_am, out_am = out_am, in_pm = in_pm, out_pm = out_pm)
            # sched.save()
            return redirect('schedule')
    
    context = {'form': form}
    return render(request, template, context)

def delete_sched(request, pk):
        schedule = Schedule.objects.get(id=pk)
        template = 'employees/schedule/delete.html'

        if request.method == 'POST':
            schedule.delete()
            return redirect('schedule')
        
        return render(request, template, {'schedule': schedule})

# EMPLOYEE ##################################################################
def employee(request):
    employees = Employee.objects.all().order_by('lastname')
    context = {'employees': employees}
    template = "employees/employee.html"
    return render(request, template, context)

def create_emp(request):
    context = {}
    form = EmployeeForm()
    template = 'employees/employee/create.html'

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            id = form.cleaned_data['id']
            lastname = form.cleaned_data['lastname']
            firstname = form.cleaned_data['firstname']
            middlename = form.cleaned_data['middlename']
            department = form.cleaned_data['department']
            designation = form.cleaned_data['designation']
            id_picture = request.FILES['id_picture']

            file_name = default_storage.save(id_picture.name, id_picture)
            image_path = os.path.join(settings.MEDIA_ROOT, file_name)
            path_to_unregistered = os.path.join(settings.MEDIA_ROOT, "unregistered")
            image_checking = os.path.join(path_to_unregistered, file_name)

            if os.path.isfile(image_checking):
                messages.warning(request, "IMAGE ALREADY USED!")
                return render(request, template, {'form':form})

            shutil.move(image_path, path_to_unregistered)

            if checkIfExist(image_checking) is True:
                messages.warning(request, "EMPLOYEE ALREADY REGISTERED!")
                return render(request, template, {'form':form})
            
            else:
                register = Employee(id = id, lastname = lastname, firstname = firstname, middlename = middlename, department = department, designation = designation, id_picture = f'registered/{id}.jpg')
                register.save()
                new_image_path = os.path.join(settings.MEDIA_ROOT, f'registered/{id}.jpg')
                os.rename(image_checking, new_image_path)
                messages.success(request, "EMPLOYEE REGISTERED SUCCESSFULLY!")
                form = EmployeeForm()
                return render(request, template, {'form':form})


            # form.save()
            # return redirect('employee')

    context = {'form' : form}
    return render(request, template, context)

def update_emp(request, pk):
    context = {}
    employee = Employee.objects.get(id=pk)
    form = EmployeeForm(instance=employee)
    template = 'employees/employee/update.html'
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee')
    
    context = {'form': form}
    return render(request, template, context)

def delete_emp(request, pk):
    employee = Employee.objects.get(id=pk)
    template = 'employees/employee/delete.html'

    if request.method == 'POST':
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, employee.id_picture.name)):
            os.remove(os.path.join(settings.MEDIA_ROOT, employee.id_picture.name))
        employee.delete()
        return redirect('employee')
    
    return render(request, template, {'employee': employee})

# HOLIDAY ###############################################################
def holiday(request):
    holidays = Holiday.objects.all()
    context = {'holidays': holidays}
    template = 'employees/holiday.html'
    return render(request, template, context)

def import_holidays(request):
    ph_calendar = Philippines()
    year = dt.datetime.now().year
    # ehem = pd.DataFrame(ph_calendar.holidays(2022), columns=["date", "holiday"])
    # print(ehem)
    holiday_list = ph_calendar.holidays(year)
    holidays = [Holiday(date=x[0], holiday=x[1]) for x in holiday_list if not Holiday.objects.filter(holiday=x[1]).exists()]
    Holiday.objects.bulk_create(holidays)
    messages.success(request, "Holidays imported successfully!")
    return redirect('holiday')

def create_holiday(request):
    context = {}
    # form = HolidayForm()
    template = 'employees/holiday/create.html'

    if request.method == 'POST':
        holiday = request.POST['holiday']
        date = request.POST['date']
        Holiday.objects.create(holiday=holiday, date=date)
        messages.success(request, "Holiday added successfully!")
        return redirect('holiday')
    
    # context = {'form': form}
    return render(request, template, context)
# ATTENDANCE #############################################################
def attendance(request):
    context = {}
    template = 'employees/attendance.html'
    return render(request, template, context)

def in_am(request):
    context = {}
    template = 'employees/attendance.html'

    if check_sched() is False:
        messages.warning(request, "NO ACTIVE SCHEDULE YET!")
        return redirect('attendance')
    
    if checkpoint_in_am() is False:
        messages.warning(request, "TIME IN NOT IN RANGE!")
        return redirect('attendance')

    if face_recog(1) is False:
        messages.warning(request, "NO REGISTERED IMAGES YET!")
        return redirect('attendance')
    else:
        return redirect('attendance')
    
def out_am(request):
    context = {}
    template = 'employees/attendance.html'

    if check_sched() is False:
        messages.warning(request, "NO ACTIVE SCHEDULE YET!")
        return redirect('attendance')
    
    if checkpoint_out_am() is False:
        messages.warning(request, "TIME OUT NOT IN RANGE!")
        return redirect('attendance')

    if face_recog(2) is False:
        messages.warning(request, "NO REGISTERED IMAGES YET!")
        return redirect('attendance')
    else:
        return redirect('attendance')

def in_pm(request):
    context = {}
    template = 'employees/attendance.html'

    if check_sched() is False:
        messages.warning(request, "NO ACTIVE SCHEDULE YET!")
        return redirect('attendance')

    if checkpoint_in_pm() is False:
        messages.warning(request, "TIME IN NOT IN RANGE!")
        return redirect('attendance')

    if face_recog(3) is False:
        messages.warning(request, "NO REGISTERED IMAGES YET!")
        return redirect('attendance')
    else:
        return redirect('attendance')

def out_pm(request):
    context = {}
    template = 'employees/attendance.html'

    if check_sched() is False:
        messages.warning(request, "NO ACTIVE SCHEDULE YET!")
        return redirect('attendance')

    if checkpoint_out_pm() is False:
        messages.warning(request, "TIME OUT NOT IN RANGE!")
        return redirect('attendance')

    if face_recog(4) is False:
        messages.warning(request, "NO REGISTERED IMAGES YET!")
        return redirect('attendance')
    else:
        return redirect('attendance')

def monitor(request):
    # logs = Attendance.objects.all()
    # ehe = logs.values_list('reference', flat=True).exclude(reference=None)
    # absents = Employee.objects.exclude(id__in = ehe)
    # context = {'logs': logs, 'absents': absents}
    context = {}
    template = 'employees/logs.html'

    in_am = Schedule.objects.filter(is_active=True).values()[0]['in_am']
    in_pm = Schedule.objects.filter(is_active=True).values()[0]['in_pm']

    now = dt.datetime.now().time()
    cut_off = now.replace(hour=23, minute=59, second=59, microsecond=0)

    if now >= in_am and now < in_pm:
        insides = Attendance.objects.filter(in_am__isnull=False, out_am__isnull=True, date=dt.datetime.now().date())
        outsides = Attendance.objects.filter(in_am__isnull=False, out_am__isnull=False, date=dt.datetime.now().date()) | Attendance.objects.filter(in_am__isnull=True, out_am__isnull=False, date=dt.datetime.now().date())
        context = {'insides':insides, 'outsides':outsides}
    elif now >= in_pm and dt.datetime.now().time() < cut_off:
        insides = Attendance.objects.filter(in_pm__isnull=False, out_pm__isnull=True, date=dt.datetime.now().date())
        outsides = Attendance.objects.filter(out_am__isnull=False, in_pm__isnull=False, out_pm__isnull=False, date=dt.datetime.now().date()) | Attendance.objects.filter(out_am__isnull=False, in_pm__isnull=True, out_pm__isnull=True, date=dt.datetime.now().date()) | Attendance.objects.filter(out_am__isnull=False, in_pm__isnull=True, out_pm__isnull=False, date=dt.datetime.now().date()) | Attendance.objects.filter(out_am__isnull=True, in_pm__isnull=False, out_pm__isnull=False, date=dt.datetime.now().date())
        context = {'insides':insides, 'outsides':outsides}

    return render(request, template, context)

def dtr_employee(request):
    pass