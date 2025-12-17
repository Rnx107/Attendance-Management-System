from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet, CourseViewSet, SemesterViewSet, SubjectViewSet,
    StudentViewSet, TeacherSubjectViewSet, ClassScheduleViewSet, AttendanceViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'semesters', SemesterViewSet, basename='semester')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'teacher-subjects', TeacherSubjectViewSet, basename='teacher-subject')
router.register(r'schedules', ClassScheduleViewSet, basename='schedule')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    # JWT Authentication endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API routes
    path('', include(router.urls)),
]