import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for CSRF token
api.interceptors.request.use(
  (config) => {
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============ AUTH API ============
export const authAPI = {
  login: (username: string, password: string) => 
    api.post('/api/auth/login/', { username, password }),
  
  logout: () => 
    api.post('/api/auth/logout/'),
  
  register: (data: any) => 
    api.post('/api/auth/register/', data),
  
  getCurrentUser: () => 
    api.get('/api/auth/user/'),
  
  getCSRFToken: () => 
    api.get('/api/csrf/'),
};

// ============ PROFILE API ============
export const profileAPI = {
  update: (data: any) => 
    api.put('/api/profile/update/', data),
  
  changePassword: (oldPassword: string, newPassword: string) => 
    api.post('/api/profile/change-password/', { 
      old_password: oldPassword, 
      new_password: newPassword 
    }),
};

// ============ MALPRACTICE LOG API ============
export const malpracticeAPI = {
  getLogs: (filters?: any) => 
    api.get('/api/malpractice-logs/', { params: filters }),
  
  review: (id: number, decision: 'yes' | 'no') => 
    api.post('/api/malpractice-logs/review/', { id, decision }),
};

// ============ LECTURE HALL API ============
export const lectureHallAPI = {
  getAll: (filters?: any) => 
    api.get('/api/lecture-halls/', { params: filters }),
  
  add: (hallName: string, building: string) => 
    api.post('/api/lecture-halls/add/', { hall_name: hallName, building }),
  
  assignTeacher: (hallId: number, teacherId: number) => 
    api.post('/api/lecture-halls/assign/', { hall_id: hallId, teacher_id: teacherId }),
};

// ============ TEACHER API ============
export const teacherAPI = {
  getAll: (filters?: any) => 
    api.get('/api/teachers/', { params: filters }),
};

// ============ CAMERA API ============
export const cameraAPI = {
  start: () => 
    api.post('/api/cameras/start/'),
  
  stop: () => 
    api.post('/api/cameras/stop/'),
};

export default api;
