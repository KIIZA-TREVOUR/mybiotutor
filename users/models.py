"""
Custom User models for BioTutor platform.
Supports multi-tenant (multi-school) architecture with role-based access.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager for User model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'SUPER_ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for BioTutor.
    
    Role Types:
    - SUPER_ADMIN: Platform owner (manages all schools, global curriculum, content approval)
    - SCHOOL_ADMIN: School manager (manages teachers/students for their school)
    - TEACHER: Content contributor (uploads notes, creates quizzes, manages their students)
    - STUDENT: Learner (accesses content, takes quizzes, uses AI tutor)
    """
    
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('SCHOOL_ADMIN', 'School Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    ]
    
    # Core fields
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # School relationship (NULL for SUPER_ADMIN)
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users'
    )
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return the user's first name."""
        return self.first_name
    
    @property
    def is_super_admin(self):
        return self.role == 'SUPER_ADMIN'
    
    @property
    def is_school_admin(self):
        return self.role == 'SCHOOL_ADMIN'
    
    @property
    def is_teacher(self):
        return self.role == 'TEACHER'
    
    @property
    def is_student(self):
        return self.role == 'STUDENT'


class TeacherProfile(models.Model):
    """Extended profile for Teacher users."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='teacher_profile'
    )
    
    # Professional info
    subject_specialization = models.CharField(max_length=200, default='Biology')
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)
    
    # Contact
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teacher_profiles'
        verbose_name = 'Teacher Profile'
        verbose_name_plural = 'Teacher Profiles'
    
    def __str__(self):
        return f"Teacher Profile: {self.user.get_full_name()}"


class StudentProfile(models.Model):
    """Extended profile for Student users."""
    
    CLASS_LEVEL_CHOICES = [
        ('S1', 'Senior 1'),
        ('S2', 'Senior 2'),
        ('S3', 'Senior 3'),
        ('S4', 'Senior 4'),
        ('S5', 'Senior 5'),
        ('S6', 'Senior 6'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='student_profile'
    )
    
    # Academic info
    class_level = models.CharField(max_length=2, choices=CLASS_LEVEL_CHOICES)
    student_id = models.CharField(max_length=50, unique=True)  # School-specific ID
    
    # Contact
    phone_number = models.CharField(max_length=20, blank=True)
    parent_email = models.EmailField(blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    
    # Learning progress (for adaptive learning)
    weak_topics = models.JSONField(default=list, blank=True)  # List of topic IDs
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        unique_together = ['user', 'student_id']
    
    def __str__(self):
        return f"Student Profile: {self.user.get_full_name()} ({self.class_level})"