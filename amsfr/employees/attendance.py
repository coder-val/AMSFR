from .models import Attendance, Schedule, Employee
import datetime
from django.conf import settings

def check_sched():
    check = Schedule.objects.filter(is_active=True)
    if check.count() == 0:
        return False

def checkpoint_in_am():
    now = datetime.datetime.now().time()
    sched = Schedule.objects.get(is_active=True)
    if now >= sched.in_am and now < sched.out_am:
        return True
    else:
        return False

def checkpoint_out_am():
    now = datetime.datetime.now().time()
    sched = Schedule.objects.get(is_active=True)
    if now >= sched.out_am and now < sched.in_pm:
        return True
    else:
        return False

def checkpoint_in_pm():
    now = datetime.datetime.now().time()
    sched = Schedule.objects.get(is_active=True)
    if now >= sched.in_pm and now < sched.out_pm:
        return True
    else:
        return False

def checkpoint_out_pm():
    now = datetime.datetime.now().time()
    cut_off = now.replace(hour=23, minute=59, second=59, microsecond=0)
    sched = Schedule.objects.get(is_active=True)
    if now >= sched.out_pm and now < cut_off:
        return True
    else:
        return False

def convert_to_timedelta(time):
    td_time = datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)
    return td_time

def convert_to_timedelta_2(time):
    td_time = datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)
    return td_time

# def check_ut_or_ot(time):
#     result = 0
#     if time < 480:
#         result = 480 - time
#     elif time > 480:
#         result = time - 480
#     return result

def convert_time_to_minutes(time):
    s_time = str(time).split(':')
    c_time = int(s_time[0])*60 + int(s_time[1]) + int(s_time[2])/60
    return int(c_time)

def calc_minutes_worked(in_am, out_am, in_pm, out_pm):
    if in_am and out_am:
        am_time = convert_to_timedelta_2(out_am) - convert_to_timedelta_2(in_am)
    else:
        am_time = datetime.timedelta(hours=0, minutes=0, seconds=0)

    if in_pm and out_pm:
        pm_time = convert_to_timedelta_2(out_pm) - convert_to_timedelta_2(in_pm)
    else:
        pm_time = datetime.timedelta(hours=0, minutes=0, seconds=0)

    calc = am_time + pm_time
    return calc

def mark_attendance(name):
    time_now = datetime.datetime.now().time()
    date_now = datetime.datetime.now().date()
    td_time_now = datetime.timedelta(hours=time_now.hour, minutes=time_now.minute, seconds=time_now.second)
    threshold = datetime.timedelta(minutes=settings.THRESHOLD)

    sched = Schedule.objects.filter(is_active=True).values()

    td_in_am = convert_to_timedelta(sched[0]['in_am'])
    td_out_am = convert_to_timedelta(sched[0]['out_am'])
    td_in_pm = convert_to_timedelta(sched[0]['in_pm'])
    td_out_pm = convert_to_timedelta(sched[0]['out_pm'])

    #IN AM
    if td_time_now >= datetime.timedelta(hours=6) and td_time_now < td_out_am:
        if td_time_now <= td_in_am + threshold:
            remarks = 'P'
        else:
            remarks = 'L'
        markAttendance = Attendance(reference = Employee.objects.get(id=name), employee_id = name, in_am = time_now, date = date_now, remarks = remarks)
        checkID = Attendance.objects.filter(employee_id = name, date = date_now)
        if not checkID.exists():
            markAttendance.save()
    #OUT AM
    elif td_time_now >= td_out_am and td_time_now < datetime.timedelta(hours=12):
        remarks = 'L'
        checkID = Attendance.objects.filter(employee_id = name, date = date_now)
        if not checkID.exists():
            Attendance.objects.create(reference = Employee.objects.get(id=name), employee_id = name, out_am = time_now, date = date_now, remarks = remarks)
        else:
            # if checkID.filter(in_am__isnull=False):
            #     log = checkID[0].in_am
            #     print(log)
            #     if td_time_now > convert_to_timedelta_2(log) + datetime.timedelta(minutes=5):
            Attendance.objects.filter(employee_id = name, in_am__isnull=False, out_am__isnull=True, in_pm__isnull=True, out_pm__isnull=True, date = date_now).update(out_am=time_now)
    #IN PM
    elif td_time_now >= datetime.timedelta(hours=12) and td_time_now < td_out_pm:
        if td_time_now <= td_in_pm + threshold:
            remarks = 'P'
        else:
            remarks = 'L'
        checkID = Attendance.objects.filter(employee_id = name, date = date_now)
        if not checkID.exists():
            Attendance.objects.create(reference = Employee.objects.get(id=name), employee_id = name, in_pm = time_now, date = date_now, remarks = remarks)
        else:
            # if checkID.filter(out_am__isnull=False).exists():
            #     log = checkID[0].out_am
            #     if td_time_now > convert_to_timedelta_2(log) + datetime.timedelta(minutes=5):
            Attendance.objects.filter(employee_id = name, in_pm__isnull = True, date = date_now).update(in_pm = time_now)
    #OUT PM
    elif td_time_now >= td_out_pm and td_time_now <= datetime.timedelta(hours=23, minutes=59, seconds=59):
        remarks = 'L'
        checkID = Attendance.objects.filter(employee_id = name, date = date_now)
        if not checkID.exists():
            Attendance.objects.create(reference = Employee.objects.get(id=name), employee_id = name, out_pm = time_now, date = date_now, remarks = remarks)
        else:
            Attendance.objects.filter(employee_id = name, out_pm__isnull=True, date = date_now).update(out_pm=time_now)

def get_Remarks():
    time_now = datetime.datetime.now().time()
    td_time_now = datetime.timedelta(hours=time_now.hour, minutes=time_now.minute, seconds=time_now.second)
    threshold = datetime.timedelta(minutes=settings.THRESHOLD)

    sched = Schedule.objects.filter(is_active=True).values()

    td_in_am = convert_to_timedelta(sched[0]['in_am'])
    td_out_am = convert_to_timedelta(sched[0]['out_am'])
    td_in_pm = convert_to_timedelta(sched[0]['in_pm'])
    td_out_pm = convert_to_timedelta(sched[0]['out_pm'])

    #IN AM
    if td_time_now >= datetime.timedelta(hours=6) and td_time_now < td_out_am:
        if td_time_now <= td_in_am + threshold:
            remarks = 'EARLY'
        else:
            remarks = 'LATE'
    #OUT AM
    elif td_time_now >= td_out_am and td_time_now < datetime.timedelta(hours=12):
        remarks = 'LATE'
    #IN PM
    elif td_time_now >= datetime.timedelta(hours=12) and td_time_now < td_out_pm:
        if td_time_now <= td_in_pm + threshold:
            remarks = 'EARLY'
        else:
            remarks = 'LATE'
    #OUT PM
    elif td_time_now >= td_out_pm and td_time_now <= datetime.timedelta(hours=23, minutes=59, seconds=59):
        remarks = 'LATE'

    return remarks
        
def mark_attendance_old(option, name):
    time_now = datetime.datetime.now().time()
    dt_time_now = datetime.timedelta(hours=time_now.hour, minutes=time_now.minute, seconds=time_now.second, microseconds=time_now.microsecond)
    date_now = datetime.datetime.now().date()
    sched = Schedule.objects.get(is_active=True)
    
    if option == 1:
        am_in = datetime.timedelta(hours=sched.in_am.hour, minutes=sched.in_am.minute, seconds=sched.in_am.second, microseconds=sched.in_am.microsecond)
        threshold = datetime.timedelta(minutes=30)
        if dt_time_now <= (am_in+threshold):
            remarks = 'P'
        else:
            remarks = 'L'

        markAttendance = Attendance(reference = Employee.objects.get(id=name), employee_id = name, in_am = time_now, date = date_now, remarks = remarks)
        checkID = Attendance.objects.filter(employee_id = name, date = date_now)
        if not checkID.exists():
            markAttendance.save()

    elif option == 2:
        remarks = 'L'
        checkID = Attendance.objects.filter(employee_id = name, date = date_now)
        if not checkID.exists():
            Attendance.objects.create(reference = Employee.objects.get(id=name), employee_id = name, out_am = time_now, date = date_now, remarks = remarks)
        else:
            Attendance.objects.filter(employee_id = name, out_am__isnull=True, date = date_now).update(out_am=time_now)

    elif option == 3:
        pm_in = datetime.timedelta(hours=sched.in_pm.hour, minutes=sched.in_pm.minute, seconds=sched.in_pm.second, microseconds=sched.in_pm.microsecond)
        threshold = datetime.timedelta(minutes=30)
        if dt_time_now <= (pm_in+threshold):
            remarks = 'P'
        else:
            remarks = 'L'

        checkID = Attendance.objects.filter(employee_id = name, date = date_now)
        if not checkID.exists():
            Attendance.objects.create(reference = Employee.objects.get(id=name), employee_id = name, in_pm = time_now, date = date_now, remarks = remarks)
        else:
            Attendance.objects.filter(employee_id = name, in_pm__isnull = True, date = date_now).update(in_pm = time_now)
    elif option == 4:
        remarks = 'L'
        checkID = Attendance.objects.filter(employee_id = name, date = date_now)
        if not checkID.exists():
            Attendance.objects.create(reference = Employee.objects.get(id=name), employee_id = name, out_pm = time_now, date = date_now, remarks = remarks)
        else:
            Attendance.objects.filter(employee_id = name, out_pm__isnull=True, date = date_now).update(out_pm=time_now)