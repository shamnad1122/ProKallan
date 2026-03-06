#!/usr/bin/env python
"""
Test to show the difference between old HTML endpoints and new JSON API endpoints
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.test import Client
import json

client = Client()

print("=" * 70)
print("COMPARING OLD vs NEW ENDPOINTS")
print("=" * 70)

# Login first
print("\n1. LOGIN")
print("-" * 70)
response = client.post(
    '/api/auth/login/',
    data=json.dumps({'username': 'admin', 'password': 'admin123'}),
    content_type='application/json'
)
print(f"✓ POST /api/auth/login/ (JSON API)")
print(f"  Status: {response.status_code}")
print(f"  Response: {json.dumps(json.loads(response.content), indent=2)}")

# Test OLD endpoint (returns HTML)
print("\n2. OLD ENDPOINT (Returns HTML)")
print("-" * 70)
response = client.get('/profile/')
print(f"✗ GET /profile/ (Old template-based)")
print(f"  Status: {response.status_code}")
print(f"  Content-Type: {response.get('Content-Type')}")
print(f"  Returns: HTML page (not suitable for React)")
print(f"  First 100 chars: {response.content.decode()[:100]}...")

# Test NEW endpoint (returns JSON)
print("\n3. NEW API ENDPOINT (Returns JSON)")
print("-" * 70)
response = client.get('/api/auth/user/')
print(f"✓ GET /api/auth/user/ (New JSON API)")
print(f"  Status: {response.status_code}")
print(f"  Content-Type: {response.get('Content-Type')}")
print(f"  Response: {json.dumps(json.loads(response.content), indent=2)}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("\nFor React Frontend, ALWAYS use endpoints starting with /api/")
print("\nCorrect endpoints:")
print("  ✓ /api/auth/login/")
print("  ✓ /api/auth/user/")
print("  ✓ /api/malpractice-logs/")
print("  ✓ /api/lecture-halls/")
print("\nAvoid these (they return HTML):")
print("  ✗ /login/addlogin")
print("  ✗ /profile/")
print("  ✗ /malpractice_log/")
print("=" * 70)
