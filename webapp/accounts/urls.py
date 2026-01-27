from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Web views
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # API endpoints
    path('api/login/', api_views.LoginAPIView.as_view(), name='api_login'),
    path('api/logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),
    path('api/user/<int:user_id>/', api_views.UserDetailAPIView.as_view(), name='api_user_detail'),
    path('api/attendance/', api_views.attendance_list, name='api_attendance_list'),
    path('api/attendance/mark/', api_views.mark_attendance, name='api_mark_attendance'),
]
