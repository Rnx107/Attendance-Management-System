from django.shortcuts import render, get_object_or_404, redirect, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Subject, Student

def teacher_check(user):
    return user.is_authenticated and (user.role == 'teacher' or user.is_superuser)

@login_required
@user_passes_test(teacher_check, login_url='login')
def teacher_view_students(request, subject_id):
    """View to list all students for a given subject."""
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Check if the requesting teacher is assigned to this subject
    if not subject.teacher_assignments.filter(teacher=request.user).exists():
        messages.error(request, "You are not authorized to view students for this subject.")
        return redirect('teacher_dashboard')
        
    students = Student.objects.filter(
        course=subject.semester.course,
        current_semester=subject.semester.semester_no
    ).select_related('user').order_by('user__lastname', 'user__firstname')
    
    context = {
        'subject': subject,
        'students': students,
        'page_title': f'Students in {subject.subject_name}'
    }
    return render(request, 'teachers/student_list.html', context)