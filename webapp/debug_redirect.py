import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
django.setup()

from core.models import User, Course, Student

def debug_redirect():
    client = Client()
    email = 'test_student@example.com'
    password = 'password123'
    
    # Create user
    user, created = User.objects.get_or_create(
        email=email,
        defaults={'firstname': 'Test', 'lastname': 'Student', 'role': 'student'}
    )
    user.set_password(password)
    user.save()
    
    # Create student profile
    course, _ = Course.objects.get_or_create(course_name='Test Course')
    Student.objects.get_or_create(user=user, defaults={'course': course, 'enrollment_year': 2024})
    
    # Login
    client.post(reverse('login'), {'email': email, 'password': password})
    
    # Try accessing dashboard
    response = client.get(reverse('student_dashboard'))
    print(f"Status Code: {response.status_code}")
    if response.status_code == 302:
        print(f"Redirect Target: {response.url}")

if __name__ == '__main__':
    debug_redirect()
