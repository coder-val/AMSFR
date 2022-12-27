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
    if option == 1:
        markAttendance = Attendance(reference = Employee.objects.get(id=name), employee_id = name, in_am = datetime.datetime.now().time(), date = datetime.datetime.now().date())
        checkID = Attendance.objects.filter(employee_id = name, date = datetime.datetime.now().date())
        if not checkID.exists():
            markAttendance.save()
    elif option == 2:
        checkID = Attendance.objects.filter(employee_id = name, date = datetime.datetime.now().date())
        if not checkID.exists():
            Attendance.objects.create(reference = Employee.objects.get(id=name), employee_id = name, out_am = datetime.datetime.now().time(), date = datetime.datetime.now().date())
        else:
            Attendance.objects.filter(employee_id = name, out_am__isnull=True, date = datetime.datetime.now().date()).update(out_am=datetime.datetime.now().time())
    elif option == 3:
        checkID = Attendance.objects.filter(employee_id = name, date = datetime.datetime.now().date())
        if not checkID.exists():
            Attendance.objects.create(reference = Employee.objects.get(id=name), employee_id = name, in_pm = datetime.datetime.now().time(), date = datetime.datetime.now().date())
        else:
            Attendance.objects.filter(employee_id = name, in_pm__isnull=True, date = datetime.datetime.now().date()).update(in_pm=datetime.datetime.now().time())
    elif option == 4:
        checkID = Attendance.objects.filter(employee_id = name, date = datetime.datetime.now().date())
        if not checkID.exists():
            Attendance.objects.create(reference = Employee.objects.get(id=name), employee_id = name, out_pm = datetime.datetime.now().time(), date = datetime.datetime.now().date())
        else:
            Attendance.objects.filter(employee_id = name, out_pm__isnull=True, date = datetime.datetime.now().date()).update(out_pm=datetime.datetime.now().time())