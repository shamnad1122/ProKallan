# API Endpoints Cheatsheet for React Frontend

## 🎯 Quick Rule: Always Use `/api/` Prefix!

```
❌ http://localhost:8000/profile/          → Returns HTML
✅ http://localhost:8000/api/auth/user/    → Returns JSON
```

## 📋 Complete Endpoint List

### 🔐 Authentication

```typescript
// Get CSRF Token
GET /api/csrf/
Response: { csrfToken: "..." }

// Login
POST /api/auth/login/
Body: { username: "admin", password: "pass" }
Response: { success: true, user: {...} }

// Logout
POST /api/auth/logout/
Response: { success: true, message: "Logged out" }

// Register
POST /api/auth/register/
Body: { username, email, password, first_name, last_name, phone }
Response: { success: true, user: {...} }

// Get Current User
GET /api/auth/user/
Response: { success: true, user: {...} }
```

### 👤 Profile

```typescript
// Update Profile
PUT /api/profile/update/
Body: { first_name, last_name, email, phone }
Response: { success: true, message: "Profile updated" }

// Change Password
POST /api/profile/change-password/
Body: { old_password, new_password }
Response: { success: true, message: "Password changed" }
```

### 📝 Malpractice Logs

```typescript
// Get Logs (with filters)
GET /api/malpractice-logs/?review=not_reviewed&date=2024-03-15
Response: { success: true, logs: [...], count: 5 }

// Review Log (Admin only)
POST /api/malpractice-logs/review/
Body: { id: 1, decision: "yes" }
Response: { success: true, message: "Review completed" }
```

### 🏫 Lecture Halls

```typescript
// Get All Halls
GET /api/lecture-halls/?building=MAIN&assigned=assigned
Response: { success: true, halls: [...], buildings: [...] }

// Add Hall (Admin only)
POST /api/lecture-halls/add/
Body: { hall_name: "LH1", building: "MAIN" }
Response: { success: true, hall: {...} }

// Assign Teacher (Admin only)
POST /api/lecture-halls/assign/
Body: { hall_id: 1, teacher_id: 2 }
Response: { success: true, message: "Teacher assigned" }
```

### 👨‍🏫 Teachers

```typescript
// Get All Teachers (Admin only)
GET /api/teachers/?assigned=assigned&building=MAIN
Response: { success: true, teachers: [...] }
```

### 📹 Camera Control

```typescript
// Start Cameras (Admin only)
POST /api/cameras/start/
Response: { success: true, message: "Cameras started" }

// Stop Cameras (Admin only)
POST /api/cameras/stop/
Response: { success: true, message: "Cameras stopped" }
```

## 💻 Frontend Usage Examples

### Using the API Client

```typescript
import { 
  authAPI, 
  profileAPI, 
  malpracticeAPI, 
  lectureHallAPI, 
  teacherAPI, 
  cameraAPI 
} from '@/lib/api';

// Login
const { data } = await authAPI.login('admin', 'password');
console.log(data.user);

// Get current user
const { data } = await authAPI.getCurrentUser();
console.log(data.user);

// Get malpractice logs
const { data } = await malpracticeAPI.getLogs({ 
  review: 'not_reviewed',
  date: '2024-03-15'
});
console.log(data.logs);

// Update profile
await profileAPI.update({
  first_name: 'John',
  last_name: 'Doe',
  email: 'john@example.com'
});

// Change password
await profileAPI.changePassword('oldpass', 'newpass');

// Get lecture halls
const { data } = await lectureHallAPI.getAll({ building: 'MAIN' });
console.log(data.halls);

// Add lecture hall (admin)
await lectureHallAPI.add('LH1', 'MAIN');

// Assign teacher (admin)
await lectureHallAPI.assignTeacher(1, 2);

// Get teachers (admin)
const { data } = await teacherAPI.getAll();
console.log(data.teachers);

// Start cameras (admin)
await cameraAPI.start();

// Stop cameras (admin)
await cameraAPI.stop();
```

### Direct Fetch Example

```typescript
// Login
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  credentials: 'include',
  body: JSON.stringify({ username: 'admin', password: 'pass' })
});
const data = await response.json();
console.log(data.user);
```

## 🔍 Filter Parameters

### Malpractice Logs
- `date` - Filter by date (YYYY-MM-DD)
- `time` - 'FN' (forenoon) or 'AN' (afternoon)
- `malpractice_type` - Type of malpractice
- `building` - Building name ('MAIN', 'KE', 'PG')
- `q` - Search hall name
- `faculty` - Teacher ID
- `assigned` - 'assigned' or 'unassigned'
- `review` - 'reviewed' or 'not_reviewed'

### Lecture Halls
- `q` - Search hall name
- `building` - Building name
- `assigned` - 'assigned' or 'unassigned'

### Teachers
- `assigned` - 'assigned' or 'unassigned'
- `building` - Building name

## 📦 Response Format

All API endpoints return consistent JSON:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message"
}
```

## 🚨 Common Errors

### 401 Unauthorized
```json
{ "success": false, "error": "Authentication required" }
```
**Fix:** Login first using `/api/auth/login/`

### 403 Forbidden
```json
{ "success": false, "error": "Admin access required" }
```
**Fix:** Endpoint requires admin privileges

### 400 Bad Request
```json
{ "success": false, "error": "Invalid data" }
```
**Fix:** Check request body format

### 404 Not Found
```json
{ "success": false, "error": "Resource not found" }
```
**Fix:** Check endpoint URL and resource ID

## 🔗 Quick Links

- **Swagger UI:** http://localhost:8000/swagger/
- **ReDoc:** http://localhost:8000/redoc/
- **API Base:** http://localhost:8000/api/
- **Frontend:** http://localhost:5173/

## 📚 Documentation Files

- `ENDPOINT_MIGRATION_GUIDE.md` - Old vs New endpoints
- `FRONTEND_API_GUIDE.md` - Detailed integration guide
- `API_BACKEND_SETUP.md` - Backend architecture
- `SWAGGER_SETUP.md` - Swagger usage

## ✅ Checklist

Before making API calls:
- [ ] Using `/api/` prefix
- [ ] Sending CSRF token for POST/PUT requests
- [ ] Including credentials (session cookie)
- [ ] Handling success/error responses
- [ ] Checking user permissions (admin vs teacher)

## 🎯 Remember

1. **Always use `/api/` endpoints** for React
2. **Include CSRF token** for POST/PUT/DELETE
3. **Send credentials** with requests (`withCredentials: true`)
4. **Check response.data.success** before using data
5. **Handle errors** gracefully

---

**Need help?** Check Swagger UI at http://localhost:8000/swagger/
