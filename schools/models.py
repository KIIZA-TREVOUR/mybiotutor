"""
School (Tenant) models for multi-school architecture.
"""

from django.db import models
from django.utils.text import slugify


class School(models.Model):
    """
    School model - represents a tenant in the multi-tenant architecture.
    Each school is a separate educational institution using the platform.
    """
    
    # Basic information
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    # Contact information
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    district = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    
    # Registration details
    registration_number = models.CharField(max_length=100, unique=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Subscription info (for future use)
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('FREE', 'Free'),
            ('BASIC', 'Basic'),
            ('PREMIUM', 'Premium'),
        ],
        default='FREE'
    )
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schools'
        verbose_name = 'School'
        verbose_name_plural = 'Schools'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def total_students(self):
        """Return count of active students in this school."""
        return self.users.filter(role='STUDENT', is_active=True).count()
    
    @property
    def total_teachers(self):
        """Return count of active teachers in this school."""
        return self.users.filter(role='TEACHER', is_active=True).count()