import React, { createContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import { authService } from '../services/authService';
import { parseJwt, isTokenExpired } from '../utils/helpers';

const TOKEN_KEY = 'access_token';

export const AuthContext = createContext();

const getStoredToken = () => {
  const token = localStorage.getItem(TOKEN_KEY);
  return token && !isTokenExpired(token) ? token : null;
};

const setStoredToken = (token) => {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
    api.defaults.headers.Authorization = `Bearer ${token}`;
  } else {
    localStorage.removeItem(TOKEN_KEY);
    delete api.defaults.headers.Authorization;
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [initialized, setInitialized] = useState(false);

  const loadUser = useCallback(async () => {
    const token = getStoredToken();
    if (!token) {
      setStoredToken(null);
      setUser(null);
      setLoading(false);
      setInitialized(true);
      return;
    }

    setStoredToken(token);
    const decoded = parseJwt(token);
    if (decoded) {
      setUser({
        username: decoded.sub || decoded.username,
        email: decoded.email || '',
        name: decoded.name || decoded.username || decoded.sub || '',
      });
    }

    try {
      const response = await authService.getCurrentUser();
      const payload = response?.data || {};
      setUser({
        username: payload.username || payload.user || decoded?.sub || decoded?.username,
        email: payload.email || decoded?.email || '',
        name: payload.username || payload.user || decoded?.sub || decoded?.username,
      });
    } catch (err) {
      if (err.response?.status === 401) {
        setStoredToken(null);
        setUser(null);
      }
    } finally {
      setLoading(false);
      setInitialized(true);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = useCallback(async ({ identifier, password }) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authService.login(identifier, password);
      const token = response?.data?.access_token;
      if (!token) {
        throw new Error('Authentication succeeded but no token was returned.');
      }

      setStoredToken(token);
      const decoded = parseJwt(token);
      const profileResponse = await authService.getCurrentUser();
      const profile = profileResponse?.data || {};
      setUser({
        username: profile.username || decoded?.sub || decoded?.username || identifier,
        email: profile.email || decoded?.email || '',
        name: profile.username || decoded?.sub || decoded?.username || identifier,
      });
      setError(null);
      return { success: true };
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        'Login failed. Please verify your credentials.';
      setError(message);
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authService.updateProfile(payload);
      const profile = response?.data || {};
      if (profile.access_token) {
        setStoredToken(profile.access_token);
      }
      setUser((current) => ({
        ...current,
        username: profile.username || current?.username,
        email: profile.email || current?.email,
        name: profile.username || current?.name || current?.username,
      }));
      return { success: true, profile };
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        'Unable to update profile. Please try again.';
      setError(message);
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setStoredToken(null);
    setUser(null);
    setError(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        initialized,
        login,
        updateProfile,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
