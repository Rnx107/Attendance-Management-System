from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from core.models import User, Student, TeacherSubject, ClassSchedule, Attendance, Subject, Course, Semester
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
            subject__course=student.course,
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
        
        # Get recent and upcoming classes (last 3 days + future)
        three_days_ago = timezone.now().date() - timezone.timedelta(days=3)
        recent_and_upcoming = ClassSchedule.objects.filter(
            taught_by=user,
            session_date__gte=three_days_ago
        ).order_by('-session_date', 'start_time')[:15]
        
        context = {
            'user': user,
            'subjects_taught': subjects_taught,
            'upcoming_classes': recent_and_upcoming,
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
@login_required
@user_passes_test(role_check('admin'), login_url='login')
def user_list(request):
    """View to list all users with role filtering"""
    role_filter = request.GET.get('role')
    users = User.objects.all()
    if role_filter:
        users = users.filter(role=role_filter)
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'page_title': 'User Management'
    }
    return render(request, 'admin/user_list.html', context)


@login_required
@user_passes_test(role_check('admin'), login_url='login')
def user_create(request):
    """View to register new users"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        role = request.POST.get('role')
        
        if email and password and firstname and lastname and role:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'User with this email already exists.')
            else:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    firstname=firstname,
                    lastname=lastname,
                    role=role
                )
                
                # If student, create student profile
                if role == 'student':
                    enrollment_year = request.POST.get('enrollment_year')
                    course_id = request.POST.get('course')
                    if enrollment_year and course_id:
                        course = get_object_or_404(Course, id=course_id)
                        Student.objects.create(
                            user=user,
                            course=course,
                            enrollment_year=enrollment_year
                        )
                
                messages.success(request, f'User {email} created successfully.')
                return redirect('user_list')
        else:
            messages.error(request, 'All fields are required.')
            
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Register New User'
    }
    return render(request, 'admin/user_form.html', context)


@login_required
@user_passes_test(role_check('admin'), login_url='login')
def user_delete(request, user_id):
    """View to delete a user"""
    user_to_delete = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        email = user_to_delete.email
        user_to_delete.delete()
        messages.success(request, f'User {email} deleted successfully.')
        return redirect('user_list')
    
    return render(request, 'admin/user_confirm_delete.html', {'user_to_delete': user_to_delete})


@login_required
@user_passes_test(role_check('admin'), login_url='login')
def course_list(request):
    """View to list all courses"""
    courses = Course.objects.all().prefetch_related('semesters')
    context = {
        'courses': courses,
        'page_title': 'Course Management'
    }
    return render(request, 'admin/course_list.html', context)


@login_required
@user_passes_test(role_check('admin'), login_url='login')
def course_create(request):
    """View to create a new course"""
    if request.method == 'POST':
        name = request.POST.get('course_name')
        if name:
            Course.objects.create(course_name=name)
            messages.success(request, f'Course {name} created successfully.')
            return redirect('course_list')
        messages.error(request, 'Course name is required.')
    
    return render(request, 'admin/course_form.html', {'page_title': 'Create Course'})


@login_required
@user_passes_test(role_check('admin'), login_url='login')
def course_edit(request, course_id):
    """View to edit an existing course"""
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        name = request.POST.get('course_name')
        status = request.POST.get('status')
        if name:
            course.course_name = name
            if status in ['active', 'inactive']:
                course.status = status
            course.save()
            messages.success(request, f'Course {name} updated successfully.')
            return redirect('course_list')
        messages.error(request, 'Course name is required.')
    
    return render(request, 'admin/course_form.html', {
        'page_title': 'Edit Course',
        'course': course,
    })

@login_required
@user_passes_test(role_check('admin'), login_url='login')
def subject_list(request):
    """View to list all subjects"""
    course_filter = request.GET.get('course')
    subjects = Subject.objects.all().select_related('course')
    
    if course_filter:
        subjects = subjects.filter(course_id=course_filter)
        
    # Get teacher assignments for these subjects
    for subject in subjects:
        assignments = TeacherSubject.objects.filter(subject=subject).select_related('teacher')
        subject.assigned_teachers = [a.teacher for a in assignments]
        
    courses = Course.objects.all()
    context = {
        'subjects': subjects,
        'courses': courses,
        'course_filter': course_filter,
        'page_title': 'Subject Management'
    }
    return render(request, 'admin/subject_list.html', context)


@login_required
@user_passes_test(role_check('admin'), login_url='login')
def subject_create(request):
    """View to create a new subject and assign a teacher"""
    if request.method == 'POST':
        code = request.POST.get('subject_code')
        name = request.POST.get('subject_name')
        course_id = request.POST.get('course')
        teacher_id = request.POST.get('teacher')
        
        if code and name and course_id:
            try:
                course = get_object_or_404(Course, id=course_id)
                subject = Subject.objects.create(
                    subject_code=code,
                    subject_name=name,
                    course=course
                )
                
                if teacher_id:
                    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
                    TeacherSubject.objects.create(subject=subject, teacher=teacher)
                    
                messages.success(request, f'Subject {name} created successfully.')
                return redirect('subject_list')
            except Exception as e:
                messages.error(request, f'Error creating subject: {str(e)}')
        else:
            messages.error(request, 'Subject code, name, and course are required.')
            
    courses = Course.objects.all()
    teachers = User.objects.filter(role='teacher')
    return render(request, 'admin/subject_form.html', {
        'page_title': 'Create Subject',
        'courses': courses,
        'teachers': teachers
    })


@login_required
@user_passes_test(role_check('admin'), login_url='login')
def subject_edit(request, subject_id):
    """View to edit an existing subject and its teacher assignment"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        code = request.POST.get('subject_code')
        name = request.POST.get('subject_name')
        course_id = request.POST.get('course')
        teacher_id = request.POST.get('teacher')
        
        if code and name and course_id:
            try:
                course = get_object_or_404(Course, id=course_id)
                subject.subject_code = code
                subject.subject_name = name
                subject.course = course
                subject.save()
                
                # Handle teacher assignment
                TeacherSubject.objects.filter(subject=subject).delete()
                if teacher_id:
                    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
                    TeacherSubject.objects.create(subject=subject, teacher=teacher)
                    
                messages.success(request, f'Subject {name} updated successfully.')
                return redirect('subject_list')
            except Exception as e:
                messages.error(request, f'Error updating subject: {str(e)}')
        else:
            messages.error(request, 'Subject code, name, and course are required.')
            
    courses = Course.objects.all()
    teachers = User.objects.filter(role='teacher')
    
    # Get current teacher assignment
    current_assignment = TeacherSubject.objects.filter(subject=subject).first()
    assigned_teacher_id = current_assignment.teacher.id if current_assignment else None
    
    return render(request, 'admin/subject_form.html', {
        'page_title': 'Edit Subject',
        'subject': subject,
        'courses': courses,
        'teachers': teachers,
        'assigned_teacher_id': assigned_teacher_id
    })
@login_required
@user_passes_test(role_check('admin'), login_url='login')
def attendance_history(request):
    """View for full attendance history"""
    attendance_records = Attendance.objects.all().select_related(
        'student__user', 'session__subject', 'session__taught_by'
    ).order_by('-marked_at')
    
    context = {
        'attendance_records': attendance_records,
        'page_title': 'Attendance History'
    }
    return render(request, 'admin/attendance_history.html', context)
