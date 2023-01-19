from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.paginator import Paginator
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
# import pandas as pd
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import StreamingHttpResponse, HttpResponse
from .camera import *

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
    template = "employees/homepage.html"

    employee = Employee.objects.all().exists()
    sched = Schedule.objects.filter(is_active=True)

    context = {'employee':employee, 'sched':sched}
    
    return render(request, template, context)

def test(request):
    response = StreamingHttpResponse(gen(VideoCamera()),content_type='multipart/x-mixed-replace; boundary=frame')
    return response

@login_required
def dashboard(request):
    context = {}
    template = "employees/dashboard.html"

    # emp_user = User.objects.filter(pk=12)[0].username
    # # haha = emp_user.employee_set.all()
    # print(emp_user)
    
    # print(emp_user.employee_set.all().filter(lastname="Cabitac").values_list())

    # toggle = True

    # school_id = "400392"
    # dtn = dt.datetime.now().strftime("%Y")
    # year = dtn[2:len(dtn)]
    # id_prefix = f'{school_id}-{year}-'
    # print(id_prefix)

    # id = User.objects.get(id=2)
    # id.delete()

    # user = User.objects.create_user(f'{id_prefix}001', "", f'{id_prefix}001')
    # user.save()
    # emp = Employee.objects.create(user = user, id=id_prefix+"001", firstname = "Val", middlename = "Caccam", lastname = "Cabitac", gender="M", biometric_id = "awit.jpg")
    # emp.save()

    return render(request, template, context)

# DEPARTMENT ################################################################
def department(request):
    departments = Department.objects.all()
    context = {'departments': departments}
    template = 'employees/department/department.html'
    return render(request, template, context)

def create_dept(request):
    context = {}
    form = DepartmentForm()
    template = 'employees/department/create_dept.html'

    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data['name']
            messages.success(request, f'{name} added successfully!')
            return redirect('create_dept')

    context = {'form' : form}
    return render(request, template, context)

def update_dept(request, pk):
    context = {}
    department = Department.objects.get(id=pk)
    dept_name = department.name
    form = DepartmentForm(instance=department)
    template = 'employees/department/update_dept.html'
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f'{dept_name} updated to {department.name} successfully!')
            return redirect('department')
    
    context = {'form': form}
    return render(request, template, context)

def delete_dept(request, pk):
    department = Department.objects.get(id=pk)
    template = 'employees/department/delete_dept.html'

    if request.method == 'POST':
        department.delete()
        messages.success(request, f'{department.name} deleted successfully!')
        return redirect('department')
    
    return render(request, template, {'department': department})

# DESIGNATION ################################################################
def designation(request):
    designations = Designation.objects.all()
    context = {'designations': designations}
    template = "employees/designation/designation.html"
    return render(request, template, context)

def create_desig(request):
    context = {}
    form = DesignationForm()
    template = 'employees/designation/create_desig.html'

    if request.method == 'POST':
        form = DesignationForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data['name']
            messages.success(request, f'{name} added successfully!')
            return redirect('designation')

    context = {'form' : form}
    return render(request, template, context)

def update_desig(request, pk):
    context = {}
    designation = Designation.objects.get(id=pk)
    desig_name = designation.name
    form = DesignationForm(instance=designation)
    template = 'employees/designation/update_desig.html'
    if request.method == 'POST':
        form = DesignationForm(request.POST, instance=designation)
        if form.is_valid():
            form.save()
            messages.success(request, f'{desig_name} updated to {designation.name} successfully!')
            return redirect('designation')
    
    context = {'form': form}
    return render(request, template, context)

def delete_desig(request, pk):
    designation = Designation.objects.get(id=pk)
    template = 'employees/designation/delete_desig.html'

    if request.method == 'POST':
        designation.delete()
        messages.success(request, f'{designation.name} deleted successfully!')
        return redirect('designation')
    
    return render(request, template, {'designation': designation})

# SCHEDULE #####################################################################
def activate(request, pk):
    Schedule.objects.filter(id=pk).update(is_active=True)
    Schedule.objects.filter(is_active=True).exclude(id=pk).update(is_active=False)
    messages.success(request, "activated successfully!")
    return redirect('schedule')

def deactivate(request, pk):
    Schedule.objects.filter(id=pk).update(is_active=False)
    messages.success(request, "deactivated successfully!")
    return redirect('schedule')

def schedule(request):
    # schedules = Schedule.objects.all()
    active_sched = Schedule.objects.filter(is_active=True)
    inactive_sched = Schedule.objects.filter(is_active=False)
    context = {'active_sched': active_sched, 'inactive_sched':inactive_sched}
    template = "employees/schedule/schedule.html"
    return render(request, template, context)

def create_sched(request):
    context = {}
    template = 'employees/schedule/create_sched.html'

    if request.method == 'POST':
            try:
                in_am = dt.datetime.strptime(request.POST['in_am'], '%I:%M %p').time()
                out_am = dt.datetime.strptime(request.POST['out_am'], '%I:%M %p').time()
                in_pm = dt.datetime.strptime(request.POST['in_pm'], '%I:%M %p').time()
                out_pm = dt.datetime.strptime(request.POST['out_pm'], '%I:%M %p').time()
            except:
                messages.error(request, "Invalid time formats!")
                return render(request, template, context)
            
            if Schedule.objects.filter(name=request.POST['name']).exists():
                messages.error(request, "Schedule already exist!")
                return render(request, template, context)
            
            Schedule.objects.create(name=request.POST['name'],in_am=in_am,out_am=out_am,in_pm=in_pm,out_pm=out_pm)
            messages.success(request, "Schedule created successfully!")
            return redirect('schedule')

    return render(request, template, context)

def update_sched(request, pk):
    context = {}
    template = 'employees/schedule/update_sched.html'
    schedule = Schedule.objects.get(id=pk)
    sched_name = schedule.name
    context = {'schedule':schedule}

    if request.method == 'POST':
        in_am = dt.datetime.strptime(request.POST['in_am'], '%I:%M %p').time()
        out_am = dt.datetime.strptime(request.POST['out_am'], '%I:%M %p').time()
        in_pm = dt.datetime.strptime(request.POST['in_pm'], '%I:%M %p').time()
        out_pm = dt.datetime.strptime(request.POST['out_pm'], '%I:%M %p').time()
        # if Schedule.objects.filter(name=request.POST['name']).exists():
        Schedule.objects.filter(id=pk).update(in_am=in_am,out_am=out_am,in_pm=in_pm,out_pm=out_pm)
        # else:
        #     Schedule.objects.filter(id=pk).update(name=request.POST['name'],in_am=in_am,out_am=out_am,in_pm=in_pm,out_pm=out_pm)
        messages.success(request, f'{sched_name} updated successfully!')
        return redirect('schedule')
    
    return render(request, template, context)

def delete_sched(request, pk):
    schedule = Schedule.objects.get(id=pk)
    sched_name = schedule.name
    template = 'employees/schedule/delete_sched.html'

    if request.method == 'POST':
        schedule.delete()
        messages.success(request, f'{sched_name} deleted successfully!')
        return redirect('schedule')
    
    return render(request, template, {'schedule': schedule})

# EMPLOYEE ##################################################################
def employee(request):
    employees = Employee.objects.all().order_by('id')
    p = Paginator(employees, 10)
    page_number = request.GET.get('page')
    p_employees = p.get_page(page_number)
    context = {'employees': p_employees}
    template = "employees/employee/employee.html"
    return render(request, template, context)

def create_emp(request):
    context = {}
    form = EmployeeForm()
    template = 'employees/employee/create_emp.html'

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            id = form.cleaned_data['id']
            biometric_id = request.FILES['biometric_id']
            lastname = form.cleaned_data['lastname']
            firstname = form.cleaned_data['firstname']
            middlename = form.cleaned_data['middlename']
            email = form.cleaned_data['email']
            birth_date = form.cleaned_data['birth_date']
            gender = form.cleaned_data['gender']
            mobile_number = form.cleaned_data['mobile_number']
            barangay = form.cleaned_data['barangay']
            municipality = form.cleaned_data['municipality']
            province = form.cleaned_data['province']
            date_employed = form.cleaned_data['date_employed']
            department = form.cleaned_data['department']
            designation = form.cleaned_data['designation']
            # reportsTo = form.cleaned_data['reportsTo']

            file_name = default_storage.save(biometric_id.name, biometric_id)
            image_path = os.path.join(settings.MEDIA_ROOT, file_name)
            path_to_unregistered = os.path.join(settings.MEDIA_ROOT, "unregistered")
            image_checking = os.path.join(path_to_unregistered, file_name)

            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'registered')):
                    os.mkdir(os.path.join(settings.MEDIA_ROOT, 'registered'))

            if os.path.isfile(image_checking):
                os.remove(image_path)
                messages.warning(request, "ID picture already used!")
                return render(request, template, {'form':form})

            shutil.move(image_path, path_to_unregistered)
            test = checkIfExist(image_checking)

            if test is True:
                os.remove(image_checking)
                messages.warning(request, "Employee already registered!")
                return render(request, template, {'form':form})
            elif test is False:
                user = User.objects.create_user(id, email, id)
                register = Employee(user = user, id = id, lastname = lastname, firstname = firstname, middlename = middlename, email = email, birth_date = birth_date, gender = gender, mobile_number = mobile_number, barangay = barangay, municipality = municipality, province = province, date_employed = date_employed, department = department, designation = designation, biometric_id = f'registered/{id}.jpg')
                user.save()
                register.save()
                new_image_path = os.path.join(settings.MEDIA_ROOT, f'registered/{id}.jpg')
                os.rename(image_checking, new_image_path)
                messages.success(request, f'Employee {id} registered successfully!')
                form = EmployeeForm()
                return render(request, template, {'form':form})
            else:
                os.remove(image_checking)
                messages.error(request, "No face detected!")
                return render(request, template, {'form':form})

            # form.save()
            # return redirect('employee')

    context = {'form' : form}
    return render(request, template, context)

def view_emp(request, pk):
    emp_details = Employee.objects.filter(id=pk)
    id = emp_details[0].id
    context = {'emp_details': emp_details, 'emp_id':id}
    template = 'employees/employee/view_emp.html'
    return render(request, template, context)

def update_emp(request, pk):
    emp_id = Employee.objects.get(id=pk)
    context = {'employee_id':emp_id}
    try:
        employee = Employee.objects.get(id=pk)
    except ObjectDoesNotExist:
        return redirect('employee')

    form = EmployeeForm(instance=employee)
    template = 'employees/employee/update_emp.html'
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            # id = Employee.objects.filter(id=pk)[0].id
            # user = User.objects.get(username=id)
            # user.username = form.cleaned_data['id']
            form.save()
            # user.save()
            messages.success(request, f"Employee {pk} updated successfully!")
            return redirect('employee')
    
    context = {'form': form, 'employee_id':emp_id}
    return render(request, template, context)

def update_photo(request, pk):
    emp_id = Employee.objects.get(id=pk)
    emp_details = Employee.objects.filter(id=pk)
    context = {'employee_id':emp_id, 'emp_details':emp_details}
    template = 'employees/employee/update_photo.html'

    if request.method == 'POST':
        biometric_id = request.FILES['biometric_id']
        cbox = request.POST.get('cbox')

        file_name = default_storage.save(biometric_id.name, biometric_id)
        image_path = os.path.join(settings.MEDIA_ROOT, file_name)
        path_to_unregistered = os.path.join(settings.MEDIA_ROOT, "unregistered")
        path_to_registered = os.path.join(settings.MEDIA_ROOT, "registered")
        image_checking = os.path.join(path_to_unregistered, file_name)

        shutil.move(image_path, path_to_unregistered)

        registered_image = os.path.join(path_to_registered, f'{pk}.jpg')
        if cbox is None:
            result = checkFace(image_checking)

            if result is True:
                os.replace(image_checking, registered_image)
                messages.success(request, "Image updated successfully!")
                return redirect('view_emp', pk)

            else:
                messages.error(request, "No face detected!")
                os.remove(image_checking)
        
        else:
            result = checkImage(image_checking, pk)
            
            if result is False:
                print("IMAGE NOT THE SAME")
                messages.warning(request, "Unknown face detected!")
                os.remove(image_checking)

            elif result is True:
                print("IMAGE GOOD")
                messages.success(request, "Image updated successfully!")
                os.replace(image_checking, registered_image)
                return redirect('view_emp', pk)

            else:
                print("NO FACE PROMISE")
                messages.error(request, "No face detected!")
                os.remove(image_checking)

    return render(request, template, context)

def delete_emp(request, pk):
    emp_id = Employee.objects.get(id=pk)
    emp_user = User.objects.get(username=emp_id)
    template = 'employees/employee/delete_emp.html'

    if request.method == 'POST':
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, emp_id.biometric_id.name)):
            os.remove(os.path.join(settings.MEDIA_ROOT, emp_id.biometric_id.name))
        # employee.delete()
        emp_user.delete()
        messages.success(request, f'Employee {emp_id} deleted successfully!')
        return redirect('employee')
    
    return render(request, template, {'employee': emp_id})

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
    in_am = Schedule.objects.filter(is_active=True).values()[0]['in_am']
    out_am = Schedule.objects.filter(is_active=True).values()[0]['out_am']
    in_pm = Schedule.objects.filter(is_active=True).values()[0]['in_pm']
    out_pm = Schedule.objects.filter(is_active=True).values()[0]['out_pm']
    template = 'employees/attendance/attendance.html'
    context = {'in_am':in_am, 'out_am':out_am, 'in_pm':in_pm, 'out_pm':out_pm}
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

def logs_today(request):
    # logs = Attendance.objects.all()
    # ehe = logs.values_list('reference', flat=True).exclude(reference=None)
    # absents = Employee.objects.exclude(id__in = ehe)
    # context = {'logs': logs, 'absents': absents}
    context = {}
    template = 'employees/attendance/logs_today.html'

    in_am = Schedule.objects.filter(is_active=True).values()[0]['in_am']
    in_pm = Schedule.objects.filter(is_active=True).values()[0]['in_pm']

    now_time = dt.datetime.now().time()
    now_date = dt.datetime.now().date()
    cut_off = now_time.replace(hour=23, minute=59, second=59, microsecond=0)

    if now_time >= in_am and now_time < in_pm:
        insides = Attendance.objects.filter(in_am__isnull=False, out_am__isnull=True, date=now_date)
        outsides = Attendance.objects.filter(in_am__isnull=False, out_am__isnull=False, date=now_date) | Attendance.objects.filter(in_am__isnull=True, out_am__isnull=False, date=now_date)
        context = {'insides':insides, 'outsides':outsides, 'in_am':in_am, 'out_am':out_am, 'in_pm':in_pm, 'out_pm':out_pm}
    elif now_time >= in_pm and now_time < cut_off:
        insides = Attendance.objects.filter(in_pm__isnull=False, out_pm__isnull=True, date=now_date)
        outsides = Attendance.objects.filter(out_am__isnull=False, in_pm__isnull=False, out_pm__isnull=False, date=now_date) | Attendance.objects.filter(out_am__isnull=False, in_pm__isnull=True, out_pm__isnull=True, date=now_date) | Attendance.objects.filter(out_am__isnull=False, in_pm__isnull=True, out_pm__isnull=False, date=now_date) | Attendance.objects.filter(out_am__isnull=True, in_pm__isnull=False, out_pm__isnull=False, date=now_date) | Attendance.objects.filter(out_am__isnull=True, in_pm__isnull=True, out_pm__isnull=False, date=now_date)
        context = {'insides':insides, 'outsides':outsides, 'in_am':in_am, 'out_am':out_am, 'in_pm':in_pm, 'out_pm':out_pm}

    return render(request, template, context)

def full_logs_today(request):
    full_attendance_today = Attendance.objects.all().order_by('employee_id')
    # print(full_attendance_today[0].reference.username)
    context = {'attendance':full_attendance_today}
    template = "employees/attendance/full_logs_today.html"
    return render(request, template, context)

def dtr_employee(request):
    pass