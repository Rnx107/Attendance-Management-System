from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count

from .models import User, Student, Course, Semester, Subject, TeacherSubject, ClassSchedule, Attendance
from .serializers import (
    UserSerializer, UserCreateSerializer, CourseSerializer, SemesterSerializer,
    SubjectSerializer, SubjectDetailSerializer, StudentSerializer,
    TeacherSubjectSerializer, ClassScheduleSerializer,
    AttendanceSerializer, AttendanceCreateSerializer, BulkAttendanceSerializer,
    StudentAttendanceReportSerializer
)
