"""
Serializers for School model.
"""

from rest_framework import serializers
from .models import School


class SchoolCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a school."""
    
    class Meta:
        model = School
        fields = [
            'name', 'email', 'phone_number', 'address',
            'district', 'region', 'registration_number',
            'subscription_type', 'subscription_start_date',
            'subscription_end_date'
        ]
    
    def validate_name(self, value):
        """Ensure school name is unique."""
        if School.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError(
                "A school with this name already exists."
            )
        return value


class SchoolDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for school information."""
    
    total_students = serializers.IntegerField(read_only=True)
    total_teachers = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'slug', 'email', 'phone_number',
            'address', 'district', 'region', 'registration_number',
            'is_active', 'subscription_type', 'subscription_start_date',
            'subscription_end_date', 'total_students', 'total_teachers',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class SchoolUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating school information."""
    
    class Meta:
        model = School
        fields = [
            'name', 'email', 'phone_number', 'address',
            'district', 'region', 'registration_number',
            'is_active', 'subscription_type',
            'subscription_start_date', 'subscription_end_date'
        ]


class SchoolListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for school list."""
    
    total_students = serializers.IntegerField(read_only=True)
    total_teachers = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'slug', 'district', 'region',
            'is_active', 'subscription_type',
            'total_students', 'total_teachers'
        ]