from .models import Attendance, Schedule, Employee
import datetime

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

def mark_attendance(option, name):
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