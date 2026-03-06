# Quick Start Guide

## Prerequisites
- Node.js 20+ installed
- Django backend running on port 8000
- npm or yarn package manager

## Installation

```bash
cd frontend
npm install
```

## Configuration

The `.env` file is already configured:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Run Development Server

```bash
npm run dev
```

Visit `http://localhost:5173` in your browser.

## Default Login Credentials

Use your existing Django admin or teacher accounts:
- Admin: Your Django superuser credentials
- Teacher: Any registered teacher account

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Features

### For All Users
- 🔐 Login/Register
- 👤 Profile management
- 📋 View malpractice logs
- 🔔 Real-time notifications

### For Admins Only
- 🏢 Manage lecture halls
- 👥 View teachers
- 📹 Control cameras
- ✅ Review malpractice incidents

## Troubleshooting

### Port Already in Use
If port 5173 is busy, Vite will automatically use the next available port.

### API Connection Issues
1. Ensure Django is running on port 8000
2. Check `.env` file has correct API URL
3. Verify CORS settings in Django

### CSRF Token Errors
Ensure Django settings have:
```python
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
```

### Login Not Working
1. Check Django backend is running
2. Verify credentials are correct
3. Check browser console for errors
4. Ensure cookies are enabled

## Tech Stack

- ⚛️ React 19 + TypeScript
- 🎨 Tailwind CSS
- 🔄 React Query (TanStack Query)
- 🛣️ React Router
- 📡 Axios
- 🎭 Radix UI

## Need Help?

Check the detailed documentation:
- `SETUP.md` - Complete setup guide
- `MIGRATION_STATUS.md` - Implementation details
- `README.md` - Project overview
