from django.urls import path
from . import views

urlpatterns = [
    path('mark/<uuid:session_id>/', views.mark_attendance, name='mark_attendance'),
    path('student/mark/<uuid:session_id>/', views.student_mark_attendance, name='student_mark_attendance'),
    path('verify/<uuid:session_id>/', views.teacher_verify_attendance, name='teacher_verify_attendance'),
    path('session/create/', views.create_session, name='create_session'),
]
