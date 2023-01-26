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
import pandas as pd
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import StreamingHttpResponse, HttpResponse
from .camera import *
import calendar

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
    partial_template = 'employees/attendance.html'

    employee = Employee.objects.all().exists()
    sched = Schedule.objects.filter(is_active=True)
    # threshold = settings.THRESHOLD


    if sched:
        # in_am = convert_to_timedelta(Schedule.objects.filter(is_active=True).values()[0]['in_am'])
        # out_am = Schedule.objects.filter(is_active=True).values()[0]['out_am']
        in_pm = convert_to_timedelta(Schedule.objects.filter(is_active=True).values()[0]['in_pm'])
        # out_pm = Schedule.objects.filter(is_active=True).values()[0]['out_pm']
        # threshold = dt.timedelta(minutes=settings.THRESHOLD)

        now_time = convert_to_timedelta(dt.datetime.now().time())
        now_date = dt.datetime.now().date()
        cut_off = dt.timedelta(hours=23, minutes=59, seconds=59, microseconds=0)

        if now_time >= dt.timedelta(hours=6) and now_time < in_pm:
            insides = Attendance.objects.filter(in_am__isnull=False, out_am__isnull=True, date=now_date).order_by('-in_am')
            outsides = Attendance.objects.filter(in_am__isnull=False, out_am__isnull=False, date=now_date).order_by('-out_am') | Attendance.objects.filter(in_am__isnull=True, out_am__isnull=False, date=now_date).order_by('-out_am')
            context = {'insides':insides, 'outsides':outsides}

        elif now_time >= in_pm and now_time < cut_off:
            insides = Attendance.objects.filter(in_pm__isnull=False, out_pm__isnull=True, date=now_date).order_by('-in_pm')
            outsides = Attendance.objects.filter(out_am__isnull=False, in_pm__isnull=False, out_pm__isnull=False, date=now_date).order_by('-out_pm') | Attendance.objects.filter(out_am__isnull=False, in_pm__isnull=True, out_pm__isnull=True, date=now_date).order_by('-out_pm') | Attendance.objects.filter(out_am__isnull=False, in_pm__isnull=True, out_pm__isnull=False, date=now_date).order_by('-out_pm') | Attendance.objects.filter(out_am__isnull=True, in_pm__isnull=False, out_pm__isnull=False, date=now_date).order_by('-out_pm') | Attendance.objects.filter(out_am__isnull=True, in_pm__isnull=True, out_pm__isnull=False, date=now_date).order_by('-out_pm')
            context = {'insides':insides, 'outsides':outsides}

    if request.htmx:
        return render(request, partial_template, context)
    else:
        context = {'employee':employee, 'sched':sched, 'threshold':settings.THRESHOLD}
        return render(request, template, context)

def test(request):
    response = StreamingHttpResponse(gen(VideoCamera()),content_type='multipart/x-mixed-replace; boundary=frame')
    return response

@login_required
def dashboard(request):
    context = {}
    template = "employees/dashboard.html"
    return render(request, template, context)

def dtr_by_date(request):
    context = {}
    template = 'employees/dtr/dtr_by_date.html'

    ph_calendar = Philippines()
    # print(ehem)
    # print(ph_calendar.is_holiday(dt.datetime(2023, 1, 1)))

    total = Employee.objects.count()
    # dates = Attendance.objects.values_list('date', flat=True).order_by('-date').distinct().filter(date__month=dt.datetime.now().date().month)
    # dates_list = Attendance.objects.values_list('date', flat=True).order_by('date').distinct()
    # p = Paginator(dates, per_page=5, orphans=1)
    # page_number = request.GET.get('page')
    # p_dates = p.get_page(page_number)
    now = dt.datetime.now().date()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    dates_list = Attendance.objects.filter(date__month=now.month).values_list('date', flat=True).distinct().order_by('date')
    dates = [dt.datetime(year=now.year, month=now.month, day=x).date() for x in range(1, days_in_month+1)]
    presents = []
    absents = []
    holidays = []
    y = 0
    z = 0
    
    for x in range(1, len(dates) + 1):
        try:
            d = dt.datetime.strptime(str(dates_list[y]), "%Y-%m-%d").date().day
            h = dt.datetime.strptime(str(dates[z]), "%Y-%m-%d").date()

            if ph_calendar.is_holiday(h):
                holidays.append(True)
            else:
                holidays.append(False)

            if  d == x:
                p = Attendance.objects.filter(date=dates_list[y]).count()
                a = total - p
                presents.append(p)
                absents.append(a)
                y+=1
            else:
                presents.append("")
                absents.append("")
        except:
            presents.append("")
            absents.append("")
        z+=1
    # for x in dates_list:
    #     p = Attendance.objects.filter(date=x).count()
    #     a = total - p
    #     present.append(p)
    #     absent.append(a)
    dates.reverse()
    presents.reverse()
    absents.reverse()
    holidays.reverse()
    items = zip(dates,presents,absents,holidays)
    context = {'dates':items}
    # if request.htmx:
    #     return render(request, 'employees/partials/dtr_by_date.html', context)
    return render(request, template, context)

def dtr_specific_date(request, date):
    context = {}
    template = 'employees/dtr/dtr_by_date_specific.html'

    d = date.split('-')
    date = dt.date(year=int(d[0]),month=int(d[1]), day=int(d[2]))

    logs = Attendance.objects.filter(date=date).order_by('reference__lastname')
    minutes_worked = []
    undertime = []
    overtime = []
    for x in range(logs.count()):
        calc = calc_minutes_worked(logs[x].in_am, logs[x].out_am, logs[x].in_pm, logs[x].out_pm)
        mins = convert_time_to_minutes(calc)
        minutes_worked.append(mins)
        if mins < 480:
            undertime.append(480 - mins)
            overtime.append("")
        elif mins > 480:
            overtime.append(mins - 480)
            undertime.append("")
        else:
            undertime.append("")
            overtime.append("")
    
    sets = zip(logs, undertime, overtime, minutes_worked)
    # print(int(convert_time_to_minutes(str(calc))))
    context = {'logs':sets, 'date':date}

    return render(request, template, context)

def dtr_by_employee(request):
    context = {}
    template = 'employees/dtr/dtr_by_employee.html'

    # emp_id = Employee.objects.filter(attendance__id=90)
    # print(emp_id[1])
    employees = Employee.objects.all().order_by('lastname')
    daysWorked = []
    absents = []
    lates = []
    undertime = []
    overtime = []
    # total_hours = 0
    
    for x in range(employees.count()):
        attendance_list = Attendance.objects.all().filter(date__month=dt.datetime.now().date().month)
        days_worked = attendance_list.filter(employee_id=employees[x], remarks="P") | attendance_list.filter(employee_id=employees[x], remarks="L")
        absent = attendance_list.values_list('date').distinct().count() - days_worked.count()
        late = attendance_list.filter(employee_id=employees[x], remarks="L").count()
        logs = attendance_list.filter(employee_id=employees[x])
        ut_count = 0
        ot_count = 0
        for y in range(logs.count()):
            calc = calc_minutes_worked(logs[y].in_am, logs[y].out_am, logs[y].in_pm, logs[y].out_pm)
            mins = convert_time_to_minutes(calc)
            if mins < 480:
                # undertime.append(480 - mins)
                ut_count+=1
            elif mins > 480:
                # overtime.append(mins - 480)
                ot_count+=1

        daysWorked.append(days_worked.count())
        absents.append(absent)
        lates.append(late)
        undertime.append(ut_count)
        overtime.append(ot_count)

    # print(round(total_hours/60, 2))
    # print(total_hours)
    sets = zip(employees,daysWorked,absents,lates,undertime,overtime)
    context = {'employees':sets}

    return render(request, template, context)

def dtr_specific_employee(request, pk):
    context = {}
    template = 'employees/dtr/dtr_by_employee_specific.html'

    ph_calendar = Philippines()
    # emp_id = []
    # emp_date = []
    emp_in_am = []
    emp_out_am = []
    emp_in_pm = []
    emp_out_pm = []
    emp_remarks = []
    minutes_worked = []
    undertime = []
    overtime = []
    holidays = []
    now = dt.datetime.now().date()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    dates = [dt.datetime(year=now.year, month=now.month, day=x).date() for x in range(1, days_in_month+1)]
    total_hours = 0

    emp_name = Employee.objects.filter(id=pk)
    emp_logs = Attendance.objects.filter(employee_id=pk, date__month=dt.datetime.now().date().month).order_by('date')
    y = 0
    z = 0
    for x in range(1, len(dates)+1):
        try:
            h = dt.datetime.strptime(str(dates[z]), "%Y-%m-%d").date()

            if ph_calendar.is_holiday(h):
                holidays.append(True)
            else:
                holidays.append(False)

            if emp_logs[y].date.day == x:
                # emp_id.append(emp_logs[y].employee_id)
                # emp_date.append(emp_logs[y].date)
                emp_in_am.append(emp_logs[y].in_am)
                emp_out_am.append(emp_logs[y].out_am)
                emp_in_pm.append(emp_logs[y].in_pm)
                emp_out_pm.append(emp_logs[y].out_pm)
                emp_remarks.append(emp_logs[y].remarks)
                
                calc = calc_minutes_worked(emp_logs[y].in_am, emp_logs[y].out_am, emp_logs[y].in_pm, emp_logs[y].out_pm)
                mins = convert_time_to_minutes(calc)
                minutes_worked.append(mins)
                if mins < 480:
                    undertime.append(480 - mins)
                    overtime.append("")
                elif mins > 480:
                    overtime.append(mins - 480)
                    undertime.append("")
                else:
                    undertime.append("")
                    overtime.append("")
                total_hours+=mins
                y+=1
            else:
                # emp_id.append("")
                # emp_date.append("")
                emp_in_am.append("")
                emp_out_am.append("")
                emp_in_pm.append("")
                emp_out_pm.append("")
                emp_remarks.append("")
                undertime.append("")
                overtime.append("")
                minutes_worked.append("")
        except:
            # emp_id.append("")
            # emp_date.append("")
            emp_in_am.append("")
            emp_out_am.append("")
            emp_in_pm.append("")
            emp_out_pm.append("")
            emp_remarks.append("")
            undertime.append("")
            overtime.append("")
            minutes_worked.append("")

        z+=1

        # calc = calc_minutes_worked(emp_logs[x].in_am, emp_logs[x].out_am, emp_logs[x].in_pm, emp_logs[x].out_pm)
        # mins = convert_time_to_minutes(calc)
        # minutes_worked.append(mins)
        # if mins < 480:
        #     undertime.append(480 - mins)
        #     overtime.append("")
        # elif mins > 480:
        #     overtime.append(mins - 480)
        #     undertime.append("")
        # else:
        #     undertime.append("")
        #     overtime.append("")
        # total_hours+=mins
    sets = zip(dates, emp_in_am, emp_out_am, emp_in_pm, emp_out_pm, emp_remarks, undertime, overtime, minutes_worked, holidays)
    
    context = {'employee':emp_name, 'logs':sets, 'total':round(total_hours/60, 2)}
    return render(request, template, context)
# DEPARTMENT ################################################################
# def department(request):
#     departments = Department.objects.all()
#     context = {'departments': departments}
#     template = 'employees/department/department.html'
#     return render(request, template, context)

# def create_dept(request):
    # context = {}
    # form = DepartmentForm()
    # template = 'employees/department/create_dept.html'

    # if request.method == 'POST':
    #     form = DepartmentForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         name = form.cleaned_data['name']
    #         messages.success(request, f'{name} added successfully!')
    #         return redirect('create_dept')

    # context = {'form' : form}
    # return render(request, template, context)

# def update_dept(request, pk):
    # context = {}
    # department = Department.objects.get(id=pk)
    # dept_name = department.name
    # form = DepartmentForm(instance=department)
    # template = 'employees/department/update_dept.html'
    # if request.method == 'POST':
    #     form = DepartmentForm(request.POST, instance=department)
    #     if form.is_valid():
    #         form.save()
    #         messages.success(request, f'{dept_name} updated to {department.name} successfully!')
    #         return redirect('department')
    
    # context = {'form': form}
    # return render(request, template, context)

# def delete_dept(request, pk):
    # department = Department.objects.get(id=pk)
    # template = 'employees/department/delete_dept.html'

    # if request.method == 'POST':
    #     department.delete()
    #     messages.success(request, f'{department.name} deleted successfully!')
    #     return redirect('department')
    
    # return render(request, template, {'department': department})

# DESIGNATION ################################################################
def position(request):
    positions = Position.objects.all()
    context = {'positions': positions}
    template = "employees/position/position.html"
    return render(request, template, context)

def create_position(request):
    context = {}
    form = PositionForm()
    template = 'employees/position/create_position.html'

    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data['name']
            messages.success(request, f'{name} added successfully!')
            return redirect('create_position')

    context = {'form' : form}
    return render(request, template, context)

def update_position(request, pk):
    context = {}
    template = 'employees/position/update_position.html'
    position = Position.objects.get(id=pk)
    position_name = position.name
    form = PositionForm(instance=position)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, f'{position_name} updated to {position.name} successfully!')
            return redirect('position')
    
    context = {'form': form}
    return render(request, template, context)

def delete_position(request, pk):
    position = Position.objects.get(id=pk)
    template = 'employees/position/delete_position.html'

    if request.method == 'POST':
        position.delete()
        messages.success(request, f'{position.name} deleted successfully!')
        return redirect('position')
    
    return render(request, template, {'position': position})

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

def view_emp(request, pk):
    emp_details = Employee.objects.filter(id=pk)
    id = emp_details[0].id
    context = {'emp_details': emp_details, 'emp_id':id}
    template = 'employees/employee/view_emp.html'
    return render(request, template, context)

def create_emp(request):
    context = {}
    form = EmployeeForm()
    template = 'employees/employee/create_emp.html'

    if Employee.objects.all().count() == 0:
        id_num = "001"
    else:
        recent_id = Employee.objects.latest('id')
        emp_id = str(recent_id).split('-')[2]

        numm = emp_id.replace("0", "")
        int_num = int(numm) + 1
        if len(str(int_num)) == 1:
            id_num = "00" + str(int_num)
        elif len(str(int_num)) == 2:
            id_num = "0" + str(int_num)
        else:
            id_num = str(int_num)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            id = form.cleaned_data['id']
            id_picture = request.FILES['id_picture']
            lastname = form.cleaned_data['lastname']
            firstname = form.cleaned_data['firstname']
            middlename = form.cleaned_data['middlename']
            # email = form.cleaned_data['email']
            birth_date = form.cleaned_data['birth_date']
            # gender = form.cleaned_data['gender']
            mobile_number = form.cleaned_data['mobile_number']
            barangay = form.cleaned_data['barangay']
            municipality = form.cleaned_data['municipality']
            province = form.cleaned_data['province']
            position = form.cleaned_data['position']
            date_employed = form.cleaned_data['date_employed']
            license_no = form.cleaned_data['license_no']
            registration_date = form.cleaned_data['registration_date']
            expiration_date = form.cleaned_data['expiration_date']

            # department = form.cleaned_data['department']
            # reportsTo = form.cleaned_data['reportsTo']

            file_name = default_storage.save(id_picture.name, id_picture)
            image_path = os.path.join(settings.MEDIA_ROOT, file_name)
            path_to_unregistered = os.path.join(settings.MEDIA_ROOT, "unregistered")
            image_checking = os.path.join(path_to_unregistered, file_name)

            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'registered')):
                    os.mkdir(os.path.join(settings.MEDIA_ROOT, 'registered'))

            if os.path.isfile(image_checking):
                os.remove(image_path)
                messages.warning(request, "ID picture already used!")
                return render(request, template, {'form':form, 'id_num':id_num})

            shutil.move(image_path, path_to_unregistered)
            test = checkIfExist(image_checking)

            if test is True:
                os.remove(image_checking)
                messages.warning(request, "Employee already registered!")
                return render(request, template, {'form':form, 'id_num':id_num})
            elif test is False:
                id_name = f'{id}_{lastname}, {firstname[0]}.'
                user = User.objects.create_user(id, "", id)
                register = Employee(user = user, id = id, lastname = lastname, firstname = firstname, middlename = middlename, birth_date = birth_date, mobile_number = mobile_number, barangay = barangay, municipality = municipality, province = province, date_employed = date_employed, position = position, id_picture = f'registered/{id_name}.jpg', license_no=license_no, registration_date=registration_date, expiration_date=expiration_date)
                user.save()
                register.save()
                new_image_path = os.path.join(settings.MEDIA_ROOT, f'registered/{id_name}.jpg')
                os.rename(image_checking, new_image_path)
                messages.success(request, f'Employee {id} registered successfully!')
                form = EmployeeForm()
                # return render(request, template, {'form':form, 'id_num':id_num})
                return redirect('create_emp')
            else:
                os.remove(image_checking)
                messages.error(request, "No face detected!")
                return render(request, template, {'form':form, 'id_num':id_num})

            # form.save()
            # return redirect('employee')

    context = {'form' : form, 'id_num':id_num}
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
        id_picture = request.FILES['id_picture']
        cbox = request.POST.get('cbox')

        file_name = default_storage.save(id_picture.name, id_picture)
        image_path = os.path.join(settings.MEDIA_ROOT, file_name)
        path_to_unregistered = os.path.join(settings.MEDIA_ROOT, "unregistered")
        path_to_registered = os.path.join(settings.MEDIA_ROOT, "registered")
        image_checking = os.path.join(path_to_unregistered, file_name)

        shutil.move(image_path, path_to_unregistered)

        # registered_image = os.path.join(path_to_registered, f'{pk}.jpg')
        registered_image = os.path.join(settings.MEDIA_ROOT, str(emp_details[0].id_picture))
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
            result = checkImage(image_checking, str(emp_details[0].id_picture))
            
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
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, emp_id.id_picture.name)):
            os.remove(os.path.join(settings.MEDIA_ROOT, emp_id.id_picture.name))
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