# DetectSus Backend API - Quick Reference

## Start Servers

```bash
# Backend (Terminal 1)
python manage.py runserver

# Frontend (Terminal 2)
cd frontend && npm run dev
```

## Test API

```bash
python test_api.py
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/csrf/` | Get CSRF token | No |
| POST | `/api/auth/login/` | Login | No |
| POST | `/api/auth/logout/` | Logout | Yes |
| POST | `/api/auth/register/` | Register teacher | No |
| GET | `/api/auth/user/` | Get current user | Yes |
| PUT | `/api/profile/update/` | Update profile | Yes |
| POST | `/api/profile/change-password/` | Change password | Yes |
| GET | `/api/malpractice-logs/` | Get logs | Yes |
| POST | `/api/malpractice-logs/review/` | Review log | Admin |
| GET | `/api/lecture-halls/` | Get halls | Yes |
| POST | `/api/lecture-halls/add/` | Add hall | Admin |
| POST | `/api/lecture-halls/assign/` | Assign teacher | Admin |
| GET | `/api/teachers/` | Get teachers | Admin |
| POST | `/api/cameras/start/` | Start cameras | Admin |
| POST | `/api/cameras/stop/` | Stop cameras | Admin |

## Frontend Usage

```typescript
import { authAPI, malpracticeAPI, lectureHallAPI, teacherAPI, cameraAPI, profileAPI } from '@/lib/api';

// Login
await authAPI.login('username', 'password');

// Get logs
const { data } = await malpracticeAPI.getLogs({ review: 'not_reviewed' });

// Review log (admin)
await malpracticeAPI.review(logId, 'yes');

// Get halls
const { data } = await lectureHallAPI.getAll();

// Start cameras (admin)
await cameraAPI.start();
```

## Filter Parameters

### Malpractice Logs
- `date` - Filter by date (YYYY-MM-DD)
- `time` - 'FN' or 'AN'
- `malpractice_type` - Type of malpractice
- `building` - Building name
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

## Response Format

```json
{
  "success": true,
  "data": { ... },
  "message": "Success message"
}
```

## Error Format

```json
{
  "success": false,
  "error": "Error message"
}
```

## Environment Variables

Create `.env` in project root:
```
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
```

## Common Commands

```bash
# Check for issues
python manage.py check

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python create_admin.py

# Collect static files
python manage.py collectstatic

# Run tests
python test_api.py
```

## File Structure

```
app/
├── api_views.py      # API endpoints
├── api_urls.py       # API routing
├── views.py          # Legacy views
├── urls.py           # Main routing
├── models.py         # Database models
├── utils.py          # Camera control
└── settings.py       # Configuration

frontend/
└── src/
    └── lib/
        └── api.ts    # API client

ML/
├── front.py          # Front camera
├── top.py            # Top camera
└── ...               # Other scripts
```

## Documentation

- **API_BACKEND_SETUP.md** - Complete backend guide
- **FRONTEND_API_GUIDE.md** - Frontend integration
- **REUSE_BACKEND_SUMMARY.md** - What was done

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS error | Check `CORS_ALLOWED_ORIGINS` in settings.py |
| 401 error | User not logged in, call login first |
| 403 error | CSRF token missing, refresh page |
| 404 error | Check endpoint URL and backend running |
| Import error | Install: `pip install -r requirements.txt` |

## Key Points

✅ ML scripts unchanged - work as before
✅ Database schema intact - same models
✅ Camera control via API - SSH/local execution
✅ Notifications automatic - email/SMS on approval
✅ Session-based auth - no JWT needed
✅ CORS configured - React frontend ready
✅ All endpoints tested - production ready

## URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/
- Admin Panel: http://localhost:8000/admin/
- Media Files: http://localhost:8000/media/

---

**Ready to use!** Start both servers and begin development.
