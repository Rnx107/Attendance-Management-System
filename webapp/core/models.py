import uuid
import secrets
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid
import secrets


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model for admin, teacher, and student roles"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100, blank=True, null=True)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    objects = UserManager()

    class Meta:
        db_table = 'user'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.role})"


class Course(models.Model):
    """Course model (e.g., Computer Science, Engineering)"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course'
        ordering = ['course_name']

    def __str__(self):
        return self.course_name


class Semester(models.Model):
    """Semester model linked to courses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='semesters')
    semester_no = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'semester'
        ordering = ['course', 'semester_no']
        unique_together = ['course', 'semester_no']

    def __str__(self):
        return f"{self.course.course_name} - Semester {self.semester_no}"


class Subject(models.Model):
    """Subject model for each semester"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    subject_code = models.CharField(max_length=50, unique=True)
    subject_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subject'
        ordering = ['subject_code']

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


class Student(models.Model):
    """Student profile linked to User"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='students')
    current_semester = models.IntegerField(default=1)
    enrollment_year = models.IntegerField()
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_students')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student'
        ordering = ['-enrollment_year', 'user__lastname']

    def __str__(self):
        return f"{self.user.firstname} {self.user.lastname} - {self.enrollment_year}"


class TeacherSubject(models.Model):
    """Maps teachers to subjects they teach"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teacher_assignments')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, related_name='teaching_subjects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teacher_subject'
        unique_together = ['subject', 'teacher']
        ordering = ['subject', 'teacher']

    def __str__(self):
        return f"{self.teacher} teaches {self.subject}"


class ClassSchedule(models.Model):
    """Class schedule for each subject session"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules')
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    taught_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, related_name='classes_taught')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'class_schedule'
        ordering = ['-session_date', 'start_time']

    def __str__(self):
        return f"{self.subject} on {self.session_date} at {self.start_time}"


class Attendance(models.Model):
    """Attendance records for students in class sessions"""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    
    VERIFICATION_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='pending')
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    marked_at = models.DateTimeField(default=timezone.now)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verified_attendances')
    verified_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance'
        unique_together = ['session', 'student']
        ordering = ['-session__session_date', 'student__user__lastname']

    def __str__(self):
        return f"{self.student.user} - {self.session} - {self.status}"


class ApiKey(models.Model):
    """Stores a single API key used by the official Flutter app.

    The admin can create or regenerate this key from Django admin. Use
    `ApiKey.get_solo()` to retrieve the current key (creates one if missing).
    """
    key = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_key'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj

    def __str__(self):
        return f"ApiKey (created: {self.created_at})"