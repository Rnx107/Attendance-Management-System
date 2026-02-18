import os
import django
import uuid
from django.utils import timezone
from datetime import time, date, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
django.setup()

from core.models import User, Student, Course, Semester, Subject, TeacherSubject, ClassSchedule, Attendance

def seed_data():
    print("Seeding data...")
    
    # 1. Create Superuser/Admin
    admin_email = "admin@example.com"
    if not User.objects.filter(email=admin_email).exists():
        admin = User.objects.create_superuser(
            email=admin_email,
            password="adminpassword",
            firstname="System",
            lastname="Administrator",
            role="admin"
        )
        print(f"Created superuser: {admin_email}")
    else:
        admin = User.objects.get(email=admin_email)
        print(f"Superuser already exists: {admin_email}")

    # 2. Create Course
    course, created = Course.objects.get_or_create(
        course_name="B.Sc. Computer Science",
        defaults={'status': 'active'}
    )
    if created:
        print(f"Created course: {course.course_name}")

    # 3. Create Semesters
    sem1, _ = Semester.objects.get_or_create(course=course, semester_no=1)
    sem2, _ = Semester.objects.get_or_create(course=course, semester_no=2)
    print("Created semesters 1 and 2")

    # 4. Create Subjects
    sub1, _ = Subject.objects.get_or_create(
        semester=sem1,
        subject_code="CS101",
        defaults={'subject_name': 'Introduction to Programming'}
    )
    sub2, _ = Subject.objects.get_or_create(
        semester=sem1,
        subject_code="CS102",
        defaults={'subject_name': 'Discrete Mathematics'}
    )
    print(f"Created subjects: {sub1.subject_code}, {sub2.subject_code}")

    # 5. Create Teacher
    teacher_email = "teacher@example.com"
    if not User.objects.filter(email=teacher_email).exists():
        teacher = User.objects.create_user(
            email=teacher_email,
            password="teacherpassword",
            firstname="John",
            lastname="Doe",
            role="teacher"
        )
        print(f"Created teacher: {teacher_email}")
    else:
        teacher = User.objects.get(email=teacher_email)

    # 6. Assign Subject to Teacher
    TeacherSubject.objects.get_or_create(subject=sub1, teacher=teacher)
    TeacherSubject.objects.get_or_create(subject=sub2, teacher=teacher)
    print(f"Assigned subjects to {teacher}")

    # 7. Create Student
    student_email = "student@example.com"
    if not User.objects.filter(email=student_email).exists():
        student_user = User.objects.create_user(
            email=student_email,
            password="studentpassword",
            firstname="Jane",
            lastname="Smith",
            role="student"
        )
        student = Student.objects.create(
            user=student_user,
            course=course,
            current_semester=1,
            enrollment_year=2025
        )
        print(f"Created student: {student_email}")
    else:
        student_user = User.objects.get(email=student_email)
        student = student_user.student_profile

    # 8. Create Class Schedules
    today = timezone.now().date()
    schedule1, _ = ClassSchedule.objects.get_or_create(
        subject=sub1,
        session_date=today,
        start_time=time(9, 0),
        end_time=time(10, 0),
        taught_by=teacher
    )
    schedule2, _ = ClassSchedule.objects.get_or_create(
        subject=sub2,
        session_date=today,
        start_time=time(10, 30),
        end_time=time(11, 30),
        taught_by=teacher
    )
    print(f"Created schedules for {today}")

    # 9. Mark Attendance (Optional)
    Attendance.objects.get_or_create(
        session=schedule1,
        student=student,
        defaults={'status': 'present', 'marked_by': teacher}
    )
    print(f"Marked attendance for {student_user.email} in {sub1.subject_code}")

    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
