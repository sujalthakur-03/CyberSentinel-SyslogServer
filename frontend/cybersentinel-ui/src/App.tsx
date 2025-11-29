/**
 * Main App Component
 * Router configuration and layout setup
 */
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import LogsPage from './pages/LogsPage';
import SearchPage from './pages/SearchPage';
import AlertsPage from './pages/AlertsPage';
import SettingsPage from './pages/SettingsPage';
import './index.css';

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="app-layout">
      <Sidebar isOpen={sidebarOpen} />
      <div className={`main-content ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <Header
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
        />
        <main className="page-content">
          {children}
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route path="/dashboard" element={
            <ProtectedRoute>
              <AppLayout>
                <Dashboard />
              </AppLayout>
            </ProtectedRoute>
          } />

          <Route path="/logs" element={
            <ProtectedRoute>
              <AppLayout>
                <LogsPage />
              </AppLayout>
            </ProtectedRoute>
          } />

          <Route path="/search" element={
            <ProtectedRoute>
              <AppLayout>
                <SearchPage />
              </AppLayout>
            </ProtectedRoute>
          } />

          <Route path="/alerts" element={
            <ProtectedRoute>
              <AppLayout>
                <AlertsPage />
              </AppLayout>
            </ProtectedRoute>
          } />

          <Route path="/settings" element={
            <ProtectedRoute>
              <AppLayout>
                <SettingsPage />
              </AppLayout>
            </ProtectedRoute>
          } />

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
