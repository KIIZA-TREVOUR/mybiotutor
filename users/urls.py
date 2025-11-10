"""
URL patterns for users app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView, logout_view, CurrentUserView,
    ChangePasswordView, password_reset_request,
    SchoolAdminCreateView, AllUsersListView, UserDetailView,
    TeacherCreateView, SchoolTeachersListView,
    StudentCreateView, BulkStudentCreateView, SchoolStudentsListView,
    SchoolUserDetailView, TeacherProfileView, StudentProfileView
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/password-reset/', password_reset_request, name='password_reset'),
    
    # Super Admin - User Management
    path('super-admin/school-admins/', SchoolAdminCreateView.as_view(), name='create_school_admin'),
    path('super-admin/users/', AllUsersListView.as_view(), name='all_users'),
    path('super-admin/users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    
    # School Admin - Teacher Management
    path('school-admin/teachers/', TeacherCreateView.as_view(), name='create_teacher'),
    path('school-admin/teachers/list/', SchoolTeachersListView.as_view(), name='list_teachers'),
    
    # School Admin - Student Management
    path('school-admin/students/', StudentCreateView.as_view(), name='create_student'),
    path('school-admin/students/bulk/', BulkStudentCreateView.as_view(), name='bulk_create_students'),
    path('school-admin/students/list/', SchoolStudentsListView.as_view(), name='list_students'),
    
    # School Admin - User Detail
    path('school-admin/users/<int:pk>/', SchoolUserDetailView.as_view(), name='school_user_detail'),
    
    # User Profiles
    path('profile/teacher/', TeacherProfileView.as_view(), name='teacher_profile'),
    path('profile/student/', StudentProfileView.as_view(), name='student_profile'),
]