/**
 * Header Component
 * Top navigation bar with user info and notifications
 */
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Bell, User, Settings, LogOut, Menu, X } from 'lucide-react';

interface HeaderProps {
  onToggleSidebar?: () => void;
  sidebarOpen?: boolean;
}

const Header: React.FC<HeaderProps> = ({ onToggleSidebar, sidebarOpen = true }) => {
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <header className="header">
      <div className="header-left">
        {onToggleSidebar && (
          <button
            className="header-menu-button"
            onClick={onToggleSidebar}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        )}
        <h1 className="header-title">CyberSentinel</h1>
      </div>

      <div className="header-right">
        <div className="header-notifications">
          <button
            className="header-icon-button"
            onClick={() => setShowNotifications(!showNotifications)}
            aria-label="Notifications"
          >
            <Bell size={20} />
            <span className="notification-badge">3</span>
          </button>

          {showNotifications && (
            <div className="dropdown-menu notifications-menu">
              <div className="dropdown-header">
                <h3>Notifications</h3>
              </div>
              <div className="dropdown-body">
                <div className="notification-item">
                  <div className="notification-icon warning">!</div>
                  <div className="notification-content">
                    <p className="notification-title">High severity log detected</p>
                    <p className="notification-time">5 minutes ago</p>
                  </div>
                </div>
                <div className="notification-item">
                  <div className="notification-icon info">i</div>
                  <div className="notification-content">
                    <p className="notification-title">System health check completed</p>
                    <p className="notification-time">1 hour ago</p>
                  </div>
                </div>
                <div className="notification-item">
                  <div className="notification-icon error">×</div>
                  <div className="notification-content">
                    <p className="notification-title">Threat detected: SQL Injection attempt</p>
                    <p className="notification-time">2 hours ago</p>
                  </div>
                </div>
              </div>
              <div className="dropdown-footer">
                <button className="dropdown-footer-link">View all notifications</button>
              </div>
            </div>
          )}
        </div>

        <div className="header-user">
          <button
            className="header-user-button"
            onClick={() => setShowUserMenu(!showUserMenu)}
            aria-label="User menu"
          >
            <div className="user-avatar">
              <User size={18} />
            </div>
            <span className="user-name">{user?.username || 'User'}</span>
          </button>

          {showUserMenu && (
            <div className="dropdown-menu user-menu">
              <div className="dropdown-header">
                <p className="user-email">{user?.email || user?.username}</p>
                <p className="user-role">{user?.role || 'User'}</p>
              </div>
              <div className="dropdown-body">
                <button className="dropdown-item">
                  <User size={16} />
                  <span>Profile</span>
                </button>
                <button className="dropdown-item">
                  <Settings size={16} />
                  <span>Settings</span>
                </button>
              </div>
              <div className="dropdown-footer">
                <button className="dropdown-item logout" onClick={handleLogout}>
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
