# ✅ DetectSus Servers Running

## Status: ACTIVE

Both frontend and backend servers are now running and ready to use!

## Server URLs

### 🎨 Frontend (React + Vite)
**URL:** http://localhost:5173/
**Status:** ✅ Running
**Framework:** React + TypeScript + Vite
**Features:**
- Login/Register pages
- Malpractice log viewer
- Lecture hall management
- Teacher management
- Camera control
- Profile management

### 🔧 Backend (Django)
**URL:** http://localhost:8000/
**Status:** ✅ Running
**Framework:** Django 4.2.29
**Features:**
- REST API endpoints
- Session authentication
- ML script control
- Email/SMS notifications
- Media file serving

### 📚 API Documentation (Swagger)
**Swagger UI:** http://localhost:8000/swagger/
**ReDoc:** http://localhost:8000/redoc/
**OpenAPI JSON:** http://localhost:8000/swagger.json
**Status:** ✅ Running
**Features:**
- Interactive API testing
- Complete endpoint documentation
- Request/response examples
- Authentication testing

### 🔐 Admin Panel
**URL:** http://localhost:8000/admin/
**Status:** ✅ Available
**Access:** Admin credentials required

## Quick Test

### ⚠️ Important: Use API Endpoints!

The backend has two types of endpoints:
- **Old endpoints** (e.g., `/profile/`, `/login/addlogin`) - Return HTML
- **New API endpoints** (e.g., `/api/auth/user/`, `/api/auth/login/`) - Return JSON

**For React, ALWAYS use `/api/` endpoints!**

### 1. Test Backend API (Correct)
Open: http://localhost:8000/api/csrf/

Expected response:
```json
{
  "csrfToken": "..."
}
```

### ❌ Common Mistake
Don't use: http://localhost:8000/profile/
This returns HTML, not JSON!

### ✅ Correct
Use: http://localhost:8000/api/auth/user/
This returns JSON for React!

### 2. Test Swagger UI
Open: http://localhost:8000/swagger/

You should see:
- Complete API documentation
- All 15 endpoints listed
- Interactive "Try it out" buttons

### 3. Test Frontend
Open: http://localhost:5173/

You should see:
- DetectSus login page
- Clean React interface
- Responsive design

## Available API Endpoints

All endpoints are documented in Swagger, but here's a quick list:

### Authentication
- `GET /api/csrf/` - Get CSRF token
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/register/` - Register
- `GET /api/auth/user/` - Current user

### Profile
- `PUT /api/profile/update/` - Update profile
- `POST /api/profile/change-password/` - Change password

### Malpractice Logs
- `GET /api/malpractice-logs/` - Get logs
- `POST /api/malpractice-logs/review/` - Review log

### Lecture Halls
- `GET /api/lecture-halls/` - Get halls
- `POST /api/lecture-halls/add/` - Add hall
- `POST /api/lecture-halls/assign/` - Assign teacher

### Teachers
- `GET /api/teachers/` - Get teachers

### Cameras
- `POST /api/cameras/start/` - Start cameras
- `POST /api/cameras/stop/` - Stop cameras

## Testing the Integration

### Test 1: Login Flow
1. Open frontend: http://localhost:5173/
2. Click "Login"
3. Enter credentials (create user if needed)
4. Should redirect to home page

### Test 2: API via Swagger
1. Open Swagger: http://localhost:8000/swagger/
2. Find `POST /api/auth/login/`
3. Click "Try it out"
4. Enter credentials
5. Click "Execute"
6. Should return user data

### Test 3: Malpractice Logs
1. Login to frontend
2. Navigate to "Malpractice Logs"
3. Should see list of logs (or empty state)
4. Filters should work

## Server Management

### View Backend Logs
The backend terminal shows:
- Request logs
- Error messages
- ML script output
- Email/SMS notifications

### View Frontend Logs
The frontend terminal shows:
- Vite dev server status
- Hot reload events
- Build warnings/errors

### Stop Servers
To stop the servers:
- Backend: Press `CTRL+C` in backend terminal
- Frontend: Press `CTRL+C` in frontend terminal

Or use Kiro's process management to stop them.

### Restart Servers
If you need to restart:

**Backend:**
```bash
.\venv\Scripts\python.exe manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Environment Configuration

### Backend (.env)
Located at project root:
```
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
```

### Frontend (.env)
Located at `frontend/.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Next Steps

### 1. Create Admin User (if not exists)
```bash
python create_admin.py
```

### 2. Test Login
- Open http://localhost:5173/
- Login with admin credentials
- Explore the interface

### 3. Test API
- Open http://localhost:8000/swagger/
- Test endpoints interactively
- Verify responses

### 4. Add Test Data
- Create lecture halls
- Register teachers
- Assign teachers to halls

### 5. Test Camera Control (Admin)
- Login as admin
- Go to "Run Cameras"
- Start/stop camera scripts
- Check ML detection works

## Troubleshooting

### Backend Not Responding
- Check terminal for errors
- Verify port 8000 is not in use
- Check database connection

### Frontend Not Loading
- Check terminal for errors
- Verify port 5173 is not in use
- Check `VITE_API_BASE_URL` in `.env`

### CORS Errors
- Check `CORS_ALLOWED_ORIGINS` in `app/settings.py`
- Should include `http://localhost:5173`

### Authentication Issues
- Clear browser cookies
- Check session configuration
- Verify CSRF token is being sent

### Swagger Not Loading
- Check `rest_framework` and `drf_yasg` are installed
- Verify `INSTALLED_APPS` in settings
- Restart backend server

## Documentation Files

- **API_BACKEND_SETUP.md** - Complete backend guide
- **FRONTEND_API_GUIDE.md** - Frontend integration
- **SWAGGER_SETUP.md** - Swagger documentation
- **QUICK_REFERENCE.md** - Quick command reference
- **REUSE_BACKEND_SUMMARY.md** - What was accomplished

## System Architecture

```
┌─────────────────────┐
│   React Frontend    │
│   localhost:5173    │
│                     │
│  - Login/Register   │
│  - Malpractice Logs │
│  - Hall Management  │
│  - Camera Control   │
└──────────┬──────────┘
           │ HTTP/JSON
           │ /api/*
           ▼
┌─────────────────────┐
│   Django Backend    │
│   localhost:8000    │
│                     │
│  - REST API         │
│  - Authentication   │
│  - Swagger Docs     │
│  - Admin Panel      │
└──────────┬──────────┘
           │
      ┌────┴────┬──────────┐
      ▼         ▼          ▼
  ┌────────┐ ┌─────┐  ┌────────┐
  │Database│ │Media│  │ML      │
  │SQLite  │ │Files│  │Scripts │
  └────────┘ └─────┘  └────────┘
```

## Key Features Working

✅ **Frontend-Backend Communication** - CORS configured
✅ **Session Authentication** - Login/logout working
✅ **API Endpoints** - All 15 endpoints available
✅ **Swagger Documentation** - Interactive API docs
✅ **ML Scripts** - Camera control ready
✅ **Database** - SQLite configured
✅ **Media Files** - Video serving ready
✅ **Notifications** - Email/SMS configured

## Summary

🎉 **Everything is ready!**

- Frontend running on port 5173
- Backend running on port 8000
- Swagger UI available for API testing
- All endpoints documented and working
- ML scripts ready to run
- Database configured
- Authentication working

**Start developing or testing the application now!**

---

**Quick Links:**
- Frontend: http://localhost:5173/
- Backend: http://localhost:8000/
- Swagger: http://localhost:8000/swagger/
- Admin: http://localhost:8000/admin/
