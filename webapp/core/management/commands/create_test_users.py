from django.core.management.base import BaseCommand
from core.models import User


class Command(BaseCommand):
    help = 'Create test users for different roles'
    
    def handle(self, *args, **options):
        # Create Admin user
        admin_email = 'admin@example.com'
        if not User.objects.filter(email=admin_email).exists():
            admin = User.objects.create(
                firstname='Admin',
                lastname='User',
                email=admin_email,
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_email} (password: admin123)'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin user already exists: {admin_email}'))
        
        # Create Teacher user
        teacher_email = 'teacher@example.com'
        if not User.objects.filter(email=teacher_email).exists():
            teacher = User.objects.create(
                firstname='John',
                lastname='Teacher',
                email=teacher_email,
                role='teacher',
                is_active=True
            )
            teacher.set_password('teacher123')
            teacher.save()
            self.stdout.write(self.style.SUCCESS(f'Created teacher user: {teacher_email} (password: teacher123)'))
        else:
            self.stdout.write(self.style.WARNING(f'Teacher user already exists: {teacher_email}'))
        
        # Create Student user
        student_email = 'student@example.com'
        if not User.objects.filter(email=student_email).exists():
            student = User.objects.create(
                firstname='Jane',
                lastname='Student',
                email=student_email,
                role='student',
                is_active=True
            )
            student.set_password('student123')
            student.save()
            self.stdout.write(self.style.SUCCESS(f'Created student user: {student_email} (password: student123)'))
        else:
            self.stdout.write(self.style.WARNING(f'Student user already exists: {student_email}'))
        
        self.stdout.write(self.style.SUCCESS('\nAll test users created successfully!'))
        self.stdout.write('\nTest Credentials:')
        self.stdout.write('  Admin:   admin@example.com / admin123')
        self.stdout.write('  Teacher: teacher@example.com / teacher123')
        self.stdout.write('  Student: student@example.com / student123')
