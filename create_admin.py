#!/usr/bin/env python
"""
Script to create admin user for DetectSus
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.contrib.auth import get_user_model
from app.models import TeacherProfile

User = get_user_model()

# Admin credentials
username = 'admin'
email = 'admin@detectsus.local'
password = 'admin123'
first_name = 'Admin'
last_name = 'User'

# Check if admin already exists
if User.objects.filter(username=username).exists():
    print(f"Admin user '{username}' already exists!")
    admin_user = User.objects.get(username=username)
else:
    # Create superuser
    admin_user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    print(f"✅ Admin user created successfully!")

# Create or get teacher profile
profile, created = TeacherProfile.objects.get_or_create(
    user=admin_user,
    defaults={'phone': '+1234567890'}
)

if created:
    print(f"✅ Teacher profile created for admin")
else:
    print(f"ℹ️  Teacher profile already exists for admin")

print("\n" + "="*50)
print("ADMIN CREDENTIALS")
print("="*50)
print(f"Username: {username}")
print(f"Password: {password}")
print(f"Email: {email}")
print("="*50)
print("\nYou can now login at: http://localhost:8000/login")
print("Or React frontend at: http://localhost:5173/login")
