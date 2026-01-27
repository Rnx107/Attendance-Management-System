from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# ViewSets are not yet implemented in core.views
# TODO: Implement the following ViewSets:
# - UserViewSet
# - CourseViewSet
# - SemesterViewSet
# - SubjectViewSet
# - StudentViewSet
# - TeacherSubjectViewSet
# - ClassScheduleViewSet
# - AttendanceViewSet

urlpatterns = [
    # JWT Authentication endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # TODO: Add API routes once ViewSets are implemented in core.views
]