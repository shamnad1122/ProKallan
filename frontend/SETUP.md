# DetectSus React Frontend

This is the React-based frontend for the DetectSus malpractice detection system, built to replace the Django template-based frontend.

## Tech Stack

- **React 19** with TypeScript
- **Vite** for build tooling
- **React Router** for routing
- **TanStack Query** (React Query) for data fetching and caching
- **Axios** for API calls with Django session auth
- **Tailwind CSS** for styling
- **Radix UI** for accessible UI primitives
- **Lucide React** for icons

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI components (Button, Input, Card, etc.)
│   │   ├── Layout.tsx       # Main layout with navigation
│   │   ├── PageHeader.tsx   # Page header component
│   │   └── ProtectedRoute.tsx # Route protection wrapper
│   ├── contexts/
│   │   └── AuthContext.tsx  # Authentication context and provider
│   ├── hooks/
│   │   └── use-toast.ts     # Toast notification hook
│   ├── lib/
│   │   ├── api.ts           # Axios instance with interceptors
│   │   └── utils.ts         # Utility functions
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Profile.tsx
│   │   ├── EditProfile.tsx
│   │   ├── ChangePassword.tsx
│   │   ├── MalpracticeLog.tsx
│   │   ├── ManageLectureHalls.tsx
│   │   ├── ViewTeachers.tsx
│   │   └── RunCameras.tsx
│   ├── types/
│   │   └── index.ts         # TypeScript type definitions
│   ├── App.tsx              # Main app with routing
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── .env                     # Environment variables
└── vite.config.ts           # Vite configuration
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file (or use the existing one):

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Features Implemented

### ✅ Authentication
- Login with Django session auth
- Teacher registration with profile picture
- Profile management
- Password change
- Protected routes (user and admin)

### ✅ Malpractice Log
- View malpractice detection logs
- Filter by date, time, building, faculty, assignment status
- Admin review workflow (approve/reject)
- Video proof viewing
- Real-time updates with React Query

### ✅ Lecture Hall Management (Admin)
- Add new lecture halls
- Assign teachers to halls
- Filter by building and assignment status
- Search functionality

### ✅ Teacher Management (Admin)
- View all registered teachers
- See teacher assignments
- Filter by assignment status and building

### ✅ Camera Control (Admin)
- Start/stop camera monitoring scripts
- Visual status indicators
- Real-time feedback

## API Integration

The frontend communicates with the Django backend using:

- **Axios** with automatic CSRF token handling
- **Session-based authentication** (cookies)
- **React Query** for caching and automatic refetching
- **Interceptors** for error handling and redirects

### API Endpoints Used

- `POST /login/addlogin` - Login
- `POST /register/teacher/` - Register
- `GET /profile/` - Get user profile
- `POST /profile/edit/` - Update profile
- `POST /profile/change-password/` - Change password
- `POST /logout/` - Logout
- `GET /malpractice_log/` - Get malpractice logs
- `POST /review_malpractice/` - Review malpractice (admin)
- `GET /manage-lecture-halls/` - Get lecture halls
- `POST /manage-lecture-halls/` - Add hall or map teacher
- `GET /view_teachers/` - Get teachers
- `POST /trigger_camera_scripts/` - Start cameras
- `POST /stop_camera_scripts/` - Stop cameras

## Django Integration

### Option 1: Development (Proxy)

Run both servers separately:
- Django: `python manage.py runserver` (port 8000)
- React: `npm run dev` (port 5173)

Vite is configured to proxy API requests to Django.

### Option 2: Production (Static Build)

1. Build the React app:
   ```bash
   npm run build
   ```

2. Configure Django to serve the built files:
   ```python
   # settings.py
   STATICFILES_DIRS = [
       os.path.join(BASE_DIR, 'frontend/dist'),
   ]
   ```

3. Add a catch-all route in Django:
   ```python
   # urls.py
   from django.views.generic import TemplateView
   
   urlpatterns = [
       # ... your API routes ...
       path('', TemplateView.as_view(template_name='index.html')),
   ]
   ```

## Styling

The project uses:
- **Tailwind CSS** for utility-first styling
- **CSS Variables** for theming (light/dark mode ready)
- **Radix UI** for accessible, unstyled components
- **shadcn/ui** design patterns

## Type Safety

Full TypeScript support with:
- Type definitions for all API responses
- Strongly typed React components
- Type-safe routing
- IntelliSense support

## Next Steps

1. Test all functionality end-to-end
2. Add loading states and error boundaries
3. Implement dark mode toggle
4. Add unit tests with Vitest
5. Optimize bundle size
6. Add PWA support (optional)
7. Implement real-time notifications with WebSockets (optional)

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure Django has CORS headers configured:
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True
```

### CSRF Token Issues
The frontend automatically extracts CSRF tokens from cookies. Ensure Django is setting the cookie:
```python
# settings.py
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
```

### Session Authentication
Ensure `withCredentials: true` is set in Axios (already configured in `lib/api.ts`).
