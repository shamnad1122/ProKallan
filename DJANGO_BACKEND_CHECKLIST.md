# Django Backend Updates Checklist

This checklist outlines the Django backend changes needed to fully support the React frontend.

## ✅ Required Changes

### 1. CORS Configuration

Add to `app/settings.py`:

```python
# Install django-cors-headers if not already installed
# pip install django-cors-headers

INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add at the top
    'django.middleware.common.CommonMiddleware',
    # ...
]

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True  # Important for session auth
```

### 2. CSRF Configuration

Update `app/settings.py`:

```python
# Make CSRF cookie accessible to JavaScript
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# For development with different ports
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

### 3. Session Configuration

Ensure session settings in `app/settings.py`:

```python
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
```

## 🔄 API Endpoint Updates

### 1. Profile Endpoint

Create or update `/profile/` to return JSON:

```python
@login_required
def profile_api(request):
    """API endpoint for React frontend"""
    try:
        teacher_profile = request.user.teacherprofile
        profile_data = {
            'phone': teacher_profile.phone,
            'profile_picture': teacher_profile.profile_picture.url if teacher_profile.profile_picture else None,
        }
        if hasattr(teacher_profile, 'lecturehall'):
            profile_data['lecture_hall'] = {
                'id': teacher_profile.lecturehall.id,
                'hall_name': teacher_profile.lecturehall.hall_name,
                'building': teacher_profile.lecturehall.building,
            }
    except TeacherProfile.DoesNotExist:
        profile_data = None

    return JsonResponse({
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'is_superuser': request.user.is_superuser,
        },
        'profile': profile_data,
    })
```

### 2. Malpractice Log Endpoint

Update `/malpractice_log/` to return JSON:

```python
@login_required
def malpractice_log_api(request):
    # ... existing filter logic ...
    
    logs_data = []
    for log in logs:
        logs_data.append({
            'id': log.id,
            'date': str(log.date),
            'time': str(log.time),
            'malpractice': log.malpractice,
            'proof': log.proof.url if log.proof else None,
            'verified': log.verified,
            'is_malpractice': log.is_malpractice,
            'lecture_hall': {
                'id': log.lecture_hall.id,
                'hall_name': log.lecture_hall.hall_name,
                'building': log.lecture_hall.building,
                'assigned_teacher': {
                    'id': log.lecture_hall.assigned_teacher.id,
                    'first_name': log.lecture_hall.assigned_teacher.first_name,
                    'last_name': log.lecture_hall.assigned_teacher.last_name,
                } if log.lecture_hall.assigned_teacher else None,
            },
        })
    
    return JsonResponse({
        'result': logs_data,
        'buildings': list(LectureHall.objects.values_list('building', flat=True).distinct()),
        'faculty_list': list(User.objects.filter(teacherprofile__isnull=False, is_superuser=False).values('id', 'first_name', 'last_name')),
    })
```

### 3. Lecture Halls Endpoint

Update `/manage-lecture-halls/` to return JSON:

```python
@login_required
@user_passes_test(is_admin)
def manage_lecture_halls_api(request):
    if request.method == 'GET':
        # ... existing filter logic ...
        
        halls_data = []
        for hall in lecture_halls:
            halls_data.append({
                'id': hall.id,
                'hall_name': hall.hall_name,
                'building': hall.building,
                'assigned_teacher': {
                    'id': hall.assigned_teacher.id,
                    'first_name': hall.assigned_teacher.first_name,
                    'last_name': hall.assigned_teacher.last_name,
                    'username': hall.assigned_teacher.username,
                } if hall.assigned_teacher else None,
            })
        
        teachers_data = []
        for teacher in teachers:
            teachers_data.append({
                'id': teacher.id,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'username': teacher.username,
            })
        
        return JsonResponse({
            'lecture_halls': halls_data,
            'teachers': teachers_data,
            'buildings': list(LectureHall.objects.values_list('building', flat=True).distinct()),
        })
    
    # POST handling remains the same
```

### 4. View Teachers Endpoint

Update `/view_teachers/` to return JSON:

```python
@login_required
@user_passes_test(is_admin)
def view_teachers_api(request):
    # ... existing filter logic ...
    
    teachers_data = []
    for teacher in teachers:
        teacher_data = {
            'id': teacher.id,
            'username': teacher.username,
            'email': teacher.email,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
        }
        
        if hasattr(teacher, 'lecturehall'):
            teacher_data['lecturehall'] = {
                'id': teacher.lecturehall.id,
                'hall_name': teacher.lecturehall.hall_name,
                'building': teacher.lecturehall.building,
            }
        else:
            teacher_data['lecturehall'] = None
        
        teachers_data.append(teacher_data)
    
    return JsonResponse({
        'teachers': teachers_data,
        'buildings': list(LectureHall.objects.values_list('building', flat=True).distinct()),
    })
```

## 🔀 URL Routing

### Option 1: Separate API Routes (Recommended)

Add API-specific routes in `app/urls.py`:

```python
urlpatterns = [
    # Existing template-based routes
    path('home', views.home),
    path('profile/', views.profile, name='profile'),
    # ...
    
    # New API routes for React
    path('api/profile/', views.profile_api, name='profile_api'),
    path('api/malpractice_log/', views.malpractice_log_api, name='malpractice_log_api'),
    path('api/manage-lecture-halls/', views.manage_lecture_halls_api, name='manage_lecture_halls_api'),
    path('api/view_teachers/', views.view_teachers_api, name='view_teachers_api'),
]
```

Then update React frontend's `lib/api.ts`:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,  // Add /api prefix
  // ...
});
```

### Option 2: Content Negotiation

Modify existing views to return JSON when requested:

```python
def profile(request):
    if request.headers.get('Accept') == 'application/json':
        return profile_api(request)
    return render(request, 'profile.html')
```

## 📦 Production Deployment

### 1. Build React App

```bash
cd frontend
npm run build
```

### 2. Configure Static Files

In `app/settings.py`:

```python
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend/dist/assets'),
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'frontend/dist')],
        # ...
    },
]
```

### 3. Add Catch-All Route

In `app/urls.py`:

```python
from django.views.generic import TemplateView

urlpatterns = [
    # ... all your API routes ...
    
    # Catch-all for React Router (must be last)
    path('', TemplateView.as_view(template_name='index.html'), name='react_app'),
]
```

### 4. Update Production Settings

```python
# Production settings
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

## ✅ Testing Checklist

- [ ] CORS headers are working
- [ ] CSRF token is accessible from JavaScript
- [ ] Session authentication works
- [ ] Login/logout flow works
- [ ] Profile data loads correctly
- [ ] Malpractice logs display with filters
- [ ] Admin can add lecture halls
- [ ] Admin can assign teachers
- [ ] Admin can review malpractice
- [ ] Camera controls work
- [ ] File uploads work (profile pictures)
- [ ] Video playback works (proof videos)
- [ ] Notifications display correctly
- [ ] Protected routes redirect to login
- [ ] Admin routes block non-admin users

## 🐛 Common Issues

### Issue: CORS errors
**Solution**: Check CORS_ALLOWED_ORIGINS includes your frontend URL

### Issue: CSRF token missing
**Solution**: Ensure CSRF_COOKIE_HTTPONLY = False

### Issue: Session not persisting
**Solution**: Check CORS_ALLOW_CREDENTIALS = True and axios withCredentials = true

### Issue: 404 on API calls
**Solution**: Verify URL patterns match frontend API calls

### Issue: Static files not loading in production
**Solution**: Run `python manage.py collectstatic` and check STATICFILES_DIRS

## 📚 Additional Resources

- [Django CORS Headers](https://github.com/adamchainz/django-cors-headers)
- [Django REST Framework](https://www.django-rest-framework.org/) (optional, for better API support)
- [Django Session Authentication](https://docs.djangoproject.com/en/stable/topics/http/sessions/)
