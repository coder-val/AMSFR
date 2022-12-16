from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    path('', home, name='home'),

    path('department/', department, name='department'),
    path('department/create/', create_dept, name='create_dept'),
    path('department/update/<str:pk>/', update_dept, name='update_dept'),
    path('department/delete/<str:pk>/', delete_dept, name='delete_dept'),

    path('designation/', designation, name='designation'),
    path('designation/create/', create_desig, name='create_desig'),
    path('designation/update/<str:pk>/', update_desig, name='update_desig'),
    path('designation/delete/<str:pk>/', delete_desig, name='delete_desig'),

    path('schedule/', schedule, name='schedule'),
    path('schedule/create', create_sched, name='create_sched'),
    path('schedule/update/<str:pk>/', update_sched, name='update_sched'),
    path('schedule/delete/<str:pk>/', delete_sched, name='delete_sched'),
    path('schedule/activate/<str:pk>/', activate, name='activate'),
    
    path('employee/', employee, name='employee'),
    path('employee/create/', create_emp, name='create_emp'),
    path('employee/update/<str:pk>/', update_emp, name='update_emp'),
    path('employee/delete/<str:pk>/', delete_emp, name='delete_emp'),

    path('attendance/', attendance, name='attendance'),
    path('attendance/in_am', in_am, name='in_am'),
    path('attendance/out_am', out_am, name='out_am'),
    path('attendance/monitor', monitor, name='monitor'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)