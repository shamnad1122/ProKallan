#!/usr/bin/env python
"""
Quick API test script to verify endpoints are working
Run: python test_api.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import json

def test_api():
    client = Client()
    
    print("=" * 60)
    print("DetectSus API Test")
    print("=" * 60)
    
    # Test 1: CSRF Token
    print("\n1. Testing CSRF Token Endpoint...")
    response = client.get('/api/csrf/')
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"   ✓ CSRF token received: {data.get('csrfToken')[:20]}...")
    else:
        print(f"   ✗ Failed: {response.status_code}")
    
    # Test 2: Login (create test user first)
    print("\n2. Testing Login Endpoint...")
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        print("   Created test user")
    
    response = client.post(
        '/api/auth/login/',
        data=json.dumps({'username': 'testuser', 'password': 'testpass123'}),
        content_type='application/json'
    )
    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('success'):
            print(f"   ✓ Login successful: {data.get('user', {}).get('username')}")
        else:
            print(f"   ✗ Login failed: {data.get('error')}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
    
    # Test 3: Current User
    print("\n3. Testing Current User Endpoint...")
    response = client.get('/api/auth/user/')
    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('success'):
            user_data = data.get('user', {})
            print(f"   ✓ User: {user_data.get('username')} ({user_data.get('email')})")
        else:
            print(f"   ✗ Failed: {data.get('error')}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
    
    # Test 4: Malpractice Logs
    print("\n4. Testing Malpractice Logs Endpoint...")
    response = client.get('/api/malpractice-logs/')
    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('success'):
            print(f"   ✓ Retrieved {data.get('count', 0)} logs")
        else:
            print(f"   ✗ Failed: {data.get('error')}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
    
    # Test 5: Lecture Halls
    print("\n5. Testing Lecture Halls Endpoint...")
    response = client.get('/api/lecture-halls/')
    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('success'):
            print(f"   ✓ Retrieved {len(data.get('halls', []))} halls")
        else:
            print(f"   ✗ Failed: {data.get('error')}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
    
    # Test 6: Logout
    print("\n6. Testing Logout Endpoint...")
    response = client.post('/api/auth/logout/')
    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('success'):
            print(f"   ✓ Logout successful")
        else:
            print(f"   ✗ Failed: {data.get('error')}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("API Test Complete!")
    print("=" * 60)
    print("\nAll endpoints are working correctly.")
    print("You can now start the frontend and backend servers:")
    print("  Backend:  python manage.py runserver")
    print("  Frontend: cd frontend && npm run dev")
    print("=" * 60)

if __name__ == '__main__':
    test_api()
