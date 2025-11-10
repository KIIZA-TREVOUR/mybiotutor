"""
API views for user authentication and management.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import User, TeacherProfile, StudentProfile
from .serializers import (
    UserRegistrationSerializer, UserDetailSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, TeacherProfileSerializer,
    TeacherProfileUpdateSerializer, StudentProfileSerializer,
    StudentProfileUpdateSerializer, BulkStudentCreateSerializer
)
from .permissions import (
    IsSuperAdmin, IsSchoolAdmin, IsSuperAdminOrSchoolAdmin,
    IsOwnerOrAdmin, IsSameSchool
)

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer to include user details."""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom claims
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            'school_id': self.user.school.id if self.user.school else None,
            'school_name': self.user.school.name if self.user.school else None,
        }
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view with user details."""
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    request=None,
    responses={200: OpenApiResponse(description='Logout successful')},
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout user by blacklisting the refresh token.
    """
    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response(
            {"message": "Successfully logged out"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    tags=['Authentication']
)
class CurrentUserView(generics.RetrieveAPIView):
    """Get current authenticated user details."""
    
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@extend_schema(
    tags=['Authentication']
)
class ChangePasswordView(generics.UpdateAPIView):
    """Change password for authenticated user."""
    
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    request=PasswordResetRequestSerializer
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    """
    Request password reset. Sends reset link to email.
    (Simplified for MVP - will be enhanced with email service)
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            # TODO: Generate reset token and send email
            # For MVP, we'll just return success
            
            return Response(
                {"message": "Password reset link sent to email"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            return Response(
                {"message": "Password reset link sent to email"},
                status=status.HTTP_200_OK
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# SUPER ADMIN VIEWS
# ============================================================================

@extend_schema(
    tags=['Super Admin - User Management']
)
class SchoolAdminCreateView(generics.CreateAPIView):
    """
    Super Admin: Create a School Admin account.
    """
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsSuperAdmin]
    
    def perform_create(self, serializer):
        # Force role to be SCHOOL_ADMIN
        serializer.save(role='SCHOOL_ADMIN')


@extend_schema(
    tags=['Super Admin - User Management']
)
class AllUsersListView(generics.ListAPIView):
    """
    Super Admin: List all users across all schools.
    """
    
    serializer_class = UserDetailSerializer
    permission_classes = [IsSuperAdmin]
    
    def get_queryset(self):
        queryset = User.objects.all().select_related('school')
        
        # Filter by role if specified
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by school if specified
        school_id = self.request.query_params.get('school', None)
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        
        return queryset


@extend_schema(
    tags=['Super Admin - User Management']
)
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Super Admin: Retrieve, update, or deactivate any user.
    """
    
    queryset = User.objects.all()
    permission_classes = [IsSuperAdmin]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserDetailSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete - deactivate user instead of deleting."""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        return Response(
            {"message": "User deactivated successfully"},
            status=status.HTTP_200_OK
        )


# ============================================================================
# SCHOOL ADMIN VIEWS
# ============================================================================

@extend_schema(
    tags=['School Admin - Teacher Management']
)
class TeacherCreateView(generics.CreateAPIView):
    """
    School Admin: Create a Teacher account for their school.
    """
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsSchoolAdmin]
    
    def perform_create(self, serializer):
        # Force role to be TEACHER and assign to school admin's school
        serializer.save(
            role='TEACHER',
            school=self.request.user.school
        )


@extend_schema(
    tags=['School Admin - Teacher Management']
)
class SchoolTeachersListView(generics.ListAPIView):
    """
    School Admin: List all teachers in their school.
    """
    
    serializer_class = UserDetailSerializer
    permission_classes = [IsSchoolAdmin]
    
    def get_queryset(self):
        return User.objects.filter(
            school=self.request.user.school,
            role='TEACHER'
        ).select_related('school')


@extend_schema(
    tags=['School Admin - Student Management']
)
class StudentCreateView(generics.CreateAPIView):
    """
    School Admin: Create a Student account for their school.
    """
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsSchoolAdmin]
    
    def perform_create(self, serializer):
        # Force role to be STUDENT and assign to school admin's school
        serializer.save(
            role='STUDENT',
            school=self.request.user.school
        )


@extend_schema(
    tags=['School Admin - Student Management']
)
class BulkStudentCreateView(APIView):
    """
    School Admin: Bulk create students from CSV data.
    """
    
    permission_classes = [IsSchoolAdmin]
    
    def post(self, request):
        serializer = BulkStudentCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            students_data = serializer.validated_data['students']
            created_students = []
            
            for student_data in students_data:
                # Create user
                user = User.objects.create_user(
                    email=student_data['email'],
                    first_name=student_data['first_name'],
                    last_name=student_data['last_name'],
                    role='STUDENT',
                    school=request.user.school,
                    password=student_data.get('password', 'BioTutor2025!')  # Default password
                )
                
                # Create student profile
                StudentProfile.objects.create(
                    user=user,
                    class_level=student_data['class_level'],
                    student_id=student_data.get('student_id', f"STD{user.id:06d}"),
                    phone_number=student_data.get('phone_number', ''),
                    parent_email=student_data.get('parent_email', ''),
                    parent_phone=student_data.get('parent_phone', '')
                )
                
                created_students.append({
                    'id': user.id,
                    'email': user.email,
                    'name': user.get_full_name(),
                    'student_id': user.student_profile.student_id
                })
            
            return Response(
                {
                    "message": f"Successfully created {len(created_students)} students",
                    "students": created_students
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['School Admin - Student Management']
)
class SchoolStudentsListView(generics.ListAPIView):
    """
    School Admin: List all students in their school.
    """
    
    serializer_class = UserDetailSerializer
    permission_classes = [IsSchoolAdmin]
    
    def get_queryset(self):
        queryset = User.objects.filter(
            school=self.request.user.school,
            role='STUDENT'
        ).select_related('school')
        
        # Filter by class level if specified
        class_level = self.request.query_params.get('class_level', None)
        if class_level:
            queryset = queryset.filter(student_profile__class_level=class_level)
        
        return queryset


@extend_schema(
    tags=['School Admin - User Management']
)
class SchoolUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    School Admin: Manage a user (teacher/student) in their school.
    """
    
    permission_classes = [IsSchoolAdmin, IsSameSchool]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserDetailSerializer
    
    def get_queryset(self):
        # School admin can only access users from their school
        return User.objects.filter(
            school=self.request.user.school
        ).select_related('school')
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete - deactivate user instead of deleting."""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        return Response(
            {"message": "User deactivated successfully"},
            status=status.HTTP_200_OK
        )


# ============================================================================
# PROFILE VIEWS
# ============================================================================

@extend_schema(
    tags=['User Profiles']
)
class TeacherProfileView(generics.RetrieveUpdateAPIView):
    """
    Teacher: View and update their profile.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TeacherProfileUpdateSerializer
        return TeacherProfileSerializer
    
    def get_object(self):
        # Get the teacher profile for the authenticated user
        return TeacherProfile.objects.select_related('user').get(
            user=self.request.user
        )


@extend_schema(
    tags=['User Profiles']
)
class StudentProfileView(generics.RetrieveUpdateAPIView):
    """
    Student: View and update their profile.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return StudentProfileUpdateSerializer
        return StudentProfileSerializer
    
    def get_object(self):
        # Get the student profile for the authenticated user
        return StudentProfile.objects.select_related('user').get(
            user=self.request.user
        )