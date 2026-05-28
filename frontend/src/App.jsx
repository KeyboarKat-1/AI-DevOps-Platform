import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout, AuthLayout } from './layouts';
import {
  Login,
  Register,
  DashboardPage,
  DockerPage,
  IncidentsPage,
  DeploymentsPage,
  SettingsPage,
  AIAssistantPage,
} from './pages';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './routes/ProtectedRoute';
import './index.css';

function AppContent() {
  const { user, logout, isAuthenticated } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <Routes>
      <Route
        path="/login"
        element={
          <AuthLayout>
            <Login />
          </AuthLayout>
        }
      />
      <Route
        path="/register"
        element={
          <AuthLayout>
            <Register />
          </AuthLayout>
        }
      />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <MainLayout user={user} onLogout={handleLogout}>
              <DashboardPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/docker"
        element={
          <ProtectedRoute>
            <MainLayout user={user} onLogout={handleLogout}>
              <DockerPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/incidents"
        element={
          <ProtectedRoute>
            <MainLayout user={user} onLogout={handleLogout}>
              <IncidentsPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/deployments"
        element={
          <ProtectedRoute>
            <MainLayout user={user} onLogout={handleLogout}>
              <DeploymentsPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/ai-assistant"
        element={
          <ProtectedRoute>
            <MainLayout user={user} onLogout={handleLogout}>
              <AIAssistantPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <MainLayout user={user} onLogout={handleLogout}>
              <SettingsPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/"
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
