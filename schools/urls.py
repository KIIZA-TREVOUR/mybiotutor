"""
URL patterns for schools app.
"""

from django.urls import path
from .views import (
    SchoolCreateView, SchoolListView, SchoolDetailView, MySchoolView
)

app_name = 'schools'

urlpatterns = [
    # Super Admin - School Management
    path('', SchoolCreateView.as_view(), name='create_school'),
    path('list/', SchoolListView.as_view(), name='list_schools'),
    path('<int:pk>/', SchoolDetailView.as_view(), name='school_detail'),
    
    # School Admin - My School
    path('my-school/', MySchoolView.as_view(), name='my_school'),
]