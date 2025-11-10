"""
Script to create test data for Phase 1 testing.
Run with: python manage.py shell < scripts/create_test_data.py
"""

from django.contrib.auth import get_user_model
from schools.models import School

User = get_user_model()

print("Creating test data...")

# Create a test school
school, created = School.objects.get_or_create(
    name="Test High School",
    defaults={
        'email': 'admin@testhigh.com',
        'phone_number': '+256700000000',
        'address': '123 Test Street',
        'district': 'Kampala',
        'region': 'Central',
        'registration_number': 'THS2025',
        'subscription_type': 'BASIC'
    }
)

if created:
    print(f"✓ Created school: {school.name}")
else:
    print(f"✓ School already exists: {school.name}")

# Create Super Admin (if not exists)
if not User.objects.filter(email='superadmin@biotutor.com').exists():
    super_admin = User.objects.create_superuser(
        email='superadmin@biotutor.com',
        password='Admin@2025',
        first_name='Super',
        last_name='Admin',
        role='SUPER_ADMIN'
    )
    print(f"✓ Created Super Admin: {super_admin.email}")
else:
    print("✓ Super Admin already exists")

# Create School Admin
if not User.objects.filter(email='schooladmin@testhigh.com').exists():
    school_admin = User.objects.create_user(
        email='schooladmin@testhigh.com',
        password='School@2025',
        first_name='School',
        last_name='Administrator',
        role='SCHOOL_ADMIN',
        school=school
    )
    print(f"✓ Created School Admin: {school_admin.email}")
else:
    print("✓ School Admin already exists")

# Create Teacher
if not User.objects.filter(email='teacher@testhigh.com').exists():
    teacher = User.objects.create_user(
        email='teacher@testhigh.com',
        password='Teacher@2025',
        first_name='Test',
        last_name='Teacher',
        role='TEACHER',
        school=school
    )
    print(f"✓ Created Teacher: {teacher.email}")
else:
    print("✓ Teacher already exists")

# Create Student
if not User.objects.filter(email='student@testhigh.com').exists():
    student = User.objects.create_user(
        email='student@testhigh.com',
        password='Student@2025',
        first_name='Test',
        last_name='Student',
        role='STUDENT',
        school=school
    )
    print(f"✓ Created Student: {student.email}")
else:
    print("✓ Student already exists")

print("\n" + "="*50)
print("TEST CREDENTIALS:")
print("="*50)
print("Super Admin:")
print("  Email: superadmin@biotutor.com")
print("  Password: Admin@2025")
print("\nSchool Admin:")
print("  Email: schooladmin@testhigh.com")
print("  Password: School@2025")
print("\nTeacher:")
print("  Email: teacher@testhigh.com")
print("  Password: Teacher@2025")
print("\nStudent:")
print("  Email: student@testhigh.com")
print("  Password: Student@2025")
print("="*50)