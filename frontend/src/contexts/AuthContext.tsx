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
        await api.get('/api/csrf/');
      } catch (error) {
        console.error('Failed to fetch CSRF token:', error);
      }
      await checkAuth();
    };
    initialize();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await api.get('/api/auth/user/');
      if (response.data.success) {
        const userData = response.data.user;
        setUser({
          id: userData.id,
          username: userData.username,
          email: userData.email,
          first_name: userData.first_name,
          last_name: userData.last_name,
          is_superuser: userData.is_admin,
        });
        setProfile({
          phone: userData.phone || '',
          profile_picture: userData.profile_picture || null,
          lecture_hall: userData.lecture_hall || null,
        });
      }
    } catch (error) {
      setUser(null);
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const response = await api.post('/api/auth/login/', { username, password });
      if (response.data.success) {
        await checkAuth();
        toast({
          title: 'Success',
          description: 'Logged in successfully',
        });
        navigate('/');
      }
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
      await api.post('/api/auth/logout/');
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
      // Note: Profile picture upload not supported in JSON API yet
      // Convert to JSON format
      const registerData = {
        username: data.username,
        email: data.email,
        password: data.password,
        first_name: data.first_name,
        last_name: data.last_name,
        phone: data.phone,
      };
      
      const response = await api.post('/api/auth/register/', registerData);
      
      if (response.data.success) {
        toast({
          title: 'Success',
          description: 'Registration successful. Please login.',
        });
        navigate('/login');
      }
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
      const updateData: any = {};
      if (data.first_name) updateData.first_name = data.first_name;
      if (data.last_name) updateData.last_name = data.last_name;
      if (data.email) updateData.email = data.email;
      if (data.phone) updateData.phone = data.phone;
      
      const response = await api.put('/api/profile/update/', updateData);
      
      if (response.data.success) {
        await checkAuth();
        toast({
          title: 'Success',
          description: 'Profile updated successfully',
        });
      }
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
      const response = await api.post('/api/profile/change-password/', {
        old_password: oldPassword,
        new_password: newPassword,
      });
      
      if (response.data.success) {
        toast({
          title: 'Success',
          description: 'Password changed successfully',
        });
      }
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
