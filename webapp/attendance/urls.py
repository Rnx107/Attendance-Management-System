from django.urls import path
from . import views

urlpatterns = [
    path('mark/<uuid:session_id>/', views.mark_attendance, name='mark_attendance'),
    path('verify/<uuid:session_id>/', views.teacher_verify_attendance, name='teacher_verify_attendance'),
    path('admin/session/<uuid:session_id>/', views.admin_session_attendance, name='admin_session_attendance'),
    path('create/', views.create_session, name='create_session'),
    path('export/excel/<uuid:subject_id>/', views.export_subject_attendance_excel, name='export_subject_attendance_excel'),
]
