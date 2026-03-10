from django.test import TestCase, Client
from django.urls import reverse
from core.models import User, Course, Student, Subject, TeacherSubject, ClassSchedule, Attendance
from django.utils import timezone

class TeacherViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher_user = User.objects.create_user(
            email='teacher@example.com',
            password='password123',
            firstname='Teacher',
            lastname='User',
            role='teacher'
        )
        self.course = Course.objects.create(course_name='IT')
        self.subject = Subject.objects.create(
            subject_code='IT101',
            subject_name='Web Dev',
            course=self.course
        )
        TeacherSubject.objects.create(teacher=self.teacher_user, subject=self.subject)
        
        # Create a student
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='password123',
            firstname='Student',
            lastname='One',
            role='student'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            course=self.course,
            enrollment_year=2024
        )
        
        # Create sessions
        self.session1 = ClassSchedule.objects.create(
            subject=self.subject,
            session_date=timezone.now().date() - timezone.timedelta(days=1),
            start_time='10:00:00',
            end_time='11:00:00',
            taught_by=self.teacher_user
        )
        self.session2 = ClassSchedule.objects.create(
            subject=self.subject,
            session_date=timezone.now().date(),
            start_time='10:00:00',
            end_time='11:00:00',
            taught_by=self.teacher_user
        )
        
        # Mark attendance
        Attendance.objects.create(
            session=self.session1,
            student=self.student,
            status='present',
            marked_by=self.teacher_user
        )

    def test_teacher_view_students_access(self):
        self.client.login(email='teacher@example.com', password='password123')
        url = reverse('teacher_view_students', kwargs={'subject_id': self.subject.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Web Dev')
        self.assertContains(response, 'Student One')
        
    def test_attendance_columns_presence(self):
        self.client.login(email='teacher@example.com', password='password123')
        url = reverse('teacher_view_students', kwargs={'subject_id': self.subject.id})
        response = self.client.get(url)
        
        # Check if session dates are in the header
        self.assertContains(response, self.session1.session_date.strftime('%b %d'))
        self.assertContains(response, self.session2.session_date.strftime('%b %d'))
        
        # Check if attendance status (Green badge for present) is there
        self.assertContains(response, 'bg-success') # For session1
        self.assertContains(response, 'text-muted') # For session2 (unmarked)

    def test_admin_view_students_access(self):
        admin = User.objects.create_superuser(email='admin@test.com', password='pass', firstname='A', lastname='B')
        self.client.login(email='admin@test.com', password='pass')
        url = reverse('teacher_view_students', kwargs={'subject_id': self.subject.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Web Dev')
