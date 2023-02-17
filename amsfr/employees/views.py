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
# from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import StreamingHttpResponse, HttpResponse
from .camera import *
import calendar

from django.views.generic import View
from .process import html_to_pdf
from django.template.loader import render_to_string

import os
from django.template.loader import get_template
from xhtml2pdf import pisa


def convert_time(time):
    if time >= dt.time(1,0,0) and time < dt.time(11,59,59):
        str_time = time.strftime("%H:%M:%S")
        real_time = dt.datetime.now().strptime(str_time, "%H:%M:%S")
        convert = real_time + timedelta(hours=12)
        return convert
    return time

def get_age(birthdate):
    today = dt.date.today()
    print(today)
    one_or_zero = ((today.month, today.day) < (birthdate.month, birthdate.day))
    year_difference = today.year - birthdate.year
    age = year_difference - one_or_zero
    return age

# Create your views here.
# class GeneratePdf(View):
#     def get(self, request, *args, **kwargs):
#         data = Attendance.objects.all()
#         open('templates/temp.html', "w").write(render_to_string('print.html',{'data':data}))

#         pdf = html_to_pdf('temp.html')

#         return HttpResponse(pdf, content_type='application/pdf')

def print_first_half(request, pk, date):
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
    regulars = []

    year_date = date.split("-")[0]
    month_date = date.split("-")[1]

    now = dt.date(year=int(year_date), month=int(month_date), day=1)
    days_in_month = calendar.monthrange(int(year_date), int(month_date))[1]
    dates = [dt.datetime(year=int(year_date), month=int(month_date), day=x).date() for x in range(1, 15+1)]
    total_hours = 0
    attendance_dates = Attendance.objects.filter(date__month=int(month_date), date__year=int(year_date), date__range=[now, now.replace(day=15)]).values_list('date', flat=True).distinct().order_by('date')
    emp_name = Employee.objects.filter(id=pk)
    emp_logs = Attendance.objects.filter(employee_id=pk, date__month=int(month_date), date__year=int(year_date), date__range=[now, now.replace(day=15)]).order_by('date')
    r = 0
    y = 0
    z = 0
    for x in range(1, days_in_month+1):
        try:
            d = dt.datetime.strptime(str(attendance_dates[r]), "%Y-%m-%d").date().day
        except IndexError:
            regulars.append(False)
        try:
            # d = dt.datetime.strptime(str(attendance_dates[r]), "%Y-%m-%d").date().day
            # print(d)
            h = dt.datetime.strptime(str(dates[z]), "%Y-%m-%d").date()

            if ph_calendar.is_holiday(h):
                holidays.append(True)
                z+=1
            else:
                holidays.append(False)
                z+=1
            
            if d == x:
                regulars.append(True)
                r+=1
            else:
                regulars.append(False)
            

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

    days_worked = [x for x in emp_remarks if x !=""]
    lates = [x for x in emp_remarks if x =="L"]
    absents = len(attendance_dates) - len(days_worked)
    ut = [x for x in undertime if x != ""]
    ot = [x for x in overtime if x != ""]

    signatory = Signatory.objects.first()
    sets = zip(dates, emp_in_am, emp_out_am, emp_in_pm, emp_out_pm, emp_remarks, undertime, overtime, minutes_worked, holidays, regulars)
    
    context = {'employee':emp_name, 'logs':sets, 'total':round(total_hours/60, 2), 'days_worked':len(days_worked), 'lates':len(lates), 'absents':absents, 'undertime':len(ut), 'overtime':len(ot), 'month':now, 'dt':dt.datetime.now(), 'signatory':signatory}



    # data = Employee.objects.all()
    open('templates/temp.html', "w").write(render_to_string('print.html',context))

    pdf = html_to_pdf('temp.html')

    return HttpResponse(pdf, content_type='application/pdf')

def print_second_half(request, pk, date):
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
    regulars = []

    year_date = date.split("-")[0]
    month_date = date.split("-")[1]

    now = dt.date(year=int(year_date), month=int(month_date), day=1)
    days_in_month = calendar.monthrange(int(year_date), int(month_date))[1]
    dates = [dt.datetime(year=int(year_date), month=int(month_date), day=x).date() for x in range(16, days_in_month+1)]
    total_hours = 0
    attendance_dates = Attendance.objects.filter(date__month=int(month_date), date__year=int(year_date), date__range=[now.replace(day=16), now.replace(day=days_in_month)]).values_list('date', flat=True).distinct().order_by('date')
    emp_name = Employee.objects.filter(id=pk)
    emp_logs = Attendance.objects.filter(employee_id=pk, date__month=int(month_date), date__year=int(year_date), date__range=[now.replace(day=16), now.replace(day=days_in_month)]).order_by('date')
    r = 0
    y = 0
    z = 0
    for x in range(16, days_in_month+1):
        try:
            d = dt.datetime.strptime(str(attendance_dates[r]), "%Y-%m-%d").date().day
        except IndexError:
            regulars.append(False)
        try:
            # d = dt.datetime.strptime(str(attendance_dates[r]), "%Y-%m-%d").date().day
            # print(d)
            h = dt.datetime.strptime(str(dates[z]), "%Y-%m-%d").date()

            if ph_calendar.is_holiday(h):
                holidays.append(True)
                z+=1
            else:
                holidays.append(False)
                z+=1
            
            if d == x:
                regulars.append(True)
                r+=1
            else:
                regulars.append(False)
            

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
    

    days_worked = [x for x in emp_remarks if x !=""]
    lates = [x for x in emp_remarks if x =="L"]
    absents = len(attendance_dates) - len(days_worked)
    ut = [x for x in undertime if x != ""]
    ot = [x for x in overtime if x != ""]

    signatory = Signatory.objects.first()
    sets = zip(dates, emp_in_am, emp_out_am, emp_in_pm, emp_out_pm, emp_remarks, undertime, overtime, minutes_worked, holidays, regulars)
    
    context = {'employee':emp_name, 'logs':sets, 'total':round(total_hours/60, 2), 'days_worked':len(days_worked), 'lates':len(lates), 'absents':absents, 'undertime':len(ut), 'overtime':len(ot), 'month':now, 'dt':dt.datetime.now(), 'signatory':signatory}



    # data = Employee.objects.all()
    open('templates/temp.html', "w").write(render_to_string('print.html',context))

    pdf = html_to_pdf('temp.html')

    return HttpResponse(pdf, content_type='application/pdf')

def print_monthly(request, pk, date):
    # pk = "400392-23-001"

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
    regulars = []

    year_date = date.split("-")[0]
    month_date = date.split("-")[1]

    now = dt.date(year=int(year_date), month=int(month_date), day=1)
    days_in_month = calendar.monthrange(int(year_date), int(month_date))[1]
    dates = [dt.datetime(year=int(year_date), month=int(month_date), day=x).date() for x in range(1, days_in_month+1)]
    total_hours = 0
    attendance_dates = Attendance.objects.filter(date__month=int(month_date), date__year=int(year_date)).values_list('date', flat=True).distinct().order_by('date')
    emp_name = Employee.objects.filter(id=pk)
    emp_logs = Attendance.objects.filter(employee_id=pk, date__month=int(month_date), date__year=int(year_date)).order_by('date')
    r = 0
    y = 0
    z = 0
    for x in range(1, days_in_month+1):
        try:
            d = dt.datetime.strptime(str(attendance_dates[r]), "%Y-%m-%d").date().day
        except IndexError:
            regulars.append(False)
        try:
            # d = dt.datetime.strptime(str(attendance_dates[r]), "%Y-%m-%d").date().day
            # print(d)
            h = dt.datetime.strptime(str(dates[z]), "%Y-%m-%d").date()

            if ph_calendar.is_holiday(h):
                holidays.append(True)
                z+=1
            else:
                holidays.append(False)
                z+=1
            
            if d == x:
                regulars.append(True)
                r+=1
            else:
                regulars.append(False)
            

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

    days_worked = [x for x in emp_remarks if x !=""]
    lates = [x for x in emp_remarks if x =="L"]
    absents = len(attendance_dates) - len(days_worked)
    ut = [x for x in undertime if x != ""]
    ot = [x for x in overtime if x != ""]

    signatory = Signatory.objects.first()
    sets = zip(dates, emp_in_am, emp_out_am, emp_in_pm, emp_out_pm, emp_remarks, undertime, overtime, minutes_worked, holidays, regulars)
    
    context = {'employee':emp_name, 'logs':sets, 'total':round(total_hours/60, 2), 'days_worked':len(days_worked), 'lates':len(lates), 'absents':absents, 'undertime':len(ut), 'overtime':len(ot), 'month':now, 'dt':dt.datetime.now(), 'signatory':signatory}



    # data = Employee.objects.all()
    open('templates/temp.html', "w").write(render_to_string('print.html',context))

    pdf = html_to_pdf('temp.html')

    return HttpResponse(pdf, content_type='application/pdf')

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

        if now_time >= dt.timedelta(hours=6) and now_time < dt.timedelta(hours=12):
            insides = Attendance.objects.filter(in_am__isnull=False, out_am__isnull=True, date=now_date).order_by('-in_am')
            outsides = Attendance.objects.filter(in_am__isnull=False, out_am__isnull=False, date=now_date).order_by('-out_am') | Attendance.objects.filter(in_am__isnull=True, out_am__isnull=False, date=now_date).order_by('-out_am')
            context = {'insides':insides, 'outsides':outsides}

        elif now_time >= dt.timedelta(hours=12) and now_time < cut_off:
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
    print(settings.BASE_DIR)
    context = {}
    template = "employees/dashboard.html"

    morning = "Good Morning!"
    afternoon = "Good Afternoon!"
    date_now = dt.datetime.now().date()

    if convert_to_timedelta_2(dt.datetime.now().time()) >= dt.timedelta(hours=12) and convert_to_timedelta_2(dt.datetime.now().time()) <= dt.timedelta(hours=23, minutes=59, seconds=59):
        greetings = afternoon
    else:
        greetings = morning

    total = Employee.objects.all().count()
    q = Attendance.objects.filter(date = dt.datetime.now().date())
    # q = Attendance.objects.filter(date = dt.date(year=2023, month=1, day=3))
    present = q.filter(remarks="P") | q.filter(remarks="L")
    late = q.filter(remarks="L")
    p = present.count()
    l = late.count()
    if q.exists() and total >= q.count():
        a = total - p
    else:
        a = 0

    context = {'present': p, 'late':l, 'absent':a, 'greetings': greetings, 'date':date_now}

    return render(request, template, context)

# def test_print(request):
#     context = {}
#     template = "employees/pdf/print.html"
#     return render(request, template, context)

@login_required
def dtr_by_date(request):
    context = {}
    template = 'employees/dtr/dtr_by_date.html'

    ph_calendar = Philippines()
    total = Employee.objects.count()

    if request.method == "POST":
        p = request.POST.get('month').split('-')
        date_year = p[0]
        date_month = p[1]
        if date_month[0] == "0":
            date_month = date_month.replace("0", "")
        year_month = dt.date(year=int(date_year), month=int(date_month), day=1)
    else:
        date_year = dt.datetime.now().date().year
        date_month = dt.datetime.now().date().month
        year_month = dt.datetime.now().date()
        

    # dates = Attendance.objects.values_list('date', flat=True).order_by('-date').distinct().filter(date__month=dt.datetime.now().date().month)
    # dates_list = Attendance.objects.values_list('date', flat=True).order_by('date').distinct()
    # p = Paginator(dates, per_page=5, orphans=1)
    # page_number = request.GET.get('page')
    # p_dates = p.get_page(page_number)
    # now = dt.datetime.now().date()
    days_in_month = calendar.monthrange(int(date_year), int(date_month))[1]
    attendance_dates = Attendance.objects.filter(date__month=int(date_month), date__year=int(date_year)).values_list('date', flat=True).distinct().order_by('date')
    dates = [dt.datetime(year=int(date_year), month=int(date_month), day=x).date() for x in range(1, days_in_month+1)]
    presents = []
    absents = []
    holidays = []
    regulars = []
    r = 0
    y = 0
    z = 0
    
    for x in range(1, len(dates) + 1):
        try:
            dd = dt.datetime.strptime(str(attendance_dates[r]), "%Y-%m-%d").date().day
            d = dt.datetime.strptime(str(attendance_dates[y]), "%Y-%m-%d").date().day
            h = dt.datetime.strptime(str(dates[z]), "%Y-%m-%d").date()

            if ph_calendar.is_holiday(h):
                holidays.append(True)
            else:
                holidays.append(False)

            if dd == x:
                regulars.append(True)
                r+=1
            else:
                regulars.append(False)

            if  d == x:
                p = Attendance.objects.filter(date=attendance_dates[y]).count()
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
    regulars.reverse()
    items = zip(dates,presents,absents,holidays, regulars)
    # print(len(dates), len(presents), len(absents), len(holidays), len(regulars))
    # print(pd.DataFrame(items, columns=['dates','presents','absents','holidays', 'regulars']))
    context = {'dates':items}
    # if request.htmx:
    #     return render(request, 'employees/partials/dtr_by_date.html', context)
    return render(request, template, context)

@login_required
def dtr_specific_date(request, date):
    absentees = []
    context = {}
    template = 'employees/dtr/dtr_by_date_specific.html'

    d = date.split('-')
    n_date = dt.date(year=int(d[0]),month=int(d[1]), day=int(d[2]))

    logs = Attendance.objects.filter(date=n_date).order_by('reference__lastname')
    if logs.exists():
        absents = Employee.objects.exclude(id__in=[logs[x].employee_id for x in range(logs.count())])
    else:
        absents = None
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
    context = {'logs':sets, 'date':n_date, 'absents':absents}

    return render(request, template, context)

@login_required
def dtr_by_employee(request):
    context = {}
    template = 'employees/dtr/dtr_by_employee.html'

    if request.method == "POST":
        p = request.POST.get('month').split('-')
        date_year = p[0]
        date_month = p[1]
        if date_month[0] == "0":
            date_month = date_month.replace("0", "")
        year_month = dt.date(year=int(date_year), month=int(date_month), day=1)
    else:
        date_year = dt.datetime.now().date().year
        date_month = dt.datetime.now().date().month
        year_month = dt.datetime.now().date()

    
    # year_now = dt.datetime.now().date().year
    # year_earliest = Attendance.objects.earliest('date').date.year
    # years_list = list(range(year_now, year_now-((year_now-year_earliest)+1), -1))
    # print(str(years_list))
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
        attendance_list = Attendance.objects.all().filter(date__month=int(date_month), date__year=int(date_year))
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
    context = {'employees':sets, 'year_month':year_month}

    return render(request, template, context)

@login_required
def dtr_specific_employee(request, pk, date):
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
    regulars = []
    date_year = date.split("-")[0]
    date_month = date.split("-")[1]
    year_month = dt.date(year=int(date_year), month=int(date_month), day=1)
    days_in_month = calendar.monthrange(int(date_year), int(date_month))[1]
    dates = [dt.datetime(year=int(date_year), month=int(date_month), day=x).date() for x in range(1, days_in_month+1)]
    total_hours = 0

    emp_name = Employee.objects.filter(id=pk)
    print(emp_name)
    emp_logs = Attendance.objects.filter(employee_id=pk, date__month=date_month).order_by('date')
    print(emp_logs)
    attendance_dates = Attendance.objects.filter(date__month=int(date_month), date__year=int(date_year)).values_list('date', flat=True).distinct().order_by('date')
    print(attendance_dates)
    r = 0
    y = 0
    z = 0
    for x in range(1, len(dates)+1):
        try:
            d = dt.datetime.strptime(str(attendance_dates[r]), "%Y-%m-%d").date().day
        except IndexError:
            regulars.append(False)
        try:
            
            h = dt.datetime.strptime(str(dates[z]), "%Y-%m-%d").date()

            if ph_calendar.is_holiday(h):
                holidays.append(True)
                z+=1
            else:
                holidays.append(False)
                z+=1

            if d == x:
                regulars.append(True)
                r+=1
            else:
                regulars.append(False)

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
            
    # print(emp_in_am, emp_out_am, emp_in_pm, emp_out_pm, emp_remarks, minutes_worked, undertime, overtime, holidays, regulars)
    # print(regulars)
    
    sets = zip(dates, emp_in_am, emp_out_am, emp_in_pm, emp_out_pm, emp_remarks, undertime, overtime, minutes_worked, holidays, regulars)
    
    context = {'employee':emp_name, 'logs':sets, 'total':round(total_hours/60, 2), 'date':date, 'year_month':year_month}
    return render(request, template, context)
# DESIGNATION ################################################################
# @login_required
# def designation(request):
#     designations = Designation.objects.all()
#     context = {'designations': designations}
#     template = 'employees/designation/designation.html'
#     return render(request, template, context)

# @login_required
# def create_desig(request):
#     context = {}
#     form = DesignationForm()
#     template = 'employees/designation/create_desig.html'

#     if request.method == 'POST':
#         form = DesignationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             name = form.cleaned_data['name']
#             messages.success(request, f'{name} added successfully!')
#             return redirect('create_desig')

#     context = {'form' : form}
#     return render(request, template, context)

# @login_required
# def update_desig(request, pk):
#     context = {}
#     designation = Designation.objects.get(id=pk)
#     desig_name = designation.name
#     form = DesignationForm(instance=designation)
#     template = 'employees/designation/update_desig.html'
#     if request.method == 'POST':
#         form = DesignationForm(request.POST, instance=designation)
#         if form.is_valid():
#             form.save()
#             messages.success(request, f'{desig_name} updated to {designation.name} successfully!')
#             return redirect('designation')
    
#     context = {'form': form}
#     return render(request, template, context)

# @login_required
# def delete_desig(request, pk):
    designation = Designation.objects.get(id=pk)
    template = 'employees/designation/delete_desig.html'

    if request.method == 'POST':
        designation.delete()
        messages.success(request, f'{designation.name} deleted successfully!')
        return redirect('designation')
    
    return render(request, template, {'designation': designation})

# POSITION ################################################################
@login_required
def position(request):
    positions = Position.objects.all()
    context = {'positions': positions}
    template = "employees/position/position.html"
    return render(request, template, context)

@login_required
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

@login_required
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

@login_required
def delete_position(request, pk):
    position = Position.objects.get(id=pk)
    template = 'employees/position/delete_position.html'

    if request.method == 'POST':
        position.delete()
        messages.success(request, f'{position.name} deleted successfully!')
        return redirect('position')
    
    return render(request, template, {'position': position})

# SCHEDULE #####################################################################
@login_required
def activate(request, pk):
    Schedule.objects.filter(id=pk).update(is_active=True)
    Schedule.objects.filter(is_active=True).exclude(id=pk).update(is_active=False)
    messages.success(request, "activated successfully!")
    return redirect('schedule')

@login_required
def deactivate(request, pk):
    Schedule.objects.filter(id=pk).update(is_active=False)
    messages.success(request, "deactivated successfully!")
    return redirect('schedule')

@login_required
def schedule(request):
    # schedules = Schedule.objects.all()
    context = {}
    template = "employees/schedule/schedule.html"
    # admins = Employee.objects.filter(position__name="admin")
    admins = Employee.objects.all()

    active_sched = Schedule.objects.filter(is_active=True)
    inactive_sched = Schedule.objects.filter(is_active=False)
    current_signatory = Signatory.objects.all()

    if request.method == "POST":
        signatory = request.POST.get('signatory')
        name = signatory.split("_")[0]
        position = signatory.split("_")[1]
        s = Signatory.objects.all().count()
        if s == 0:
            Signatory.objects.create(signatory=name, position=position)
        else:
            Signatory.objects.update(signatory=name, position=position)
        messages.success(request, "Signatory updated successfully!")
        return redirect('schedule')

    context = {'admins':admins, 'current':current_signatory, 'active_sched': active_sched, 'inactive_sched':inactive_sched}

    return render(request, template, context)

@login_required
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

@login_required
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

@login_required
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
@login_required
def employee(request):
    employees = Employee.objects.all().order_by('id')
    p = Paginator(employees, 10)
    page_number = request.GET.get('page')
    p_employees = p.get_page(page_number)
    emp_count = employees.count()
    context = {'employees': p_employees, 'count':emp_count}
    template = "employees/employee/employee.html"
    return render(request, template, context)

@login_required
def view_emp(request, pk):
    emp_details = Employee.objects.filter(id=pk)
    id = emp_details[0].id
    try:
        birthdate = emp_details[0].birth_date
        age = get_age(birthdate)
    except:
        age = None

    context = {'emp_details': emp_details, 'emp_id':id, 'age': age}
    template = 'employees/employee/view_emp.html'
    return render(request, template, context)

@login_required
def create_emp(request):
    context = {}
    form = EmployeeForm()
    template = 'employees/employee/create_emp.html'
    
    id_prefix = "400392-23-"

    if Employee.objects.all().count() == 0:
        id_num = "001"
    else:
        recent_id = Employee.objects.latest('id')
        emp_id = str(recent_id).split('-')[2]

        if emp_id[2] == "0":
            numm = emp_id.replace("0", "", 1)
        else:
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
            # id = form.cleaned_data['id']
            id = id_prefix+id_num
            id_picture = request.FILES['id_picture']
            lastname = form.cleaned_data['lastname']
            firstname = form.cleaned_data['firstname']
            middlename = form.cleaned_data['middlename']
            suffix = form.cleaned_data['suffix']
            # email = form.cleaned_data['email']
            birth_date = form.cleaned_data['birth_date']
            # gender = form.cleaned_data['gender']
            mobile_number = form.cleaned_data['mobile_number']
            barangay = form.cleaned_data['barangay']
            municipality = form.cleaned_data['municipality']
            province = form.cleaned_data['province']
            position = form.cleaned_data['position']
            # designation = form.cleaned_data['designation']
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
                return render(request, template, {'form':form})

            shutil.move(image_path, path_to_unregistered)
            # test = checkIfExist(image_checking)

            # if test is True:
            #     os.remove(image_checking)
            #     messages.warning(request, "Employee already registered!")
            #     return render(request, template, {'form':form, 'id_num':id_num})
            # elif test is False:
            id_name = f'{id}_{lastname.title()}, {firstname.title()}'
            # user = User.objects.create_user(id, "", id)
            # register = Employee(user = user, id = id, lastname = lastname, firstname = firstname, middlename = middlename, birth_date = birth_date, mobile_number = mobile_number, barangay = barangay, municipality = municipality, province = province, date_employed = date_employed, position = position, id_picture = f'registered/{id_name}.jpg', license_no=license_no, registration_date=registration_date, expiration_date=expiration_date)
            register = Employee(id = id, lastname = lastname.title(), firstname = firstname.title(), middlename = middlename.title(), suffix = suffix, birth_date = birth_date, mobile_number = mobile_number, barangay = barangay.title(), municipality = municipality.title(), province = province.title(), date_employed = date_employed, position = position, id_picture = f'registered/{id_name}.jpg', license_no=license_no, registration_date=registration_date, expiration_date=expiration_date)
            # user.save()
            register.save()
            new_image_path = os.path.join(settings.MEDIA_ROOT, f'registered/{id_name}.jpg')
            os.rename(image_checking, new_image_path)
            messages.success(request, f'Employee {id} registered successfully!')
            form = EmployeeForm()
            # return render(request, template, {'form':form, 'id_num':id_num})
            return redirect('create_emp')
            # else:
            #     os.remove(image_checking)
            #     messages.error(request, "No face detected!")
            #     return render(request, template, {'form':form, 'id_num':id_num})

            # form.save()
            # return redirect('employee')

    context = {'form' : form, 'id_num':id_num}
    return render(request, template, context)

@login_required
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

@login_required
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

@login_required
def delete_emp(request, pk):
    emp_id = Employee.objects.get(id=pk)
    # emp_user = User.objects.get(username=emp_id)
    template = 'employees/employee/delete_emp.html'

    if request.method == 'POST':
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, emp_id.id_picture.name)):
            os.remove(os.path.join(settings.MEDIA_ROOT, emp_id.id_picture.name))
        # employee.delete()
        # emp_user.delete()
        messages.success(request, f'Employee {emp_id} deleted successfully!')
        emp_id.delete()
        return redirect('employee')
    
    return render(request, template, {'employee': emp_id})

# HOLIDAY ###############################################################
@login_required
def holiday(request):
    holidays = Holiday.objects.all()
    context = {'holidays': holidays}
    template = 'employees/holiday.html'
    return render(request, template, context)

@login_required
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

@login_required
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