from django.test import TestCase, Client
from django.urls import reverse
from core.models import User

class AuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_password = 'password123'
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            password=self.user_password,
            firstname='Teacher',
            lastname='User',
            role='teacher'
        )
        self.student = User.objects.create_user(
            email='student@example.com',
            password=self.user_password,
            firstname='Student',
            lastname='User',
            role='student'
        )
        # Create profile for student
        from core.models import Course, Student
        course = Course.objects.create(course_name='Test Course')
        Student.objects.create(user=self.student, course=course, enrollment_year=2024)

        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password=self.user_password,
            firstname='Admin',
            lastname='User'
        )

    def test_login_teacher(self):
        response = self.client.post(reverse('login'), {
            'email': 'teacher@example.com',
            'password': self.user_password
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('teacher_dashboard'))

    def test_login_student(self):
        response = self.client.post(reverse('login'), {
            'email': 'student@example.com',
            'password': self.user_password
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_login_admin(self):
        response = self.client.post(reverse('login'), {
            'email': 'admin@example.com',
            'password': self.user_password
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {
            'email': 'teacher@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password.')
