from django.test import TestCase
from core.models import User, Course, Student, Subject, TeacherSubject, ClassSchedule, Attendance
from django.utils import timezone

class ModelTestCase(TestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='password123',
            firstname='Admin',
            lastname='User'
        )
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            password='password123',
            firstname='Teacher',
            lastname='User',
            role='teacher'
        )
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='password123',
            firstname='Student',
            lastname='User',
            role='student'
        )

        # Create Course
        self.course = Course.objects.create(course_name='Computer Science')

        # Create Student Profile
        self.student = Student.objects.create(
            user=self.student_user,
            course=self.course,
            enrollment_year=2024
        )

        # Create Subject
        self.subject = Subject.objects.create(
            subject_code='CS101',
            subject_name='Programming 1',
            course=self.course
        )

        # Assign Teacher
        TeacherSubject.objects.create(teacher=self.teacher, subject=self.subject)

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(self.admin.role, 'admin')
        self.assertEqual(self.teacher.role, 'teacher')
        self.assertEqual(self.student_user.role, 'student')

    def test_course_creation(self):
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(self.course.course_name, 'Computer Science')

    def test_subject_creation(self):
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(self.subject.subject_code, 'CS101')
        self.assertEqual(self.subject.course, self.course)

    def test_teacher_assignment(self):
        self.assertTrue(self.subject.teacher_assignments.filter(teacher=self.teacher).exists())

    def test_class_schedule_and_attendance(self):
        # Create Session
        session = ClassSchedule.objects.create(
            subject=self.subject,
            session_date=timezone.now().date(),
            start_time='09:00:00',
            end_time='10:00:00',
            taught_by=self.teacher
        )
        
        # Test Helper Properties
        self.assertTrue(session.is_today)
        self.assertFalse(session.is_past)

        # Create Attendance
        attendance = Attendance.objects.create(
            session=session,
            student=self.student,
            status='present',
            marked_by=self.teacher
        )

        self.assertEqual(Attendance.objects.count(), 1)
        self.assertEqual(attendance.status, 'present')
