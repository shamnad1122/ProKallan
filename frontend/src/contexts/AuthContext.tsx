import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import type { User, TeacherProfile, AuthContextType, RegisterData } from '@/types';
import { useToast } from '@/hooks/use-toast';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<TeacherProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    // Fetch CSRF token first, then check auth
    const initialize = async () => {
      try {
        await api.get('/csrf/');
      } catch (error) {
        console.error('Failed to fetch CSRF token:', error);
      }
      await checkAuth();
    };
    initialize();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await api.get('/profile/');
      setUser(response.data.user);
      setProfile(response.data.profile);
    } catch (error) {
      setUser(null);
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    try {
      await api.post('/login/addlogin', { username, password });
      await checkAuth();
      toast({
        title: 'Success',
        description: 'Logged in successfully',
      });
      navigate('/');
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Invalid credentials',
        variant: 'destructive',
      });
      throw error;
    }
  };

  const logout = async () => {
    try {
      await api.post('/logout/');
      setUser(null);
      setProfile(null);
      toast({
        title: 'Success',
        description: 'Logged out successfully',
      });
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const register = async (data: RegisterData) => {
    try {
      const formData = new FormData();
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined) {
          formData.append(key, value);
        }
      });
      
      await api.post('/register/teacher/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      toast({
        title: 'Success',
        description: 'Registration successful. Please login.',
      });
      navigate('/login');
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Registration failed',
        variant: 'destructive',
      });
      throw error;
    }
  };

  const updateProfile = async (data: Partial<User & TeacherProfile>) => {
    try {
      const formData = new FormData();
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined) {
          formData.append(key, value);
        }
      });
      
      await api.post('/profile/edit/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      await checkAuth();
      toast({
        title: 'Success',
        description: 'Profile updated successfully',
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Update failed',
        variant: 'destructive',
      });
      throw error;
    }
  };

  const changePassword = async (oldPassword: string, newPassword: string) => {
    try {
      await api.post('/profile/change-password/', {
        old_password: oldPassword,
        new_password1: newPassword,
        new_password2: newPassword,
      });
      
      toast({
        title: 'Success',
        description: 'Password changed successfully',
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Password change failed',
        variant: 'destructive',
      });
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    profile,
    isLoading,
    isAdmin: user?.is_superuser || false,
    login,
    logout,
    register,
    updateProfile,
    changePassword,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
