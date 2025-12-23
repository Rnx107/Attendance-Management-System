from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet, CourseViewSet, SemesterViewSet, SubjectViewSet,
    StudentViewSet, TeacherSubjectViewSet, ClassScheduleViewSet, AttendanceViewSet
)
from .auth_views import firebase_login, firebase_logout, verify_session, refresh_token

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
    # Firebase Authentication endpoints
    path('auth/firebase-login/', firebase_login, name='firebase_login'),
    path('auth/firebase-logout/', firebase_logout, name='firebase_logout'),
    path('auth/verify-session/', verify_session, name='verify_session'),
    path('auth/refresh-token/', refresh_token, name='refresh_token'),
    
    # JWT Authentication endpoints (for backward compatibility)
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API routes
    path('', include(router.urls)),
]