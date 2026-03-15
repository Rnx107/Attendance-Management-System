from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Web views
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/student/subject/<uuid:subject_id>/', views.student_subject_attendance, name='student_subject_attendance'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Custom Admin Management
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/create/', views.user_create, name='user_create'),
    path('admin/users/delete/<uuid:user_id>/', views.user_delete, name='user_delete'),
    path('admin/students/edit/<uuid:user_id>/', views.student_edit, name='student_edit'),
    path('admin/courses/', views.course_list, name='course_list'),
    path('admin/courses/<uuid:course_id>/semesters/', views.course_semesters, name='course_semesters'),
    path('admin/courses/<uuid:course_id>/semesters/create/', views.semester_create, name='semester_create'),
    path('admin/courses/create/', views.course_create, name='course_create'),
    path('admin/courses/edit/<uuid:course_id>/', views.course_edit, name='course_edit'),
    path('admin/subjects/', views.subject_list, name='subject_list'),
    path('admin/subjects/create/', views.subject_create, name='subject_create'),
    path('admin/subjects/edit/<uuid:subject_id>/', views.subject_edit, name='subject_edit'),
    path('admin/attendance/history/', views.attendance_history, name='attendance_history'),
    path('api/semesters/', views.semesters_api, name='semesters_api'),
    
    # API endpoints
    path('api/login/', api_views.LoginAPIView.as_view(), name='api_login'),
    path('api/logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),
    path('api/user/<int:user_id>/', api_views.UserDetailAPIView.as_view(), name='api_user_detail'),
    path('api/attendance/', api_views.attendance_list, name='api_attendance_list'),
    path('api/attendance/mark/', api_views.mark_attendance, name='api_mark_attendance'),
]
