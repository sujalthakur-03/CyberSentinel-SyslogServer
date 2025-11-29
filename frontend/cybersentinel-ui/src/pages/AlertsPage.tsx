/**
 * Alerts Page Component
 * Displays security alerts and threat notifications
 */
import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  AlertCircle,
  Shield,
  RefreshCw,
  Filter,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp
} from 'lucide-react';
import api from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { parseErrorMessage, formatTimestamp } from '../utils/helpers';

interface Alert {
  id: string;
  timestamp: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  source: string;
  status: 'active' | 'acknowledged' | 'resolved';
  threat_type?: string;
  affected_hosts?: string[];
}

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchAlerts();
  }, [filterSeverity, filterStatus]);

  const fetchAlerts = async () => {
    setIsLoading(true);
    setError('');

    try {
      // Fetch threat logs from the API
      const response = await api.getThreatLogs({
        size: 100,
      });

      // Transform threat logs into alerts
      const alertsData = response.logs?.map((log: any, index: number) => ({
        id: log.id || `alert-${index}`,
        timestamp: log.timestamp || log.received_at,
        severity: mapSeverityToAlertLevel(log.severity),
        title: log.threat_indicators?.join(', ') || 'Security Alert',
        description: log.message,
        source: log.hostname || 'Unknown',
        status: 'active',
        threat_type: log.threat_indicators?.[0] || 'Unknown',
        affected_hosts: [log.hostname],
      })) || [];

      setAlerts(alertsData);
    } catch (err) {
      setError(parseErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const mapSeverityToAlertLevel = (severity: string): 'critical' | 'high' | 'medium' | 'low' => {
    const severityMap: { [key: string]: 'critical' | 'high' | 'medium' | 'low' } = {
      'emergency': 'critical',
      'alert': 'critical',
      'critical': 'critical',
      'error': 'high',
      'warning': 'medium',
      'notice': 'low',
      'informational': 'low',
      'debug': 'low',
    };
    return severityMap[severity] || 'medium';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="severity-icon critical" size={20} />;
      case 'high':
        return <AlertTriangle className="severity-icon high" size={20} />;
      case 'medium':
        return <AlertCircle className="severity-icon medium" size={20} />;
      case 'low':
        return <Shield className="severity-icon low" size={20} />;
      default:
        return <AlertCircle className="severity-icon" size={20} />;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      active: { color: 'danger', icon: TrendingUp },
      acknowledged: { color: 'warning', icon: Clock },
      resolved: { color: 'success', icon: CheckCircle },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.active;
    const StatusIcon = config.icon;

    return (
      <span className={`status-badge ${config.color}`}>
        <StatusIcon size={14} />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const filteredAlerts = alerts.filter(alert => {
    const severityMatch = filterSeverity === 'all' || alert.severity === filterSeverity;
    const statusMatch = filterStatus === 'all' || alert.status === filterStatus;
    return severityMatch && statusMatch;
  });

  const stats = {
    total: alerts.length,
    critical: alerts.filter(a => a.severity === 'critical').length,
    high: alerts.filter(a => a.severity === 'high').length,
    active: alerts.filter(a => a.status === 'active').length,
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="header-left">
          <h1 className="page-title">
            <Shield className="page-icon" />
            Security Alerts
          </h1>
          <p className="page-subtitle">Monitor security threats and anomalies</p>
        </div>
        <div className="header-right">
          <button
            className="btn-secondary"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter size={18} />
            Filters
          </button>
          <button
            className="btn-primary"
            onClick={fetchAlerts}
            disabled={isLoading}
          >
            <RefreshCw size={18} className={isLoading ? 'spinning' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon primary">
            <AlertTriangle size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Total Alerts</p>
            <p className="stat-value">{stats.total}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon danger">
            <XCircle size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Critical</p>
            <p className="stat-value">{stats.critical}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon warning">
            <AlertCircle size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">High Priority</p>
            <p className="stat-value">{stats.high}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon success">
            <TrendingUp size={24} />
          </div>
          <div className="stat-content">
            <p className="stat-label">Active</p>
            <p className="stat-value">{stats.active}</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="filters-panel">
          <div className="filter-group">
            <label className="filter-label">Severity</label>
            <select
              className="filter-select"
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Status</label>
            <select
              className="filter-select"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-banner">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Alerts List */}
      <div className="content-card">
        <div className="alerts-list">
          {filteredAlerts.length === 0 ? (
            <div className="empty-state">
              <CheckCircle size={48} className="empty-icon" />
              <h3>No Alerts</h3>
              <p>No security alerts found matching your criteria</p>
            </div>
          ) : (
            filteredAlerts.map((alert) => (
              <div key={alert.id} className="alert-item">
                <div className="alert-header">
                  <div className="alert-severity">
                    {getSeverityIcon(alert.severity)}
                    <span className={`severity-label ${alert.severity}`}>
                      {alert.severity.toUpperCase()}
                    </span>
                  </div>
                  <div className="alert-status">
                    {getStatusBadge(alert.status)}
                  </div>
                </div>

                <div className="alert-body">
                  <h3 className="alert-title">{alert.title}</h3>
                  <p className="alert-description">{alert.description}</p>

                  <div className="alert-meta">
                    <div className="meta-item">
                      <Clock size={14} />
                      <span>{formatTimestamp(alert.timestamp)}</span>
                    </div>
                    <div className="meta-item">
                      <Shield size={14} />
                      <span>Source: {alert.source}</span>
                    </div>
                    {alert.threat_type && (
                      <div className="meta-item">
                        <AlertTriangle size={14} />
                        <span>Type: {alert.threat_type}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="alert-actions">
                  <button className="btn-sm btn-outline">
                    View Details
                  </button>
                  <button className="btn-sm btn-outline">
                    Acknowledge
                  </button>
                  <button className="btn-sm btn-outline">
                    Resolve
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AlertsPage;
