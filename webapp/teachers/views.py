from django.shortcuts import render, get_object_or_404, redirect, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Subject, Student, ClassSchedule, Attendance

def teacher_check(user):
    return user.is_authenticated and (user.role == 'teacher' or user.role == 'admin' or user.is_superuser)

@login_required
@user_passes_test(teacher_check, login_url='login')
def teacher_view_students(request, subject_id):
    """View to list all students for a given subject."""
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Check if the requesting teacher is assigned to this subject (admins bypass this)
    if request.user.role != 'admin' and not subject.teacher_assignments.filter(teacher=request.user).exists():
        messages.error(request, "You are not authorized to view students for this subject.")
        return redirect('teacher_dashboard')
        
    students = Student.objects.filter(
        course=subject.course
    ).select_related('user').order_by('user__lastname', 'user__firstname')
    
    # Get recent class sessions (last 5)
    recent_sessions = list(ClassSchedule.objects.filter(
        subject=subject
    ).order_by('-session_date', '-start_time')[:5])
    recent_sessions.reverse() # Oldest to newest
    
    # For each student, get their attendance for these sessions
    for student in students:
        history = []
        for session in recent_sessions:
            att = Attendance.objects.filter(student=student, session=session).first()
            history.append(att.status if att else 'N/A')
        student.attendance_history = zip(recent_sessions, history)
    
    context = {
        'subject': subject,
        'students': students,
        'recent_sessions': recent_sessions,
        'page_title': f'Students in {subject.subject_name}'
    }
    return render(request, 'teachers/student_list.html', context)