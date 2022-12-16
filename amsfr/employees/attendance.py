from .models import Attendance, Schedule
import datetime

def check_sched():
    check = Schedule.objects.filter(is_active=True)
    if check.count() == 0:
        return False

def checkpoint_am():
    now = datetime.datetime.now().time()
    start = now.replace(hour=6, minute=0, second=0, microsecond=0)
    sched = Schedule.objects.get(is_active=True)
    if now > start and now < sched.in_pm:
        return True
    else:
        return False


def mark_attendance(option, name):
    if option == 1:
        markAttendance = Attendance(employee_id = name, in_am = datetime.datetime.now().time(), date = datetime.datetime.now().date())
        checkID = Attendance.objects.filter(employee_id = name, date = datetime.datetime.now().date())
        if not checkID.exists():
            markAttendance.save()
    elif option == 2:
        getID = Attendance.objects.filter(employee_id = name, date = datetime.datetime.now().date()).values('id')[0]['id']
        if Attendance.objects.filter(id=getID, out_am__isnull=True):
            # print(getID)
            Attendance.objects.filter(id=getID).update(out_am=datetime.datetime.now().time())