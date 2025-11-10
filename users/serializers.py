"""
Serializers for User, TeacherProfile, and StudentProfile models.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, TeacherProfile, StudentProfile
from schools.models import School


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 
            'school', 'password', 'password_confirm'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        """Validate password confirmation and role-school relationship."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        
        # Super Admin should not have a school
        if attrs.get('role') == 'SUPER_ADMIN' and attrs.get('school'):
            raise serializers.ValidationError({
                "school": "Super Admin cannot be assigned to a school."
            })
        
        # All other roles must have a school
        if attrs.get('role') != 'SUPER_ADMIN' and not attrs.get('school'):
            raise serializers.ValidationError({
                "school": "This role requires a school assignment."
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create profile based on role
        if user.role == 'TEACHER':
            TeacherProfile.objects.create(user=user)
        elif user.role == 'STUDENT':
            # Student ID will be set separately
            StudentProfile.objects.create(
                user=user,
                class_level='S1',  # Default, will be updated
                student_id=f"STD{user.id:06d}"  # Auto-generate
            )
        
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for user information."""
    
    school_name = serializers.CharField(source='school.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'school', 'school_name', 'is_active',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'is_active']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs


class TeacherProfileSerializer(serializers.ModelSerializer):
    """Serializer for teacher profile."""
    
    user = UserDetailSerializer(read_only=True)
    
    class Meta:
        model = TeacherProfile
        fields = [
            'user', 'subject_specialization', 'years_of_experience',
            'bio', 'phone_number', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TeacherProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating teacher profile."""
    
    class Meta:
        model = TeacherProfile
        fields = [
            'subject_specialization', 'years_of_experience',
            'bio', 'phone_number'
        ]


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for student profile."""
    
    user = UserDetailSerializer(read_only=True)
    class_level_display = serializers.CharField(
        source='get_class_level_display',
        read_only=True
    )
    
    class Meta:
        model = StudentProfile
        fields = [
            'user', 'class_level', 'class_level_display', 'student_id',
            'phone_number', 'parent_email', 'parent_phone',
            'weak_topics', 'created_at', 'updated_at'
        ]
        read_only_fields = ['student_id', 'weak_topics', 'created_at', 'updated_at']


class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating student profile."""
    
    class Meta:
        model = StudentProfile
        fields = [
            'class_level', 'phone_number', 'parent_email', 'parent_phone'
        ]


class BulkStudentCreateSerializer(serializers.Serializer):
    """Serializer for bulk student creation from CSV."""
    
    students = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
    
    def validate_students(self, value):
        """Validate each student entry."""
        required_fields = ['email', 'first_name', 'last_name', 'class_level']
        
        for idx, student in enumerate(value):
            for field in required_fields:
                if field not in student:
                    raise serializers.ValidationError(
                        f"Student {idx + 1}: Missing required field '{field}'"
                    )
            
            # Validate email format
            email = student.get('email')
            if email and User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    f"Student {idx + 1}: Email '{email}' already exists"
                )
            
            # Validate class level
            class_level = student.get('class_level')
            valid_levels = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
            if class_level not in valid_levels:
                raise serializers.ValidationError(
                    f"Student {idx + 1}: Invalid class level '{class_level}'"
                )
        
        return value