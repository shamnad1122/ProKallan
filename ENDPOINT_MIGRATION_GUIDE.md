# Endpoint Migration Guide - Old vs New

## ⚠️ Important: Use API Endpoints for React

The backend has **two sets of endpoints**:
1. **Old template-based endpoints** - Return HTML (for legacy Django templates)
2. **New API endpoints** - Return JSON (for React frontend)

**For your React frontend, ALWAYS use the `/api/` endpoints!**

## Endpoint Comparison

### Authentication

| Old (HTML) ❌ | New (JSON) ✅ | Method | Purpose |
|--------------|--------------|--------|---------|
| `/login/addlogin` | `/api/auth/login/` | POST | Login |
| `/logout/` | `/api/auth/logout/` | POST | Logout |
| `/register/teacher/` | `/api/auth/register/` | POST | Register |
| N/A | `/api/auth/user/` | GET | Get current user |
| N/A | `/api/csrf/` | GET | Get CSRF token |

### Profile

| Old (HTML) ❌ | New (JSON) ✅ | Method | Purpose |
|--------------|--------------|--------|---------|
| `/profile/` | `/api/auth/user/` | GET | View profile |
| `/profile/edit/` | `/api/profile/update/` | PUT | Update profile |
| `/profile/change-password/` | `/api/profile/change-password/` | POST | Change password |

### Malpractice Logs

| Old (HTML) ❌ | New (JSON) ✅ | Method | Purpose |
|--------------|--------------|--------|---------|
| `/malpractice_log/` | `/api/malpractice-logs/` | GET | Get logs |
| `/review_malpractice/` | `/api/malpractice-logs/review/` | POST | Review log |

### Lecture Halls

| Old (HTML) ❌ | New (JSON) ✅ | Method | Purpose |
|--------------|--------------|--------|---------|
| `/manage-lecture-halls/` | `/api/lecture-halls/` | GET | Get halls |
| `/manage-lecture-halls/` (POST) | `/api/lecture-halls/add/` | POST | Add hall |
| `/manage-lecture-halls/` (POST) | `/api/lecture-halls/assign/` | POST | Assign teacher |

### Teachers

| Old (HTML) ❌ | New (JSON) ✅ | Method | Purpose |
|--------------|--------------|--------|---------|
| `/view_teachers/` | `/api/teachers/` | GET | Get teachers |

### Camera Control

| Old (HTML) ❌ | New (JSON) ✅ | Method | Purpose |
|--------------|--------------|--------|---------|
| `/trigger_camera_scripts/` | `/api/cameras/start/` | POST | Start cameras |
| `/stop_camera_scripts/` | `/api/cameras/stop/` | POST | Stop cameras |

## Example: Login Flow

### ❌ Wrong (Old Endpoint)
```typescript
// This returns HTML, not JSON!
const response = await fetch('http://localhost:8000/login/addlogin', {
  method: 'POST',
  body: JSON.stringify({ username, password })
});
// Response: HTML page (not usable in React)
```

### ✅ Correct (New API Endpoint)
```typescript
// This returns JSON
const response = await authAPI.login(username, password);
// Response: { success: true, user: {...} }
```

## Frontend API Client Usage

The `frontend/src/lib/api.ts` file already has the correct endpoints configured:

```typescript
import { authAPI, malpracticeAPI, lectureHallAPI, teacherAPI, cameraAPI } from '@/lib/api';

// Login
const response = await authAPI.login('admin', 'password');

// Get current user
const user = await authAPI.getCurrentUser();

// Get malpractice logs
const logs = await malpracticeAPI.getLogs({ review: 'not_reviewed' });

// Get lecture halls
const halls = await lectureHallAPI.getAll();

// Start cameras (admin only)
await cameraAPI.start();
```

## Response Format Comparison

### Old Endpoint Response (HTML)
```
GET /profile/

<!DOCTYPE html>
<html>
  <head>...</head>
  <body>
    <div class="profile-container">...</div>
  </body>
</html>
```

### New API Endpoint Response (JSON)
```
GET /api/auth/user/

{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@detectsus.local",
    "first_name": "Admin",
    "last_name": "User",
    "is_admin": true
  }
}
```

## Testing Endpoints

### Test with curl
```bash
# Wrong - returns HTML
curl http://localhost:8000/profile/

# Correct - returns JSON
curl http://localhost:8000/api/auth/user/ \
  -H "Cookie: sessionid=..."
```

### Test with Swagger UI
Open http://localhost:8000/swagger/ to test all API endpoints interactively.

### Test with Python
```python
python test_correct_endpoints.py
```

## Common Mistakes

### ❌ Mistake 1: Using old login endpoint
```typescript
fetch('http://localhost:8000/login/addlogin', ...)
```
**Fix:** Use `/api/auth/login/`

### ❌ Mistake 2: Using old profile endpoint
```typescript
fetch('http://localhost:8000/profile/', ...)
```
**Fix:** Use `/api/auth/user/`

### ❌ Mistake 3: Mixing old and new endpoints
```typescript
await fetch('/api/auth/login/', ...)  // ✓ Correct
await fetch('/profile/', ...)          // ✗ Wrong
```
**Fix:** Use `/api/` prefix for all endpoints

## Why Two Sets of Endpoints?

The old endpoints are kept for **backward compatibility** with the legacy Django template-based frontend. They will continue to work for:
- Direct browser access
- Django admin panel
- Legacy integrations

But for your **React frontend**, always use the new `/api/` endpoints that return JSON.

## Quick Reference

**Base URL:** `http://localhost:8000`

**API Prefix:** `/api/`

**All API Endpoints:**
```
/api/csrf/                          GET
/api/auth/login/                    POST
/api/auth/logout/                   POST
/api/auth/register/                 POST
/api/auth/user/                     GET
/api/profile/update/                PUT
/api/profile/change-password/       POST
/api/malpractice-logs/              GET
/api/malpractice-logs/review/       POST
/api/lecture-halls/                 GET
/api/lecture-halls/add/             POST
/api/lecture-halls/assign/          POST
/api/teachers/                      GET
/api/cameras/start/                 POST
/api/cameras/stop/                  POST
```

## Documentation

- **Swagger UI:** http://localhost:8000/swagger/
- **ReDoc:** http://localhost:8000/redoc/
- **OpenAPI Schema:** http://localhost:8000/swagger.json

## Summary

✅ **DO:** Use `/api/` endpoints for React
✅ **DO:** Use the API client in `frontend/src/lib/api.ts`
✅ **DO:** Test with Swagger UI
✅ **DO:** Expect JSON responses

❌ **DON'T:** Use old template-based endpoints
❌ **DON'T:** Expect JSON from `/profile/`, `/login/`, etc.
❌ **DON'T:** Mix old and new endpoints

---

**Remember:** All React API calls should go to `/api/*` endpoints!
