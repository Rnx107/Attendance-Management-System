from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
import openpyxl
from core.models import User, Student, ClassSchedule, Attendance, Subject
from django.utils import timezone

def student_check(user):
    return user.is_authenticated and (user.role == 'student')

def teacher_check(user):
    return user.is_authenticated and (user.role == 'teacher' or user.is_superuser)

def admin_check(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

@login_required
@user_passes_test(student_check, login_url='login')
def student_mark_attendance(request, session_id):
    """Student marks their own attendance"""
    session = get_object_or_404(ClassSchedule, id=session_id)
    student = request.user.student_profile
    
    # Check if session is for student's course
    if session.subject.course != student.course:
        messages.error(request, "You are not enrolled in this subject's course.")
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
        course=session.subject.course
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
        course=session.subject.course
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
    
    if request.user.role == 'admin' or request.user.is_superuser:
        subjects_taught = Subject.objects.select_related('course', 'semester').all()
    else:
        subjects_taught = Subject.objects.filter(
            teacher_assignments__teacher=request.user
        ).select_related('course', 'semester').distinct()
        
    courses = list(set([s.course for s in subjects_taught if s.course]))
    courses.sort(key=lambda c: c.course_name)
    
    semesters = list(set([s.semester for s in subjects_taught if s.semester]))
    semesters.sort(key=lambda s: (s.course_id, s.semester_no))
    
    context = {
        'subjects': subjects_taught,
        'courses': courses,
        'semesters': semesters,
        'today': timezone.now().date().isoformat(),
        'page_title': 'Create New Session'
    }
    return render(request, 'attendance/create_session.html', context)


@login_required
@user_passes_test(admin_check, login_url='login')
def admin_session_attendance(request, session_id):
    """Admin view to see and manage attendance for a specific session"""
    session = get_object_or_404(ClassSchedule, id=session_id)
    
    # Get all students in the course associated with this subject
    students = Student.objects.filter(
        course=session.subject.course
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
        messages.success(request, f"Attendance for {session.subject.subject_name} updated successfully.")
        return redirect('admin_dashboard')
    
    student_list = []
    for s in students:
        s.current_status = attendance_map.get(str(s.id), 'present')
        student_list.append(s)
    
    context = {
        'session': session,
        'students': student_list,
        'page_title': 'Session Attendance - Admin'
    }
    return render(request, 'admin/session_attendance.html', context)


@login_required
def export_subject_attendance_excel(request, subject_id):
    """Export attendance for a subject to an Excel file."""
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Permission check: admin or assigned teacher
    if request.user.role != 'admin' and not request.user.is_superuser:
        if not subject.teacher_assignments.filter(teacher=request.user).exists():
            messages.error(request, "You are not authorized to export attendance for this subject.")
            return redirect('teacher_dashboard')

    # Get all students for this course
    students = Student.objects.filter(
        course=subject.course
    ).select_related('user').order_by('user__lastname', 'user__firstname')
    
    # Get all sessions for this subject
    sessions = ClassSchedule.objects.filter(
        subject=subject
    ).order_by('session_date', 'start_time')
    
    # Get attendance data
    attendances = Attendance.objects.filter(session__subject=subject)
    
    # Build a quick lookup dictionary: (student_id, session_id) -> status
    att_map = {}
    for att in attendances:
        att_map[(att.student_id, att.session_id)] = att.status

    # Create the Excel workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Attendance - {subject.subject_code}"
    
    # Header row
    headers = ["Student Name", "Email"]
    for s in sessions:
        headers.append(s.session_date.strftime("%b %d") + " " + s.start_time.strftime("%H:%M"))
    headers.extend(["Total Present", "Total Absent", "Total Late"])
    ws.append(headers)
    
    # Student rows
    for student in students:
        row = [f"{student.user.firstname} {student.user.lastname}", student.user.email]
        
        present = 0
        absent = 0
        late = 0
        
        for s in sessions:
            status = att_map.get((student.id, s.id), 'N/A')
            row.append(status.title() if status != 'N/A' else '-')
            
            if status == 'present':
                present += 1
            elif status == 'absent':
                absent += 1
            elif status == 'late':
                late += 1
                
        row.extend([present, absent, late])
        ws.append(row)
        
    # Auto-adjust column widths
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # Prepare response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Attendance_{subject.subject_code}.xlsx"'
    wb.save(response)
    
    return response
