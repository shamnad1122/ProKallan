# Frontend API Integration Guide

## Quick Start

The Django backend is now a complete REST API. All endpoints are available at `/api/*`.

### Setup

1. **Backend** (Terminal 1):
```bash
python manage.py runserver
# Runs on http://localhost:8000
```

2. **Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

### Environment Variables

Create `frontend/.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Using the API in React

Import the API client:
```typescript
import { authAPI, malpracticeAPI, lectureHallAPI, teacherAPI, cameraAPI, profileAPI } from '@/lib/api';
```

### Authentication

**Login:**
```typescript
const handleLogin = async (username: string, password: string) => {
  try {
    const response = await authAPI.login(username, password);
    if (response.data.success) {
      const user = response.data.user;
      console.log('Logged in:', user);
      // User data includes: id, username, email, first_name, last_name, is_admin
    }
  } catch (error) {
    console.error('Login failed:', error);
  }
};
```

**Get Current User:**
```typescript
const fetchUser = async () => {
  try {
    const response = await authAPI.getCurrentUser();
    if (response.data.success) {
      setUser(response.data.user);
    }
  } catch (error) {
    console.error('Not authenticated');
  }
};
```

**Logout:**
```typescript
const handleLogout = async () => {
  await authAPI.logout();
  // Redirect to login
};
```

**Register:**
```typescript
const handleRegister = async (data: any) => {
  try {
    const response = await authAPI.register({
      username: data.username,
      email: data.email,
      password: data.password,
      first_name: data.firstName,
      last_name: data.lastName,
      phone: data.phone,
    });
    if (response.data.success) {
      // Registration successful
    }
  } catch (error) {
    console.error('Registration failed:', error);
  }
};
```

### Profile Management

**Update Profile:**
```typescript
const updateProfile = async (data: any) => {
  try {
    const response = await profileAPI.update({
      first_name: data.firstName,
      last_name: data.lastName,
      email: data.email,
      phone: data.phone,
    });
    if (response.data.success) {
      // Profile updated
    }
  } catch (error) {
    console.error('Update failed:', error);
  }
};
```

**Change Password:**
```typescript
const changePassword = async (oldPassword: string, newPassword: string) => {
  try {
    const response = await profileAPI.changePassword(oldPassword, newPassword);
    if (response.data.success) {
      // Password changed
    }
  } catch (error) {
    console.error('Password change failed:', error);
  }
};
```

### Malpractice Logs

**Get Logs with Filters:**
```typescript
const fetchLogs = async () => {
  try {
    const response = await malpracticeAPI.getLogs({
      date: '2024-03-15',           // Optional: filter by date
      time: 'FN',                   // Optional: 'FN' or 'AN'
      malpractice_type: 'Mobile',   // Optional: type of malpractice
      building: 'MAIN',             // Optional: building filter
      q: 'LH1',                     // Optional: search hall name
      faculty: '5',                 // Optional: teacher ID
      assigned: 'assigned',         // Optional: 'assigned' or 'unassigned'
      review: 'not_reviewed',       // Optional: 'reviewed' or 'not_reviewed'
    });
    
    if (response.data.success) {
      const logs = response.data.logs;
      // Each log has: id, date, time, malpractice, proof (video URL), 
      // is_malpractice, verified, lecture_hall, assigned_teacher
      setLogs(logs);
    }
  } catch (error) {
    console.error('Failed to fetch logs:', error);
  }
};
```

**Review Log (Admin Only):**
```typescript
const reviewLog = async (logId: number, decision: 'yes' | 'no') => {
  try {
    const response = await malpracticeAPI.review(logId, decision);
    if (response.data.success) {
      // Review completed, notifications sent
    }
  } catch (error) {
    console.error('Review failed:', error);
  }
};
```

### Lecture Halls

**Get All Halls:**
```typescript
const fetchHalls = async () => {
  try {
    const response = await lectureHallAPI.getAll({
      q: 'LH',              // Optional: search
      building: 'MAIN',     // Optional: filter by building
      assigned: 'assigned', // Optional: 'assigned' or 'unassigned'
    });
    
    if (response.data.success) {
      const halls = response.data.halls;
      const buildings = response.data.buildings;
      setHalls(halls);
      setBuildings(buildings);
    }
  } catch (error) {
    console.error('Failed to fetch halls:', error);
  }
};
```

**Add Hall (Admin Only):**
```typescript
const addHall = async (hallName: string, building: string) => {
  try {
    const response = await lectureHallAPI.add(hallName, building);
    if (response.data.success) {
      // Hall added
    }
  } catch (error) {
    console.error('Failed to add hall:', error);
  }
};
```

**Assign Teacher (Admin Only):**
```typescript
const assignTeacher = async (hallId: number, teacherId: number) => {
  try {
    const response = await lectureHallAPI.assignTeacher(hallId, teacherId);
    if (response.data.success) {
      // Teacher assigned
    }
  } catch (error) {
    console.error('Failed to assign teacher:', error);
  }
};
```

### Teachers

**Get All Teachers (Admin Only):**
```typescript
const fetchTeachers = async () => {
  try {
    const response = await teacherAPI.getAll({
      assigned: 'assigned',  // Optional: 'assigned' or 'unassigned'
      building: 'MAIN',      // Optional: filter by building
    });
    
    if (response.data.success) {
      const teachers = response.data.teachers;
      // Each teacher has: id, username, email, first_name, last_name,
      // full_name, phone, profile_picture, lecture_hall
      setTeachers(teachers);
    }
  } catch (error) {
    console.error('Failed to fetch teachers:', error);
  }
};
```

### Camera Control

**Start Cameras (Admin Only):**
```typescript
const startCameras = async () => {
  try {
    const response = await cameraAPI.start();
    if (response.data.success) {
      // ML scripts started
    }
  } catch (error) {
    console.error('Failed to start cameras:', error);
  }
};
```

**Stop Cameras (Admin Only):**
```typescript
const stopCameras = async () => {
  try {
    const response = await cameraAPI.stop();
    if (response.data.success) {
      // ML scripts stopped
    }
  } catch (error) {
    console.error('Failed to stop cameras:', error);
  }
};
```

## Data Structures

### User Object
```typescript
{
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_admin: boolean;
  phone?: string;
  profile_picture?: string;
  lecture_hall?: {
    id: number;
    building: string;
    hall_name: string;
  };
}
```

### Malpractice Log Object
```typescript
{
  id: number;
  date: string;           // ISO format: "2024-03-15"
  time: string;           // ISO format: "14:30:00"
  malpractice: string;    // e.g., "Mobile Phone", "Passing Paper"
  proof: string;          // Full URL to video file
  is_malpractice: boolean | null;
  verified: boolean;
  lecture_hall?: {
    id: number;
    building: string;
    hall_name: string;
  };
  assigned_teacher?: {
    id: number;
    username: string;
    full_name: string;
  };
}
```

### Lecture Hall Object
```typescript
{
  id: number;
  building: string;       // e.g., "MAIN", "KE", "PG"
  hall_name: string;      // e.g., "LH1", "LH2"
  assigned_teacher?: {
    id: number;
    username: string;
    full_name: string;
    email: string;
  };
}
```

### Teacher Object
```typescript
{
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone?: string;
  profile_picture?: string;
  lecture_hall?: {
    id: number;
    building: string;
    hall_name: string;
  };
}
```

## Error Handling

All API calls return consistent error format:

```typescript
try {
  const response = await someAPI.call();
  if (response.data.success) {
    // Handle success
  }
} catch (error: any) {
  if (error.response) {
    // Server responded with error
    const errorMessage = error.response.data.error;
    console.error('API Error:', errorMessage);
  } else if (error.request) {
    // Request made but no response
    console.error('Network Error');
  } else {
    // Something else happened
    console.error('Error:', error.message);
  }
}
```

## Authentication State

The API uses session-based authentication. After login:
- Session cookie is automatically stored
- All subsequent requests include the session
- No need to manually manage tokens

Check authentication:
```typescript
useEffect(() => {
  authAPI.getCurrentUser()
    .then(response => {
      if (response.data.success) {
        setUser(response.data.user);
        setIsAuthenticated(true);
      }
    })
    .catch(() => {
      setIsAuthenticated(false);
    });
}, []);
```

## Media Files

Proof videos are served directly from Django:
```typescript
// The 'proof' field in logs contains full URL
<video src={log.proof} controls />
// Example: http://localhost:8000/media/proof_videos/video_20240315_143000.mp4
```

## CORS & CSRF

Already configured! The API client automatically:
- Sends credentials with requests
- Includes CSRF token from cookies
- Handles CORS headers

## Testing

Test individual endpoints:
```bash
# Backend test
python test_api.py

# Manual test with curl
curl http://localhost:8000/api/csrf/
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## Common Issues

**401 Unauthorized:**
- User not logged in
- Session expired
- Call `authAPI.login()` first

**403 Forbidden:**
- CSRF token missing
- Call `authAPI.getCSRFToken()` first
- Or refresh the page

**404 Not Found:**
- Check endpoint URL
- Ensure backend is running

**CORS Error:**
- Check `VITE_API_BASE_URL` in `.env`
- Ensure backend CORS settings include frontend URL

## Next Steps

1. Start both servers
2. Test login flow
3. Implement remaining pages using the API
4. Add error handling and loading states
5. Test camera control (admin only)

The backend is ready to use! All ML scripts, database operations, and notifications work as before.
