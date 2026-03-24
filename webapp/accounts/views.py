from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
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
        
        # If user is staff but no assigned role, send to admin
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
            
        # If we reach here, user is logged in but has no valid role
        # logout to break the loop and show message
        auth_logout(request)
        messages.error(request, 'Your account does not have an assigned role. Please contact the administrator.')
        return redirect('login')

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
    user = request.user
    student = user.student_profile

    today = timezone.now().date()

    # All today's sessions for student's course
    todays_sessions = ClassSchedule.objects.filter(
        subject__course=student.course,
        session_date=today
    ).select_related('subject', 'taught_by')

    # Attendance records the student already has for today
    todays_attendance = {
        str(a.session_id): a
        for a in Attendance.objects.filter(student=student, session__in=todays_sessions)
    }

    # Annotate each session and split by attendance state/time window.
    available_classes = []   # sessions student can still mark now
    closed_unmarked = []     # sessions student missed marking (time window closed)
    marked_today = []        # sessions already marked (with status + verification)
    now_time = timezone.localtime().time()
    for cls in todays_sessions:
        att = todays_attendance.get(str(cls.id))
        if att:
            cls.my_attendance = att
            marked_today.append(cls)
        else:
            if now_time <= cls.end_time:
                available_classes.append(cls)
            else:
                closed_unmarked.append(cls)

    # Get current semester subjects for the student
    current_semester_obj = Semester.objects.filter(
        course=student.course,
        semester_no=student.current_semester
    ).first()

    semester_subjects = list(
        Subject.objects.filter(
            course=student.course,
            semester=current_semester_obj
        ).select_related('course', 'semester').order_by('subject_name')
    ) if current_semester_obj else []

    # Calculate per-subject attendance stats
    for subject in semester_subjects:
        total_classes = ClassSchedule.objects.filter(subject=subject).count()
        present_count = Attendance.objects.filter(
            student=student,
            session__subject=subject,
            status='present'
        ).count()
        absent_count = Attendance.objects.filter(
            student=student,
            session__subject=subject,
            status='absent'
        ).count()
        late_count = Attendance.objects.filter(
            student=student,
            session__subject=subject,
            status='late'
        ).count()
        attended = Attendance.objects.filter(
            student=student,
            session__subject=subject
        ).count()

        # Keep dashboard consistent with subject detail: sessions without a
        # student record are treated as absent.
        missing_count = max(total_classes - (present_count + absent_count + late_count), 0)
        absent_direct_count = absent_count + missing_count

        absent_from_late = late_count // 4
        effective_absent_count = absent_direct_count + absent_from_late
        effective_present_count = max(total_classes - effective_absent_count, 0)

        subject.total_classes = total_classes
        subject.present_count = present_count
        subject.absent_count = effective_absent_count
        subject.absent_direct_count = absent_direct_count
        subject.late_count = late_count
        subject.absent_from_late = absent_from_late
        subject.effective_present_count = effective_present_count
        subject.attended_count = attended
        subject.attendance_pct = round((effective_present_count / total_classes) * 100, 1) if total_classes > 0 else 0

    # Overall stats across all subjects
    total_classes_all = sum(s.total_classes for s in semester_subjects)
    total_present_all = sum(s.effective_present_count for s in semester_subjects)
    overall_pct = round((total_present_all / total_classes_all) * 100, 1) if total_classes_all > 0 else 0
    subjects_at_risk = sum(1 for s in semester_subjects if s.attendance_pct < 70 and s.total_classes > 0)

    context = {
        'user': user,
        'student': student,
        'current_semester_obj': current_semester_obj,
        'semester_subjects': semester_subjects,
        'overall_pct': overall_pct,
        'total_classes_all': total_classes_all,
        'total_present_all': total_present_all,
        'subjects_at_risk': subjects_at_risk,
        'available_classes': available_classes,
        'closed_unmarked': closed_unmarked,
        'marked_today': marked_today,
        'today': today,
        'page_title': 'Student Dashboard'
    }
    return render(request, 'students/dashboard.html', context)


@login_required
@user_passes_test(role_check('student'), login_url='login')
def student_subject_attendance(request, subject_id):
    """View showing a student's attendance detail for a specific subject"""
    user = request.user
    student = user.student_profile
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Get all class sessions for this subject, ordered by date
    sessions = list(ClassSchedule.objects.filter(
        subject=subject
    ).select_related('taught_by').order_by('-session_date', '-start_time'))
    
    # Get attendance records for this student + subject
    attendance_map = {}
    for att in Attendance.objects.filter(student=student, session__subject=subject):
        attendance_map[str(att.session_id)] = att.status
    
    # Attach status to each session
    for session in sessions:
        session.student_status = attendance_map.get(str(session.id), 'absent')
    
    # Stats
    total_classes = len(sessions)
    present_count = sum(1 for s in sessions if s.student_status == 'present')
    absent_count = sum(1 for s in sessions if s.student_status == 'absent')
    late_count = sum(1 for s in sessions if s.student_status == 'late')
    absent_from_late = late_count // 4
    effective_absent_count = absent_count + absent_from_late
    effective_present_count = max(total_classes - effective_absent_count, 0)
    attendance_pct = round((effective_present_count / total_classes) * 100, 1) if total_classes > 0 else 0
    
    context = {
        'subject': subject,
        'sessions': sessions,
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': effective_absent_count,
        'absent_direct_count': absent_count,
        'late_count': late_count,
        'absent_from_late': absent_from_late,
        'attendance_pct': attendance_pct,
        'page_title': f'Attendance: {subject.subject_name}'
    }
    return render(request, 'students/subject_attendance.html', context)


@login_required
@user_passes_test(role_check('teacher'), login_url='login')
def teacher_dashboard(request):
    """Teacher dashboard view"""
    user = request.user
    
    # Get subjects taught by this teacher with related course and semester
    subjects_taught = Subject.objects.filter(
        teacher_assignments__teacher=user
    ).select_related('course', 'semester').order_by(
        'course__course_name', 'semester__semester_no', 'subject_name'
    ).distinct()
    
    # Pre-group subjects by course -> semester for the template
    from collections import OrderedDict
    grouped_subjects = OrderedDict()
    for subject in subjects_taught:
        course_name = subject.course.course_name if subject.course else 'No Course'
        semester_no = subject.semester.semester_no if subject.semester else 0
        
        if course_name not in grouped_subjects:
            grouped_subjects[course_name] = OrderedDict()
        if semester_no not in grouped_subjects[course_name]:
            grouped_subjects[course_name][semester_no] = []
        grouped_subjects[course_name][semester_no].append(subject)
    
    # Get recent and upcoming classes (last 3 days + future)
    three_days_ago = timezone.now().date() - timezone.timedelta(days=3)
    recent_and_upcoming = ClassSchedule.objects.filter(
        taught_by=user,
        session_date__gte=three_days_ago
    ).order_by('-session_date', 'start_time')[:15]
    
    # Annotate each class with pending count
    for cls in recent_and_upcoming:
        cls.pending_count = Attendance.objects.filter(
            session=cls,
            verification_status='pending'
        ).count()

    context = {
        'user': user,
        'subjects_taught': subjects_taught,
        'grouped_subjects': grouped_subjects,
        'upcoming_classes': recent_and_upcoming,
        'page_title': 'Teacher Dashboard'
    }
    return render(request, 'teachers/dashboard.html', context)


@login_required
@user_passes_test(role_check('admin'), login_url='login')
def admin_dashboard(request):
    """Admin dashboard view with statistics and class schedule"""
    user = request.user
    
    # Get statistics
    total_users = User.objects.count()
    total_students = Student.objects.count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_courses = Course.objects.count()
    
    # Chart JS Data Aggregation with Filters
    import json
    from django.shortcuts import get_object_or_404
    
    course_chart_id = request.GET.get('course_chart')
    semester_chart_id = request.GET.get('semester_chart')
    subject_chart_id = request.GET.get('subject_chart')
    
    chart_labels = []
    attendance_data = []
    chart_title = "Overall Attendance by Semester"
    chart_type = 'bar'
    
    if subject_chart_id:
        subject = get_object_or_404(Subject, id=subject_chart_id)
        chart_title = f"Attendance for {subject.subject_name}"
        chart_type = 'doughnut'
        total_present = Attendance.objects.filter(session__subject=subject, status='present').count()
        total_absent = Attendance.objects.filter(session__subject=subject, status='absent').count()
        total_late = Attendance.objects.filter(session__subject=subject, status='late').count()
        chart_labels = ['Present', 'Absent', 'Late']
        attendance_data = [total_present, total_absent, total_late]
        
    elif semester_chart_id:
        semester = get_object_or_404(Semester, id=semester_chart_id)
        chart_title = f"Attendance by Subject ({semester.course.course_name} - Sem {semester.semester_no})"
        subjects = Subject.objects.filter(semester=semester)
        for sub in subjects:
            chart_labels.append(sub.subject_name)
            total_records = Attendance.objects.filter(session__subject=sub).count()
            present_records = Attendance.objects.filter(session__subject=sub, status='present').count()
            pct = round((present_records / total_records) * 100, 1) if total_records > 0 else 0
            attendance_data.append(pct)
            
    elif course_chart_id:
        course = get_object_or_404(Course, id=course_chart_id)
        chart_title = f"Attendance by Semester ({course.course_name})"
        semesters = Semester.objects.filter(course=course).order_by('semester_no')
        for sem in semesters:
            chart_labels.append(f"Sem {sem.semester_no}")
            total_records = Attendance.objects.filter(session__subject__semester=sem).count()
            present_records = Attendance.objects.filter(session__subject__semester=sem, status='present').count()
            pct = round((present_records / total_records) * 100, 1) if total_records > 0 else 0
            attendance_data.append(pct)
            
    else:
        semesters = Semester.objects.all().select_related('course')
        for sem in semesters:
            label_str = f"{sem.course.course_name[:15]} - Sem {sem.semester_no}"
            chart_labels.append(label_str)
            total_records = Attendance.objects.filter(session__subject__semester=sem).count()
            present_records = Attendance.objects.filter(session__subject__semester=sem, status='present').count()
            pct = round((present_records / total_records) * 100, 1) if total_records > 0 else 0
            attendance_data.append(pct)

    # For the dropdown filters
    filter_courses = Course.objects.all()
    filter_semesters = Semester.objects.all()
    if course_chart_id:
        filter_semesters = filter_semesters.filter(course_id=course_chart_id)
    filter_subjects = Subject.objects.all()
    if semester_chart_id:
        filter_subjects = filter_subjects.filter(semester_id=semester_chart_id)
    elif course_chart_id:
        filter_subjects = filter_subjects.filter(course_id=course_chart_id)

    # Remove recent_attendance context and add chart data
    recent_attendance = None

    # Class Schedule Logic
    today = timezone.now().date()
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    yesterday = today - timezone.timedelta(days=1)
    tomorrow = today + timezone.timedelta(days=1)

    # Fetch classes for specific dates
    classes_today = ClassSchedule.objects.filter(session_date=today).select_related('subject', 'taught_by')
    classes_yesterday = ClassSchedule.objects.filter(session_date=yesterday).select_related('subject', 'taught_by')
    classes_tomorrow = ClassSchedule.objects.filter(session_date=tomorrow).select_related('subject', 'taught_by')
    
    # Classes for selected date (if not one of the quick dates)
    classes_selected = None
    if selected_date not in [today, yesterday, tomorrow]:
        classes_selected = ClassSchedule.objects.filter(session_date=selected_date).select_related('subject', 'taught_by')

    context = {
        'user': user,
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'semester_labels_json': json.dumps(chart_labels),
        'attendance_data_json': json.dumps(attendance_data),
        'chart_height': max(350, len(chart_labels) * 40),
        'chart_title': chart_title,
        'chart_type': chart_type,
        'filter_courses': filter_courses,
        'filter_semesters': filter_semesters,
        'filter_subjects': filter_subjects,
        'classes_today': classes_today,
        'classes_yesterday': classes_yesterday,
        'classes_tomorrow': classes_tomorrow,
        'classes_selected': classes_selected,
        'selected_date': selected_date,
        'today': today,
        'yesterday': yesterday,
        'tomorrow': tomorrow,
        'page_title': 'Admin Dashboard'
    }
    return render(request, 'admin/dashboard.html', context)
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
def student_edit(request, user_id):
    """View to edit a student's course, semester, and enrollment year"""
    user_obj = get_object_or_404(User, id=user_id, role='student')
    student = get_object_or_404(Student, user=user_obj)
    
    if request.method == 'POST':
        course_id = request.POST.get('course')
        current_semester = request.POST.get('current_semester')
        enrollment_year = request.POST.get('enrollment_year')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        
        if course_id and current_semester and enrollment_year:
            try:
                course = get_object_or_404(Course, id=course_id)
                student.course = course
                student.current_semester = int(current_semester)
                student.enrollment_year = int(enrollment_year)
                student.updated_by = request.user
                student.save()
                
                if firstname:
                    user_obj.firstname = firstname
                if lastname:
                    user_obj.lastname = lastname
                user_obj.save()
                
                messages.success(request, f'Student {user_obj.firstname} {user_obj.lastname} updated successfully.')
                return redirect('user_list')
            except Exception as e:
                messages.error(request, f'Error updating student: {str(e)}')
        else:
            messages.error(request, 'Course, semester, and enrollment year are required.')
    
    courses = Course.objects.all()
    # Get semesters for current course
    semesters = Semester.objects.filter(course=student.course).order_by('semester_no') if student.course else []
    
    context = {
        'user_obj': user_obj,
        'student': student,
        'courses': courses,
        'semesters': semesters,
        'page_title': f'Edit Student: {user_obj.firstname} {user_obj.lastname}'
    }
    return render(request, 'admin/student_edit.html', context)


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
            course = Course.objects.create(course_name=name)
            messages.success(request, f'Course {name} created successfully.')
            return redirect('course_semesters', course_id=course.id)
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
def course_semesters(request, course_id):
    """View to list all semesters for a specific course"""
    course = get_object_or_404(Course, id=course_id)
    semesters = Semester.objects.filter(course=course).prefetch_related('subjects')
    
    context = {
        'course': course,
        'semesters': semesters,
        'page_title': f'Semesters for {course.course_name}'
    }
    return render(request, 'admin/semester_list.html', context)


@login_required
@user_passes_test(role_check('admin'), login_url='login')
@login_required
@user_passes_test(role_check('admin'), login_url='login')
def semester_create(request, course_id):
    """View to create a new semester for a course"""
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        semester_no = request.POST.get('semester_no')
        if semester_no and semester_no.isdigit():
            sem, created = Semester.objects.get_or_create(
                course=course,
                semester_no=int(semester_no)
            )
            if created:
                messages.success(request, f'Semester {semester_no} added to {course.course_name}.')
            else:
                messages.warning(request, f'Semester {semester_no} already exists for this course.')
            return redirect('course_semesters', course_id=course.id)
        messages.error(request, 'A valid semester number is required.')
    
    return render(request, 'admin/semester_form.html', {
        'page_title': f'Add Semester to {course.course_name}',
        'course': course
    })


def subject_list(request):
    """View to list all subjects"""
    course_filter = request.GET.get('course')
    semester_filter = request.GET.get('semester')
    
    subjects = Subject.objects.all().select_related('course', 'semester')
    
    if course_filter:
        subjects = subjects.filter(course_id=course_filter)
    if semester_filter:
        subjects = subjects.filter(semester_id=semester_filter)
        
    # Get teacher assignments for these subjects
    for subject in subjects:
        assignments = TeacherSubject.objects.filter(subject=subject).select_related('teacher')
        subject.assigned_teachers = [a.teacher for a in assignments]
        
    courses = Course.objects.all()
    selected_semester = None
    if semester_filter:
        selected_semester = Semester.objects.filter(id=semester_filter).first()
        
    context = {
        'subjects': subjects,
        'courses': courses,
        'course_filter': course_filter,
        'semester_filter': semester_filter,
        'selected_semester': selected_semester,
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
        semester_id = request.POST.get('semester')
        teacher_id = request.POST.get('teacher')
        
        if code and name and course_id and semester_id:
            try:
                course = get_object_or_404(Course, id=course_id)
                semester = get_object_or_404(Semester, id=semester_id, course=course)
                subject = Subject.objects.create(
                    subject_code=code,
                    subject_name=name,
                    course=course,
                    semester=semester
                )
                
                if teacher_id:
                    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
                    TeacherSubject.objects.create(subject=subject, teacher=teacher)
                    
                messages.success(request, f'Subject {name} created successfully.')
                return redirect('subject_list')
            except Exception as e:
                messages.error(request, f'Error creating subject: {str(e)}')
        else:
            messages.error(request, 'Subject code, name, course, and semester are required.')
            
    # Pre-select semester if passed in GET
    initial_semester_id = request.GET.get('semester')
    initial_semester = None
    if initial_semester_id:
        initial_semester = Semester.objects.filter(id=initial_semester_id).first()

    courses = Course.objects.all()
    semesters = Semester.objects.all()
    teachers = User.objects.filter(role='teacher')
    return render(request, 'admin/subject_form.html', {
        'page_title': 'Create Subject',
        'courses': courses,
        'semesters': semesters,
        'teachers': teachers,
        'initial_semester': initial_semester
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
        semester_id = request.POST.get('semester')
        teacher_id = request.POST.get('teacher')
        
        if code and name and course_id and semester_id:
            try:
                course = get_object_or_404(Course, id=course_id)
                semester = get_object_or_404(Semester, id=semester_id, course=course)
                subject.subject_code = code
                subject.subject_name = name
                subject.course = course
                subject.semester = semester
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
            messages.error(request, 'Subject code, name, course, and semester are required.')
            
    courses = Course.objects.all()
    semesters = Semester.objects.all()
    teachers = User.objects.filter(role='teacher')
    
    # Get current teacher assignment
    current_assignment = TeacherSubject.objects.filter(subject=subject).first()
    assigned_teacher_id = current_assignment.teacher.id if current_assignment else None
    
    return render(request, 'admin/subject_form.html', {
        'page_title': 'Edit Subject',
        'subject': subject,
        'courses': courses,
        'semesters': semesters,
        'teachers': teachers,
        'assigned_teacher_id': assigned_teacher_id
    })
@login_required
@user_passes_test(role_check('admin'), login_url='login')
def attendance_history(request):
    """View for full attendance history"""
    subject_filter = request.GET.get('subject')
    attendance_records = Attendance.objects.all().select_related(
        'student__user', 'session__subject', 'session__taught_by'
    )
    
    selected_subject = None
    if subject_filter:
        attendance_records = attendance_records.filter(session__subject_id=subject_filter)
        selected_subject = Subject.objects.filter(id=subject_filter).first()
        
    attendance_records = attendance_records.order_by('-marked_at')
    
    page_title = 'Attendance History'
    if selected_subject:
        page_title = f'Attendance History: {selected_subject.subject_name}'
    
    context = {
        'attendance_records': attendance_records,
        'subject_filter': subject_filter,
        'selected_subject': selected_subject,
        'page_title': page_title
    }
    return render(request, 'admin/attendance_history.html', context)


@login_required
def semesters_api(request):
    """Simple JSON API to return semesters for a given course"""
    course_id = request.GET.get('course')
    if not course_id:
        return JsonResponse([], safe=False)
    semesters = Semester.objects.filter(course_id=course_id).order_by('semester_no')
    data = [{'id': str(s.id), 'semester_no': s.semester_no} for s in semesters]
    return JsonResponse(data, safe=False)
