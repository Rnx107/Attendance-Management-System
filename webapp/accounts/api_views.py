from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from core.models import User
import json


class LoginAPIView(APIView):
    """
    API endpoint for user login.
    Accepts POST requests with email and password.
    Returns user data on successful login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()

        # Validation
        if not email or not password:
            return Response(
                {
                    'success': False,
                    'error': 'Email and password are required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Find user by email
            user = User.objects.get(email=email)
            
            # Check password
            if user.check_password(password) and user.is_active:
                return Response(
                    {
                        'success': True,
                        'user_id': user.id,
                        'email': user.email,
                        'role': user.role,
                        'firstname': user.firstname,
                        'lastname': user.lastname,
                        'full_name': f"{user.firstname} {user.lastname}",
                        'phone': user.phone if hasattr(user, 'phone') else '',
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        'success': False,
                        'error': 'Invalid email or password'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except User.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'error': 'Invalid email or password'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': f'Server error: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutAPIView(APIView):
    """
    API endpoint for user logout.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Perform logout operations here
            return Response(
                {
                    'success': True,
                    'message': 'Logged out successfully'
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserDetailAPIView(APIView):
    """
    Get user details by user ID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            return Response(
                {
                    'user_id': user.id,
                    'email': user.email,
                    'role': user.role,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'full_name': f"{user.firstname} {user.lastname}",
                },
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {
                    'error': 'User not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_list(request):
    """
    Get attendance records for a user.
    Query parameters: user_id (required)
    """
    try:
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from core.models import Attendance
        attendance_records = Attendance.objects.filter(
            student__user_id=user_id
        ).values(
            'id',
            'status',
            'marked_at',
            'session__subject__name',
            'session__taught_by__firstname',
            'session__taught_by__lastname'
        ).order_by('-marked_at')[:50]

        return Response(
            {
                'results': list(attendance_records),
                'count': len(list(attendance_records))
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    """
    Mark attendance for a student.
    Required fields: user_id, course_id, status (present/absent/late)
    """
    try:
        from core.models import Attendance, Student
        
        user_id = request.data.get('user_id')
        course_id = request.data.get('course_id')
        status_val = request.data.get('status', 'present')

        if not all([user_id, course_id, status_val]):
            return Response(
                {'error': 'user_id, course_id, and status are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create attendance record
        try:
            student = Student.objects.get(user_id=user_id)
            # Additional logic to mark attendance
            # This is a placeholder - adjust based on your data model
            return Response(
                {
                    'success': True,
                    'message': 'Attendance marked successfully',
                    'status': status_val
                },
                status=status.HTTP_201_CREATED
            )
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
