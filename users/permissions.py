"""
Custom permission classes for role-based access control.
"""

from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """Permission class for Super Admin only."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'SUPER_ADMIN'
        )


class IsSchoolAdmin(permissions.BasePermission):
    """Permission class for School Admin only."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'SCHOOL_ADMIN'
        )


class IsTeacher(permissions.BasePermission):
    """Permission class for Teacher only."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'TEACHER'
        )


class IsStudent(permissions.BasePermission):
    """Permission class for Student only."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'STUDENT'
        )


class IsSuperAdminOrSchoolAdmin(permissions.BasePermission):
    """Permission class for Super Admin or School Admin."""
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['SUPER_ADMIN', 'SCHOOL_ADMIN']
        )


class IsSameSchool(permissions.BasePermission):
    """
    Permission class to ensure School Admin can only access
    users from their own school.
    """
    
    def has_object_permission(self, request, view, obj):
        # Super Admin has access to everything
        if request.user.role == 'SUPER_ADMIN':
            return True
        
        # School Admin can only access users from their school
        if request.user.role == 'SCHOOL_ADMIN':
            # Check if the object has a school attribute
            if hasattr(obj, 'school'):
                return obj.school == request.user.school
            # If object is a User
            if hasattr(obj, 'role'):
                return obj.school == request.user.school
        
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class to allow users to access their own data,
    or admins to access any data.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.role in ['SUPER_ADMIN', 'SCHOOL_ADMIN']:
            return True
        
        # Users can access their own data
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user