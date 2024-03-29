from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    path('', home, name='home'),
    path('test/', test, name='test'),

    path('dashboard/', dashboard, name='dashboard'),

    # path('designation/', designation, name='designation'),
    # path('designation/create/', create_desig, name='create_desig'),
    # path('designation/update/<str:pk>/', update_desig, name='update_desig'),
    # path('designation/delete/<str:pk>/', delete_desig, name='delete_desig'),

    path('position/', position, name='position'),
    path('position/create/', create_position, name='create_position'),
    path('position/update/<str:pk>/', update_position, name='update_position'),
    path('position/delete/<str:pk>/', delete_position, name='delete_position'),

    path('schedule/', schedule, name='schedule'),
    path('schedule/create', create_sched, name='create_sched'),
    path('schedule/update/<str:pk>/', update_sched, name='update_sched'),
    path('schedule/delete/<str:pk>/', delete_sched, name='delete_sched'),
    path('schedule/activate/<str:pk>/', activate, name='activate'),
    path('schedule/deactivate/<str:pk>/', deactivate, name='deactivate'),

    path('holiday/', holiday, name='holiday'),
    path('holiday/import_holidays/', import_holidays, name='import_holidays'),
    path('holiday/create/', create_holiday, name='create_holiday'),
    
    path('employee/', employee, name='employee'),
    path('employee/create/', create_emp, name='create_emp'),
    path('employee/view/<str:pk>/', view_emp, name='view_emp'),
    path('employee/update/<str:pk>/', update_emp, name='update_emp'),
    path('employee/update_photo/<str:pk>/', update_photo, name='update_photo'),
    path('employee/delete/<str:pk>/', delete_emp, name='delete_emp'),

    path('dtr/dtr_by_date/', dtr_by_date, name="dtr_by_date"),
    path('dtr/dtr_by_employee/', dtr_by_employee, name="dtr_by_employee"),
    path('dtr/dtr_by_date/<str:date>/', dtr_specific_date, name="dtr_specific_date"),
    path('dtr/dtr_by_employee/<str:pk>/<str:date>/', dtr_specific_employee, name="dtr_specific_employee"),

    path('dtr/dtr_by_employee/<str:pk>/<str:date>/monthly/print/', print_monthly, name="print_monthly"),
    path('dtr/dtr_by_employee/<str:pk>/<str:date>/first-half/print/', print_first_half, name="print_first_half"),
    path('dtr/dtr_by_employee/<str:pk>/<str:date>/second-half/print/', print_second_half, name="print_second_half"),
    # path('dtr/print/pdf/', GeneratePdf.as_view()),

    path('attendance/', attendance, name='attendance'),
    path('attendance/in_am', in_am, name='in_am'),
    path('attendance/out_am', out_am, name='out_am'),
    path('attendance/in_pm', in_pm, name='in_pm'),
    path('attendance/out_pm', out_pm, name='out_pm'),
    path('attendance/logs_today', logs_today, name='logs_today'),
    path('attendance/full_logs_today', full_logs_today, name="full_logs_today"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)