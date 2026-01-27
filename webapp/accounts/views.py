from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.sessions.models import Session
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from core.models import User, Student, TeacherSubject, ClassSchedule, Attendance, Subject
from django.db.models import Count, Q
from django.utils import timezone


@require_http_methods(["GET", "POST"])
@csrf_protect
def login_view(request):
    """Handle user login with email and password"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return render(request, 'accounts/login.html')
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password) and user.is_active:
                # Store user info in session
                request.session['user_id'] = str(user.id)
                request.session['user_email'] = user.email
                request.session['user_role'] = user.role
                request.session['user_name'] = f"{user.firstname} {user.lastname}"
                
                # Role-based redirect
                if user.role == 'student':
                    return redirect('student_dashboard')
                elif user.role == 'teacher':
                    return redirect('teacher_dashboard')
                elif user.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('login')
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
        
        return render(request, 'accounts/login.html')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """Handle user logout"""
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def login_required_decorator(view_func):
    """Decorator to check if user is logged in"""
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(role):
    """Decorator to check if user has specific role"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if 'user_id' not in request.session:
                return redirect('login')
            if request.session.get('user_role') != role:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required_decorator
@role_required('student')
def student_dashboard(request):
    """Student dashboard view"""
    user_id = request.session.get('user_id')
    try:
        user = User.objects.get(id=user_id)
        student = user.student_profile
        
        # Get enrolled subjects
        subjects = Subject.objects.filter(
            semester__course__in=student.user.student_profile.__dict__  # simplified for now
        )
        
        # Get attendance records
        attendance_records = Attendance.objects.filter(
            student=student
        ).select_related('session__subject', 'session__taught_by')[:10]
        
        context = {
            'user': user,
            'student': student,
            'attendance_records': attendance_records,
            'page_title': 'Student Dashboard'
        }
        return render(request, 'students/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('login')


@login_required_decorator
@role_required('teacher')
def teacher_dashboard(request):
    """Teacher dashboard view"""
    user_id = request.session.get('user_id')
    try:
        user = User.objects.get(id=user_id)
        
        # Get subjects taught by this teacher
        subjects_taught = TeacherSubject.objects.filter(
            teacher=user
        ).select_related('subject').values_list('subject', flat=True).distinct()
        
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


@login_required_decorator
@role_required('admin')
def admin_dashboard(request):
    """Admin dashboard view"""
    user_id = request.session.get('user_id')
    try:
        user = User.objects.get(id=user_id)
        
        # Get statistics
        total_users = User.objects.count()
        total_students = User.objects.filter(role='student').count()
        total_teachers = User.objects.filter(role='teacher').count()
        total_admins = User.objects.filter(role='admin').count()
        
        # Recent attendance records
        recent_attendance = Attendance.objects.all().select_related(
            'student__user', 'session__subject', 'session__taught_by'
        ).order_by('-marked_at')[:10]
        
        context = {
            'user': user,
            'total_users': total_users,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_admins': total_admins,
            'recent_attendance': recent_attendance,
            'page_title': 'Admin Dashboard'
        }
        return render(request, 'admin/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('login')
