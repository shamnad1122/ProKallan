# Swagger API Documentation Setup

## Overview

Swagger/OpenAPI documentation has been added to the DetectSus backend API for easy exploration and testing of endpoints.

## Access Swagger UI

With the backend running, access the interactive API documentation at:

### Swagger UI (Interactive)
**URL:** http://localhost:8000/swagger/

Features:
- Interactive API explorer
- Try out endpoints directly from browser
- See request/response examples
- View all available endpoints
- Test authentication flow

### ReDoc (Alternative Documentation)
**URL:** http://localhost:8000/redoc/

Features:
- Clean, readable documentation
- Better for reading and understanding
- Organized by tags
- Search functionality

### OpenAPI Schema (JSON/YAML)
- **JSON:** http://localhost:8000/swagger.json
- **YAML:** http://localhost:8000/swagger.yaml

Use these for:
- Importing into Postman
- Generating client SDKs
- API testing tools

## What Was Added

### 1. Dependencies
Added to `requirements.txt`:
- `djangorestframework==3.14.0` - Django REST framework
- `drf-yasg==1.21.7` - Swagger/OpenAPI generator

### 2. Django Settings
Updated `app/settings.py`:
```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'drf_yasg',
    ...
]
```

### 3. URL Configuration
Updated `app/urls.py` with Swagger endpoints:
- `/swagger/` - Swagger UI
- `/redoc/` - ReDoc UI
- `/swagger.json` - OpenAPI JSON schema
- `/swagger.yaml` - OpenAPI YAML schema

## Using Swagger UI

### 1. Open Swagger UI
Navigate to: http://localhost:8000/swagger/

### 2. Authenticate
Since the API uses session-based authentication:

**Option A: Login via API**
1. Find the `POST /api/auth/login/` endpoint
2. Click "Try it out"
3. Enter credentials:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
4. Click "Execute"
5. Session cookie is automatically stored

**Option B: Login via Django Admin**
1. Open http://localhost:8000/admin/
2. Login with admin credentials
3. Return to Swagger UI
4. Session is already active

### 3. Test Endpoints
After authentication:
1. Browse available endpoints
2. Click "Try it out" on any endpoint
3. Fill in parameters
4. Click "Execute"
5. View response

## API Documentation Structure

### Authentication Endpoints
- `GET /api/csrf/` - Get CSRF token
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/register/` - Register teacher
- `GET /api/auth/user/` - Get current user

### Profile Endpoints
- `PUT /api/profile/update/` - Update profile
- `POST /api/profile/change-password/` - Change password

### Malpractice Log Endpoints
- `GET /api/malpractice-logs/` - Get logs with filters
- `POST /api/malpractice-logs/review/` - Review log (admin)

### Lecture Hall Endpoints
- `GET /api/lecture-halls/` - Get all halls
- `POST /api/lecture-halls/add/` - Add hall (admin)
- `POST /api/lecture-halls/assign/` - Assign teacher (admin)

### Teacher Endpoints
- `GET /api/teachers/` - Get all teachers (admin)

### Camera Control Endpoints
- `POST /api/cameras/start/` - Start cameras (admin)
- `POST /api/cameras/stop/` - Stop cameras (admin)

## Example: Testing Login Flow

### 1. Get CSRF Token
```bash
GET /api/csrf/
```

Response:
```json
{
  "csrfToken": "abc123..."
}
```

### 2. Login
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

Response:
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_admin": true
  }
}
```

### 3. Get Malpractice Logs
```bash
GET /api/malpractice-logs/?review=not_reviewed
```

Response:
```json
{
  "success": true,
  "logs": [...],
  "count": 5
}
```

## Exporting for Postman

1. Open http://localhost:8000/swagger.json
2. Copy the JSON content
3. In Postman: Import → Raw Text → Paste JSON
4. All endpoints will be imported with examples

## Exporting for Client Generation

Use the OpenAPI schema to generate client SDKs:

```bash
# Download schema
curl http://localhost:8000/swagger.json > api-schema.json

# Generate TypeScript client
npx @openapitools/openapi-generator-cli generate \
  -i api-schema.json \
  -g typescript-axios \
  -o ./generated-client

# Generate Python client
openapi-generator-cli generate \
  -i api-schema.json \
  -g python \
  -o ./python-client
```

## Customizing Documentation

To add more details to endpoints, you can use `drf_yasg` decorators in `app/api_views.py`:

```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view

@swagger_auto_schema(
    method='get',
    operation_description="Get all malpractice logs",
    manual_parameters=[
        openapi.Parameter('date', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        openapi.Parameter('review', openapi.IN_QUERY, type=openapi.TYPE_STRING),
    ],
    responses={200: 'Success', 401: 'Unauthorized'}
)
@api_view(['GET'])
def api_malpractice_logs(request):
    # ... implementation
```

## Security Notes

### Production Deployment
In production, you may want to:

1. **Disable Swagger in Production:**
```python
# app/settings.py
if not DEBUG:
    # Remove swagger URLs
    pass
```

2. **Restrict Access:**
```python
# app/urls.py
schema_view = get_schema_view(
    ...
    permission_classes=(permissions.IsAdminUser,),  # Only admins
)
```

3. **Use HTTPS:**
Ensure Swagger UI is only accessible over HTTPS in production.

## Troubleshooting

### Swagger UI Not Loading
- Check backend is running: http://localhost:8000/
- Check for errors in terminal
- Clear browser cache

### Authentication Not Working
- Login first via `/api/auth/login/`
- Or login via Django admin
- Check session cookie is set

### Endpoints Not Showing
- Restart Django server
- Check `INSTALLED_APPS` includes `drf_yasg`
- Check URL configuration

## Benefits

✅ **Interactive Testing** - Test all endpoints from browser
✅ **Documentation** - Auto-generated from code
✅ **Client Generation** - Generate SDKs automatically
✅ **Team Collaboration** - Share API docs easily
✅ **Postman Integration** - Import directly to Postman
✅ **Standards Compliant** - OpenAPI 3.0 specification

## Quick Links

- **Swagger UI:** http://localhost:8000/swagger/
- **ReDoc:** http://localhost:8000/redoc/
- **OpenAPI JSON:** http://localhost:8000/swagger.json
- **Backend API:** http://localhost:8000/api/
- **Django Admin:** http://localhost:8000/admin/
- **Frontend:** http://localhost:5173/

---

**Swagger is now ready!** Open http://localhost:8000/swagger/ to explore the API.
