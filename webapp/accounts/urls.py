from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/student/subject/<uuid:subject_id>/', views.student_subject_attendance, name='student_subject_attendance'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # Admin — User management
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/create/', views.user_create, name='user_create'),
    path('admin/users/delete/<uuid:user_id>/', views.user_delete, name='user_delete'),
    path('admin/students/edit/<uuid:user_id>/', views.student_edit, name='student_edit'),

    # Admin — Course / Semester / Subject management
    path('admin/courses/', views.course_list, name='course_list'),
    path('admin/courses/create/', views.course_create, name='course_create'),
    path('admin/courses/edit/<uuid:course_id>/', views.course_edit, name='course_edit'),
    path('admin/courses/<uuid:course_id>/semesters/', views.course_semesters, name='course_semesters'),
    path('admin/courses/<uuid:course_id>/semesters/create/', views.semester_create, name='semester_create'),
    path('admin/subjects/', views.subject_list, name='subject_list'),
    path('admin/subjects/create/', views.subject_create, name='subject_create'),
    path('admin/subjects/edit/<uuid:subject_id>/', views.subject_edit, name='subject_edit'),

    # Admin — Attendance history
    path('admin/attendance/history/', views.attendance_history, name='attendance_history'),

    # Utility JSON
    path('api/semesters/', views.semesters_api, name='semesters_api'),
]
