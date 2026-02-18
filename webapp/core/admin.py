from django.contrib import admin
import secrets
from .models import User, Student, Course, Semester, Subject, TeacherSubject, ClassSchedule, Attendance, ApiKey


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'email', 'role', 'date_joined']
    list_filter = ['role', 'date_joined']
    search_fields = ['firstname', 'lastname', 'email']
    readonly_fields = ['id', 'date_joined', 'updated_at']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_name', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['course_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['course', 'semester_no', 'created_at']
    list_filter = ['course']
    search_fields = ['course__course_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subject_code', 'subject_name', 'semester', 'created_at']
    list_filter = ['semester__course']
    search_fields = ['subject_code', 'subject_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'enrollment_year', 'updated_by', 'created_at']
    list_filter = ['enrollment_year']
    search_fields = ['user__firstname', 'user__lastname', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'created_at']
    list_filter = ['subject__semester__course']
    search_fields = ['teacher__firstname', 'teacher__lastname', 'subject__subject_name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['subject', 'session_date', 'start_time', 'end_time', 'taught_by']
    list_filter = ['session_date', 'subject__semester__course']
    search_fields = ['subject__subject_name', 'taught_by__firstname', 'taught_by__lastname']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'session_date'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'status', 'marked_by', 'marked_at']
    list_filter = ['status', 'session__session_date']
    search_fields = ['student__user__firstname', 'student__user__lastname']
    readonly_fields = ['id', 'marked_at', 'updated_at']
    date_hierarchy = 'session__session_date'


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ['short_key', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['generate_key']

    def short_key(self, obj):
        if not obj.key:
            return '(empty)'
        return obj.key[:8] + '...' + obj.key[-8:]

    short_key.short_description = 'API Key (partial)'

    def generate_key(self, request, queryset):
        for obj in queryset:
            obj.key = secrets.token_urlsafe(32)
            obj.save()
        self.message_user(request, "Generated new API key for selected entries.")

    generate_key.short_description = 'Generate new API key for selected'