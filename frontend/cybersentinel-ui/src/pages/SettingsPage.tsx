/**
 * Settings Page Component
 * System configuration and user preferences
 */
import React, { useState, useEffect } from 'react';
import {
  Save,
  RefreshCw,
  Database,
  Bell,
  Palette,
  Server,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import api from '../services/api';
import { SystemSettings, HealthStatus } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import { parseErrorMessage } from '../utils/helpers';

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SystemSettings>({
    api_endpoint: 'http://localhost:8000',
    refresh_interval: 30,
    logs_per_page: 50,
    theme: 'dark',
    enable_notifications: true,
    enable_auto_refresh: true,
  });

  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [connectionStatus, setConnectionStatus] = useState<'success' | 'error' | null>(null);

  useEffect(() => {
    const savedSettings = localStorage.getItem('settings');
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings));
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, []);

  const handleSettingChange = (key: keyof SystemSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSaveSettings = () => {
    setIsSaving(true);
    setSaveMessage('');

    try {
      localStorage.setItem('settings', JSON.stringify(settings));
      setSaveMessage('Settings saved successfully');
      setTimeout(() => setSaveMessage(''), 3000);
    } catch (error) {
      setSaveMessage('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    setConnectionStatus(null);

    try {
      const healthData = await api.getHealth();
      setHealth(healthData);
      setConnectionStatus('success');
    } catch (error) {
      setConnectionStatus('error');
      console.error('Connection test failed:', error);
    } finally {
      setIsTestingConnection(false);
    }
  };

  const handleResetSettings = () => {
    if (window.confirm('Are you sure you want to reset all settings to default?')) {
      const defaultSettings: SystemSettings = {
        api_endpoint: 'http://localhost:8000',
        refresh_interval: 30,
        logs_per_page: 50,
        theme: 'dark',
        enable_notifications: true,
        enable_auto_refresh: true,
      };
      setSettings(defaultSettings);
      localStorage.setItem('settings', JSON.stringify(defaultSettings));
      setSaveMessage('Settings reset to default');
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };

  return (
    <div className="settings-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Settings</h1>
          <p className="page-subtitle">
            Configure system preferences and options
          </p>
        </div>
        <div className="page-actions">
          <button
            className="secondary-button"
            onClick={handleResetSettings}
          >
            <RefreshCw size={18} />
            Reset to Default
          </button>
          <button
            className="primary-button"
            onClick={handleSaveSettings}
            disabled={isSaving}
          >
            <Save size={18} />
            {isSaving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>

      {saveMessage && (
        <div className={`settings-message ${saveMessage.includes('success') ? 'success' : 'error'}`}>
          {saveMessage.includes('success') ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
          <span>{saveMessage}</span>
        </div>
      )}

      <div className="settings-sections">
        <div className="settings-section">
          <div className="section-header">
            <Server size={20} />
            <h2>API Configuration</h2>
          </div>
          <div className="section-content">
            <div className="form-group">
              <label className="form-label">API Endpoint</label>
              <input
                type="text"
                className="form-input"
                value={settings.api_endpoint}
                onChange={(e) => handleSettingChange('api_endpoint', e.target.value)}
                placeholder="http://localhost:8000"
              />
              <p className="form-hint">Base URL for the backend API server</p>
            </div>

            <div className="connection-test">
              <button
                className="test-button"
                onClick={handleTestConnection}
                disabled={isTestingConnection}
              >
                {isTestingConnection ? (
                  <>
                    <RefreshCw size={18} className="spinning" />
                    Testing Connection...
                  </>
                ) : (
                  <>
                    <Database size={18} />
                    Test Connection
                  </>
                )}
              </button>

              {connectionStatus === 'success' && health && (
                <div className="connection-result success">
                  <CheckCircle size={18} />
                  <div className="result-details">
                    <p className="result-title">Connection Successful</p>
                    <div className="health-details">
                      <span>Status: {health.status}</span>
                      <span>OpenSearch: {health.opensearch.status}</span>
                      {health.kafka && <span>Kafka: {health.kafka.status}</span>}
                    </div>
                  </div>
                </div>
              )}

              {connectionStatus === 'error' && (
                <div className="connection-result error">
                  <AlertCircle size={18} />
                  <div className="result-details">
                    <p className="result-title">Connection Failed</p>
                    <p className="result-text">Unable to connect to the API server</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="settings-section">
          <div className="section-header">
            <RefreshCw size={20} />
            <h2>Display Settings</h2>
          </div>
          <div className="section-content">
            <div className="form-group">
              <label className="form-label">Auto-refresh Interval (seconds)</label>
              <select
                className="form-select"
                value={settings.refresh_interval}
                onChange={(e) => handleSettingChange('refresh_interval', Number(e.target.value))}
              >
                <option value={10}>10 seconds</option>
                <option value={30}>30 seconds</option>
                <option value={60}>1 minute</option>
                <option value={120}>2 minutes</option>
                <option value={300}>5 minutes</option>
              </select>
              <p className="form-hint">How often to refresh data automatically</p>
            </div>

            <div className="form-group">
              <label className="form-label">Logs Per Page</label>
              <select
                className="form-select"
                value={settings.logs_per_page}
                onChange={(e) => handleSettingChange('logs_per_page', Number(e.target.value))}
              >
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
                <option value={200}>200</option>
              </select>
              <p className="form-hint">Number of logs to display per page</p>
            </div>

            <div className="form-group">
              <label className="form-label">
                <input
                  type="checkbox"
                  className="form-checkbox"
                  checked={settings.enable_auto_refresh}
                  onChange={(e) => handleSettingChange('enable_auto_refresh', e.target.checked)}
                />
                <span>Enable Auto-refresh</span>
              </label>
              <p className="form-hint">Automatically refresh data at the specified interval</p>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <div className="section-header">
            <Palette size={20} />
            <h2>Appearance</h2>
          </div>
          <div className="section-content">
            <div className="form-group">
              <label className="form-label">Theme</label>
              <select
                className="form-select"
                value={settings.theme}
                onChange={(e) => handleSettingChange('theme', e.target.value)}
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
              </select>
              <p className="form-hint">Choose your preferred color theme</p>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <div className="section-header">
            <Bell size={20} />
            <h2>Notifications</h2>
          </div>
          <div className="section-content">
            <div className="form-group">
              <label className="form-label">
                <input
                  type="checkbox"
                  className="form-checkbox"
                  checked={settings.enable_notifications}
                  onChange={(e) => handleSettingChange('enable_notifications', e.target.checked)}
                />
                <span>Enable Notifications</span>
              </label>
              <p className="form-hint">Show desktop notifications for important events</p>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <div className="section-header">
            <Database size={20} />
            <h2>Data Management</h2>
          </div>
          <div className="section-content">
            <div className="data-actions">
              <button
                className="secondary-button"
                onClick={() => {
                  if (window.confirm('Clear all saved searches?')) {
                    localStorage.removeItem('savedSearches');
                    setSaveMessage('Saved searches cleared');
                    setTimeout(() => setSaveMessage(''), 3000);
                  }
                }}
              >
                Clear Saved Searches
              </button>
              <button
                className="secondary-button"
                onClick={() => {
                  if (window.confirm('Clear all application data? This will log you out.')) {
                    localStorage.clear();
                    window.location.href = '/login';
                  }
                }}
              >
                Clear All Data
              </button>
            </div>
          </div>
        </div>

        <div className="settings-section">
          <div className="section-header">
            <Server size={20} />
            <h2>System Information</h2>
          </div>
          <div className="section-content">
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Application Version:</span>
                <span className="info-value">1.0.0</span>
              </div>
              <div className="info-item">
                <span className="info-label">Build Date:</span>
                <span className="info-value">{new Date().toLocaleDateString()}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Environment:</span>
                <span className="info-value">
                  {process.env.NODE_ENV || 'development'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
