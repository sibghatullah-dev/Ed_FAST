/**
 * Authentication Store using Zustand
 */

import { create } from 'zustand';
import { api } from './api';

interface User {
  username: string;
  name: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (name: string, username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (username: string, password: string) => {
    try {
      const response = await api.login(username, password);
      if (response.success) {
        set({
          user: {
            username: response.data.username,
            name: response.data.name,
          },
          isAuthenticated: true,
        });
      } else {
        throw new Error(response.error || 'Login failed');
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message || 'Login failed');
    }
  },

  register: async (name: string, username: string, password: string) => {
    try {
      const response = await api.register({ name, username, password });
      if (response.success) {
        set({
          user: {
            username: response.data.username,
            name: response.data.name,
          },
          isAuthenticated: true,
        });
      } else {
        throw new Error(response.error || 'Registration failed');
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.error || error.message || 'Registration failed');
    }
  },

  logout: async () => {
    try {
      await api.logoutUser();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      set({ user: null, isAuthenticated: false });
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
  },

  checkAuth: async () => {
    try {
      const response = await api.verifyToken();
      if (response.success) {
        set({
          user: {
            username: response.data.username,
            name: response.data.name,
          },
          isAuthenticated: true,
          isLoading: false,
        });
      } else {
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));




