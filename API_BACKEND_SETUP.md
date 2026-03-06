# DetectSus API Backend Setup

## Overview
The Django backend has been configured as a complete REST API for the React frontend while keeping all ML scripts and database schema intact. The backend serves as the data layer and camera control system.

## What Was Done

### 1. Created API Layer (`app/api_views.py`)
Complete JSON API endpoints covering all functionality:

**Authentication**
- `POST /api/auth/login/` - Login with username/password
- `POST /api/auth/logout/` - Logout current user
- `POST /api/auth/register/` - Register new teacher
- `GET /api/auth/user/` - Get current user info
- `GET /api/csrf/` - Get CSRF token

**Profile Management**
- `PUT /api/profile/update/` - Update user profile
- `POST /api/profile/change-password/` - Change password

**Malpractice Logs**
- `GET /api/malpractice-logs/` - Get logs with filters (date, time, building, faculty, review status)
- `POST /api/malpractice-logs/review/` - Review and approve/reject logs (admin only)

**Lecture Halls**
- `GET /api/lecture-halls/` - Get all halls with filters
- `POST /api/lecture-halls/add/` - Add new hall (admin only)
- `POST /api/lecture-halls/assign/` - Assign teacher to hall (admin only)

**Teachers**
- `GET /api/teachers/` - Get all teachers (admin only)

**Camera Control**
- `POST /api/cameras/start/` - Start ML detection scripts (admin only)
- `POST /api/cameras/stop/` - Stop all running scripts (admin only)

### 2. Updated URL Configuration
- Created `app/api_urls.py` for API routes
- Updated `app/urls.py` to include API routes under `/api/` prefix
- Kept legacy template-based views for backward compatibility

### 3. Enhanced Frontend API Client (`frontend/src/lib/api.ts`)
Added organized API functions:
- `authAPI` - Authentication operations
- `profileAPI` - Profile management
- `malpracticeAPI` - Malpractice log operations
- `lectureHallAPI` - Lecture hall management
- `teacherAPI` - Teacher operations
- `cameraAPI` - Camera control

### 4. CORS & Security Configuration
Already configured in `app/settings.py`:
- CORS enabled for React frontend (localhost:5173)
- CSRF protection with cookie-based tokens
- Session-based authentication
- Credentials support for cross-origin requests

### 5. Dependencies
Added `django-cors-headers==4.6.0` to `requirements.txt`

## Architecture

```
┌─────────────────┐
│  React Frontend │
│  (Port 5173)    │
└────────┬────────┘
         │ HTTP/JSON
         │ /api/*
         ▼
┌─────────────────┐
│ Django Backend  │
│  (Port 8000)    │
├─────────────────┤
│ • API Views     │
│ • Auth/Session  │
│ • CORS/CSRF     │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌────────┐ ┌─────┐  ┌────────┐
│Database│ │Media│  │ML      │
│(SQLite)│ │Files│  │Scripts │
└────────┘ └─────┘  └────────┘
```

## ML Scripts Integration
The ML detection scripts remain unchanged and continue to:
1. Write detection records to `MalpraticeDetection` table
2. Save proof videos to `media/` directory
3. Run via SSH or locally through Django's camera control endpoints

## Database Schema
No changes to existing models:
- `User` (Django built-in)
- `TeacherProfile` - Teacher info and phone
- `LectureHall` - Hall assignments
- `MalpraticeDetection` - Detection logs with proof videos

## How to Use

### Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations (if needed)
python manage.py migrate

# Create admin user (if not exists)
python create_admin.py

# Start Django server
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

### Testing API Endpoints
```bash
# Get CSRF token
curl http://localhost:8000/api/csrf/

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get malpractice logs
curl http://localhost:8000/api/malpractice-logs/ \
  -H "Cookie: sessionid=<session_id>"
```

## API Response Format

All endpoints return JSON with consistent structure:

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

## Authentication Flow

1. Frontend calls `GET /api/csrf/` to get CSRF token
2. Frontend stores token in cookie
3. User submits login form
4. Frontend calls `POST /api/auth/login/` with credentials
5. Backend creates session, returns user data
6. Frontend stores session cookie automatically
7. All subsequent requests include session cookie + CSRF token

## Media Files
Proof videos are served via Django's media URL:
- Backend: `/media/proof_videos/video.mp4`
- Frontend receives: `http://localhost:8000/media/proof_videos/video.mp4`

## Camera Control Flow

**Start Cameras:**
1. Admin clicks "Start Cameras" in frontend
2. Frontend calls `POST /api/cameras/start/`
3. Backend spawns ML script threads (local or SSH)
4. Scripts run continuously, writing to DB
5. Returns success immediately

**Stop Cameras:**
1. Admin clicks "Stop Cameras"
2. Frontend calls `POST /api/cameras/stop/`
3. Backend terminates all running script processes
4. Returns success after cleanup

## Notifications
When admin approves malpractice:
1. Email sent to assigned teacher
2. SMS sent via Twilio (if phone configured)
3. Teacher can view proof video in portal

## Deployment Considerations

### Production Settings
Update `app/settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
CORS_ALLOWED_ORIGINS = ['https://your-frontend.com']
CSRF_TRUSTED_ORIGINS = ['https://your-frontend.com']

# Use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASS'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}
```

### Environment Variables
Required in `.env`:
```
SECRET_KEY=your-secret-key
DEBUG=False
DB_NAME=detectsus
DB_USER=dbuser
DB_PASS=dbpass
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
```

## Extending the API

### Add New Endpoint
1. Add function to `app/api_views.py`:
```python
@require_http_methods(["GET"])
@login_required
def api_my_endpoint(request):
    return JsonResponse({'success': True, 'data': []})
```

2. Add route to `app/api_urls.py`:
```python
path('my-endpoint/', api_views.api_my_endpoint, name='api_my_endpoint'),
```

3. Add frontend function to `frontend/src/lib/api.ts`:
```typescript
export const myAPI = {
  getData: () => api.get('/api/my-endpoint/'),
};
```

## Troubleshooting

**CORS Errors:**
- Check `CORS_ALLOWED_ORIGINS` in settings.py
- Ensure frontend URL matches exactly (including port)

**CSRF Errors:**
- Call `/api/csrf/` before any POST requests
- Ensure `withCredentials: true` in axios config
- Check CSRF token is in cookie and header

**Session Not Persisting:**
- Verify `withCredentials: true` in frontend
- Check `CORS_ALLOW_CREDENTIALS = True` in backend
- Ensure same-site cookie settings

**Media Files Not Loading:**
- Check `MEDIA_URL` and `MEDIA_ROOT` in settings
- Verify static file serving in urls.py
- In production, use nginx/apache for media files

## Summary

The Django backend now functions as a complete REST API while maintaining:
- ✅ All ML detection scripts unchanged
- ✅ Database schema intact
- ✅ Camera control via SSH/local execution
- ✅ Email/SMS notifications
- ✅ Media file serving
- ✅ Session-based authentication
- ✅ CORS configured for React frontend
- ✅ Backward compatible with legacy views

The React frontend can now consume all backend functionality through clean JSON APIs at `/api/*` endpoints.
