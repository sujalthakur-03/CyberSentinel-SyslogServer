/**
 * Login Page Component
 * Handles user authentication with username and password
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, AlertCircle, Loader2 } from 'lucide-react';
import { parseErrorMessage } from '../utils/helpers';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }

    setIsLoading(true);

    try {
      await login(username, password);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(parseErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <div className="login-logo">
              <Shield size={48} className="logo-icon" />
            </div>
            <h1 className="login-title">CyberSentinel</h1>
            <p className="login-subtitle">Syslog Monitoring & Analysis</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {error && (
              <div className="error-message">
                <AlertCircle size={18} />
                <span>{error}</span>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="username" className="form-label">
                Username
              </label>
              <input
                id="username"
                type="text"
                className="form-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                disabled={isLoading}
                autoComplete="username"
                autoFocus
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <input
                id="password"
                type="password"
                className="form-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                disabled={isLoading}
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              className="login-button"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="spinner-icon" />
                  <span>Signing in...</span>
                </>
              ) : (
                <span>Sign In</span>
              )}
            </button>
          </form>

          <div className="login-footer">
            <p className="footer-text">
              Secure access to your syslog monitoring system
            </p>
          </div>
        </div>

        <div className="login-info">
          <div className="info-card">
            <h3>Real-time Monitoring</h3>
            <p>Monitor your system logs in real-time with advanced analytics</p>
          </div>
          <div className="info-card">
            <h3>Threat Detection</h3>
            <p>Automated security threat detection and alerting</p>
          </div>
          <div className="info-card">
            <h3>Advanced Search</h3>
            <p>Powerful search capabilities across all your logs</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
