from rest_framework import serializers
from .models import User, Student, Course, Semester, Subject, TeacherSubject, ClassSchedule, Attendance


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'firstname', 'middlename', 'lastname', 'full_name', 'email', 'role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return f"{obj.firstname} {obj.middlename or ''} {obj.lastname}".strip()


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    class Meta:
        model = User
        fields = ['firstname', 'middlename', 'lastname', 'email', 'role']
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    semester_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'course_name', 'status', 'semester_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_semester_count(self, obj):
        return obj.semesters.count()


class SemesterSerializer(serializers.ModelSerializer):
    """Serializer for Semester model"""
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    subject_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Semester
        fields = ['id', 'course', 'course_name', 'semester_no', 'subject_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_subject_count(self, obj):
        return obj.subjects.count()


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model"""
    semester_info = serializers.SerializerMethodField()
    course_name = serializers.CharField(source='semester.course.course_name', read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'semester', 'semester_info', 'course_name', 'subject_code', 'subject_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_semester_info(self, obj):
        return {
            'semester_no': obj.semester.semester_no,
            'course_name': obj.semester.course.course_name,
            'course_id': str(obj.semester.course.id)
        }


class SubjectDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Subject with teachers"""
    teachers = serializers.SerializerMethodField()
    semester_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = ['id', 'subject_code', 'subject_name', 'semester', 'semester_info', 'teachers', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_teachers(self, obj):
        teacher_assignments = obj.teacher_assignments.all()
        return [{
            'id': str(ta.teacher.id),
            'name': f"{ta.teacher.firstname} {ta.teacher.lastname}",
            'email': ta.teacher.email
        } for ta in teacher_assignments]
    
    def get_semester_info(self, obj):
        return {
            'semester_no': obj.semester.semester_no,
            'course_name': obj.semester.course.course_name
        }


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model"""
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    attendance_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'user_id', 'enrollment_year', 'attendance_summary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_attendance_summary(self, obj):
        total = obj.attendance_records.count()
        if total == 0:
            return {'total': 0, 'present': 0, 'absent': 0, 'late': 0, 'percentage': 0}
        
        present = obj.attendance_records.filter(status='present').count()
        absent = obj.attendance_records.filter(status='absent').count()
        late = obj.attendance_records.filter(status='late').count()
        
        return {
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'percentage': round((present / total) * 100, 2)
        }


class TeacherSubjectSerializer(serializers.ModelSerializer):
    """Serializer for Teacher-Subject assignment"""
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    subject_code = serializers.CharField(source='subject.subject_code', read_only=True)
    
    class Meta:
        model = TeacherSubject
        fields = ['id', 'subject', 'subject_name', 'subject_code', 'teacher', 'teacher_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_teacher_name(self, obj):
        return f"{obj.teacher.firstname} {obj.teacher.lastname}"


class ClassScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Class Schedule"""
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    subject_code = serializers.CharField(source='subject.subject_code', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    attendance_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassSchedule
        fields = [
            'id', 'subject', 'subject_name', 'subject_code', 
            'session_date', 'start_time', 'end_time', 
            'taught_by', 'teacher_name', 'attendance_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_teacher_name(self, obj):
        return f"{obj.taught_by.firstname} {obj.taught_by.lastname}"
    
    def get_attendance_count(self, obj):
        total = obj.attendances.count()
        present = obj.attendances.filter(status='present').count()
        return {
            'total': total,
            'present': present,
            'absent': obj.attendances.filter(status='absent').count(),
            'late': obj.attendances.filter(status='late').count(),
            'percentage': round((present / total * 100), 2) if total > 0 else 0
        }


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance records"""
    student_name = serializers.SerializerMethodField()
    student_email = serializers.CharField(source='student.user.email', read_only=True)
    subject_name = serializers.CharField(source='session.subject.subject_name', read_only=True)
    session_date = serializers.DateField(source='session.session_date', read_only=True)
    marked_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'session', 'student', 'student_name', 'student_email',
            'subject_name', 'session_date', 'status', 
            'marked_by', 'marked_by_name', 'marked_at', 'updated_at'
        ]
        read_only_fields = ['id', 'marked_at', 'updated_at']
    
    def get_student_name(self, obj):
        return f"{obj.student.user.firstname} {obj.student.user.lastname}"
    
    def get_marked_by_name(self, obj):
        if obj.marked_by:
            return f"{obj.marked_by.firstname} {obj.marked_by.lastname}"
        return None


class AttendanceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating attendance"""
    class Meta:
        model = Attendance
        fields = ['session', 'student', 'status', 'marked_by']
    
    def validate(self, data):
        # Check if attendance already exists for this session and student
        if self.instance is None:  # Only for creation
            if Attendance.objects.filter(session=data['session'], student=data['student']).exists():
                raise serializers.ValidationError("Attendance already marked for this student in this session")
        return data


class BulkAttendanceSerializer(serializers.Serializer):
    """Serializer for bulk attendance marking"""
    session_id = serializers.UUIDField()
    attendances = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )
    marked_by = serializers.UUIDField()
    
    def validate_attendances(self, value):
        """Validate attendance list structure"""
        for attendance in value:
            if 'student_id' not in attendance or 'status' not in attendance:
                raise serializers.ValidationError("Each attendance must have student_id and status")
            if attendance['status'] not in ['present', 'absent', 'late']:
                raise serializers.ValidationError("Status must be present, absent, or late")
        return value


class StudentAttendanceReportSerializer(serializers.Serializer):
    """Serializer for student attendance report"""
    student = StudentSerializer()
    subjects = serializers.SerializerMethodField()
    overall_summary = serializers.SerializerMethodField()
    
    def get_subjects(self, obj):
        # Group attendance by subject
        student = obj['student']
        attendances = student.attendance_records.select_related('session__subject')
        
        subject_data = {}
        for att in attendances:
            subject = att.session.subject
            if subject.id not in subject_data:
                subject_data[subject.id] = {
                    'subject_name': subject.subject_name,
                    'subject_code': subject.subject_code,
                    'total': 0,
                    'present': 0,
                    'absent': 0,
                    'late': 0
                }
            
            subject_data[subject.id]['total'] += 1
            subject_data[subject.id][att.status] += 1
        
        # Calculate percentages
        for subject_id, data in subject_data.items():
            data['percentage'] = round((data['present'] / data['total'] * 100), 2) if data['total'] > 0 else 0
        
        return list(subject_data.values())
    
    def get_overall_summary(self, obj):
        student = obj['student']
        total = student.attendance_records.count()
        if total == 0:
            return {'total': 0, 'present': 0, 'absent': 0, 'late': 0, 'percentage': 0}
        
        present = student.attendance_records.filter(status='present').count()
        absent = student.attendance_records.filter(status='absent').count()
        late = student.attendance_records.filter(status='late').count()
        
        return {
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'percentage': round((present / total) * 100, 2)
        }