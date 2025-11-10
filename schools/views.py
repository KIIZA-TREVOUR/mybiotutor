"""
API views for school management.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import School
from .serializers import (
    SchoolCreateSerializer, SchoolDetailSerializer,
    SchoolUpdateSerializer, SchoolListSerializer
)
from users.permissions import IsSuperAdmin, IsSuperAdminOrSchoolAdmin


@extend_schema(
    tags=['Super Admin - School Management']
)
class SchoolCreateView(generics.CreateAPIView):
    """
    Super Admin: Create a new school (tenant).
    """
    
    serializer_class = SchoolCreateSerializer
    permission_classes = [IsSuperAdmin]


@extend_schema(
    tags=['Super Admin - School Management']
)
class SchoolListView(generics.ListAPIView):
    """
    Super Admin: List all schools.
    """
    
    serializer_class = SchoolListSerializer
    permission_classes = [IsSuperAdmin]
    queryset = School.objects.all()


@extend_schema(
    tags=['Super Admin - School Management', 'School Admin']
)
class SchoolDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Super Admin: Full access to any school.
    School Admin: Read-only access to their own school.
    """
    
    queryset = School.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SchoolUpdateSerializer
        return SchoolDetailSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsSuperAdmin()]
        return [IsSuperAdminOrSchoolAdmin()]  # 
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete - deactivate school instead of deleting."""
        school = self.get_object()
        school.is_active = False
        school.save()
        
        return Response(
            {"message": "School deactivated successfully"},
            status=status.HTTP_200_OK
        )


@extend_schema(
    tags=['School Admin']
)
class MySchoolView(generics.RetrieveAPIView):
    """
    School Admin: View their own school details.
    """
    
    serializer_class = SchoolDetailSerializer
    permission_classes = [IsSuperAdminOrSchoolAdmin]  # Or just [IsSchoolAdmin] if you prefer strictness
    
    def get_object(self):
        return self.request.user.school  # 