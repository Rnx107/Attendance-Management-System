from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from core.models import User, Student, TeacherSubject, ClassSchedule, Attendance, Subject, Course
from django.db.models import Count, Q
from django.utils import timezone


@require_http_methods(["GET", "POST"])
@csrf_protect
def login_view(request):
    """Handle user login with email and password"""
    if request.user.is_authenticated:
        # Role-based redirect if already logged in
        if request.user.role == 'student':
            return redirect('student_dashboard')
        elif request.user.role == 'teacher':
            return redirect('teacher_dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('admin_dashboard') if request.user.is_staff else redirect('/')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'accounts/login.html')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                # Role-based redirect
                if user.role == 'student':
                    return redirect('student_dashboard')
                elif user.role == 'teacher':
                    return redirect('teacher_dashboard')
                elif user.role == 'admin' or user.is_staff:
                    return redirect('admin_dashboard')
                else:
                    return redirect('login')
            else:
                messages.error(request, 'This account is inactive.')
        else:
            messages.error(request, 'Invalid email or password.')
        
        return render(request, 'accounts/login.html')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """Handle user logout"""
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def role_check(role):
    def check(user):
        return user.is_authenticated and (user.role == role or user.is_superuser)
    return check


@login_required
@user_passes_test(role_check('student'), login_url='login')
def student_dashboard(request):
    """Student dashboard view"""
    try:
        user = request.user
        student = user.student_profile
        
        # Get attendance records
        attendance_records = Attendance.objects.filter(
            student=student
        ).select_related('session__subject', 'session__taught_by').order_by('-session__session_date')[:10]
        
        # Get available classes for today that match student's course and semester
        today = timezone.now().date()
        available_classes = ClassSchedule.objects.filter(
            subject__semester__course=student.course,
            subject__semester__semester_no=student.current_semester,
            session_date=today
        ).select_related('subject', 'taught_by')
        
        # Mark classes student has already marked
        marked_sessions = Attendance.objects.filter(
            student=student,
            session__in=available_classes
        ).values_list('session_id', flat=True)
        
        for cls in available_classes:
            cls.already_marked = cls.id in marked_sessions

        context = {
            'user': user,
            'student': student,
            'attendance_records': attendance_records,
            'available_classes': available_classes,
            'page_title': 'Student Dashboard'
        }
        return render(request, 'students/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('login')


@login_required
@user_passes_test(role_check('teacher'), login_url='login')
def teacher_dashboard(request):
    """Teacher dashboard view"""
    try:
        user = request.user
        
        # Get subjects taught by this teacher
        subjects_taught = Subject.objects.filter(
            teacher_assignments__teacher=user
        ).distinct()
        
        # Get upcoming classes
        upcoming_classes = ClassSchedule.objects.filter(
            taught_by=user,
            session_date__gte=timezone.now().date()
        ).order_by('session_date', 'start_time')[:10]
        
        context = {
            'user': user,
            'subjects_taught': subjects_taught,
            'upcoming_classes': upcoming_classes,
            'page_title': 'Teacher Dashboard'
        }
        return render(request, 'teachers/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('login')


@login_required
@user_passes_test(role_check('admin'), login_url='login')
def admin_dashboard(request):
    """Admin dashboard view"""
    try:
        user = request.user
        
        # Get statistics
        total_users = User.objects.count()
        total_students = Student.objects.count()
        total_teachers = User.objects.filter(role='teacher').count()
        total_courses = Course.objects.count()
        
        # Recent attendance records
        recent_attendance = Attendance.objects.all().select_related(
            'student__user', 'session__subject', 'session__taught_by'
        ).order_by('-marked_at')[:10]
        
        context = {
            'user': user,
            'total_users': total_users,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_courses': total_courses,
            'recent_attendance': recent_attendance,
            'page_title': 'Admin Dashboard'
        }
        return render(request, 'admin/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('login')
