from django.contrib import admin
from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'region', 'is_active', 'subscription_type']
    list_filter = ['is_active', 'subscription_type', 'region']
    search_fields = ['name', 'district', 'registration_number']
    prepopulated_fields = {'slug': ('name',)}