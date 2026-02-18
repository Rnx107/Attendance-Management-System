from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import User, Student, ClassSchedule, Attendance, Subject, Semester
from django.utils import timezone

def student_check(user):
    return user.is_authenticated and (user.role == 'student')

def teacher_check(user):
    return user.is_authenticated and (user.role == 'teacher' or user.is_superuser)

@login_required
@user_passes_test(student_check, login_url='login')
def student_mark_attendance(request, session_id):
    """Student marks their own attendance"""
    session = get_object_or_404(ClassSchedule, id=session_id)
    student = request.user.student_profile
    
    # Check if session is for student's course and semester
    if session.subject.semester.course != student.course or \
       session.subject.semester.semester_no != student.current_semester:
        messages.error(request, "You are not enrolled in this subject's semester.")
        return redirect('student_dashboard')
    
    # Check if session is today
    if session.session_date != timezone.now().date():
        messages.error(request, "Attendance can only be marked on the day of the class.")
        return redirect('student_dashboard')
        
    # Check if already marked
    if Attendance.objects.filter(session=session, student=student).exists():
        messages.info(request, "You have already marked attendance for this session.")
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        Attendance.objects.create(
            session=session,
            student=student,
            status='present',
            verification_status='pending',
            marked_by=request.user,
            marked_at=timezone.now()
        )
        messages.success(request, f"Attendance for {session.subject.subject_name} marked successfully. Awaiting teacher verification.")
        return redirect('student_dashboard')
        
    context = {
        'session': session,
        'page_title': 'Confirm Attendance'
    }
    return render(request, 'attendance/student_confirm.html', context)

@login_required
@user_passes_test(teacher_check, login_url='login')
def mark_attendance(request, session_id):
    """View to mark attendance for a specific class session (Teacher Direct)"""
    session = get_object_or_404(ClassSchedule, id=session_id)
    
    if request.user.role == 'teacher' and session.taught_by != request.user:
        messages.error(request, "You are not authorized to mark attendance for this session.")
        return redirect('teacher_dashboard')

    students = Student.objects.filter(
        course=session.subject.semester.course,
        current_semester=session.subject.semester.semester_no
    ).select_related('user').order_by('user__lastname', 'user__firstname')
    
    existing_attendance = Attendance.objects.filter(session=session)
    attendance_map = {str(a.student_id): a.status for a in existing_attendance}
    
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status:
                Attendance.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={
                        'status': status,
                        'verification_status': 'verified',
                        'marked_by': request.user,
                        'marked_at': timezone.now(),
                        'verified_by': request.user,
                        'verified_at': timezone.now()
                    }
                )
        messages.success(request, f"Attendance for {session.subject.subject_name} marked and verified successfully.")
        return redirect('teacher_dashboard')
    
    student_list = []
    for s in students:
        s.current_status = attendance_map.get(str(s.id), 'present')
        student_list.append(s)
    
    context = {
        'session': session,
        'students': student_list,
        'page_title': 'Mark Attendance'
    }
    return render(request, 'attendance/mark.html', context)

@login_required
@user_passes_test(teacher_check, login_url='login')
def teacher_verify_attendance(request, session_id):
    """Teacher verifies students' self-marked attendance"""
    session = get_object_or_404(ClassSchedule, id=session_id)
    
    if request.user.role == 'teacher' and session.taught_by != request.user:
        messages.error(request, "You are not authorized to verify attendance for this session.")
        return redirect('teacher_dashboard')

    students = Student.objects.filter(
        course=session.subject.semester.course,
        current_semester=session.subject.semester.semester_no
    ).select_related('user').order_by('user__lastname', 'user__firstname')
    
    attendance_records = Attendance.objects.filter(session=session).select_related('student__user')
    attendance_map = {str(a.student_id): a for a in attendance_records}
    
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            v_status = request.POST.get(f'verify_{student.id}')
            
            if status:
                Attendance.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={
                        'status': status,
                        'verification_status': v_status if v_status else 'verified',
                        'verified_by': request.user,
                        'verified_at': timezone.now()
                    }
                )
        messages.success(request, f"Attendance for {session.subject.subject_name} verified successfully.")
        return redirect('teacher_dashboard')
    
    student_list = []
    for s in students:
        s.attendance = attendance_map.get(str(s.id))
        student_list.append(s)
        
    context = {
        'session': session,
        'students': student_list,
        'page_title': 'Verify Attendance'
    }
    return render(request, 'attendance/verify.html', context)

@login_required
@user_passes_test(teacher_check, login_url='login')
def create_session(request):
    """View to create a new class session"""
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        session_date = request.POST.get('session_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        if subject_id and session_date and start_time and end_time:
            subject = get_object_or_404(Subject, id=subject_id)
            session = ClassSchedule.objects.create(
                subject=subject,
                session_date=session_date,
                start_time=start_time,
                end_time=end_time,
                taught_by=request.user
            )
            messages.success(request, f"Session for {subject.subject_name} created successfully.")
            return redirect('mark_attendance', session_id=session.id)
        else:
            messages.error(request, "All fields are required.")
    
    subjects_taught = Subject.objects.filter(
        teacher_assignments__teacher=request.user
    ).distinct()
    
    context = {
        'subjects': subjects_taught,
        'today': timezone.now().date().isoformat(),
        'page_title': 'Create New Session'
    }
    return render(request, 'attendance/create_session.html', context)
