/**
 * Dashboard Page Component - Comprehensive Log Viewer
 * Main log viewing interface with 180-day calendar search
 */
import React, { useState, useEffect } from 'react';
import {
  Calendar,
  RefreshCw,
  Download,
  Filter,
  X,
  ChevronLeft,
  ChevronRight,
  Search as SearchIcon,
  FileText,
  AlertCircle,
  AlertTriangle
} from 'lucide-react';
import api from '../services/api';
import { SyslogEntry, SearchParams } from '../types';
import LogTable from '../components/LogTable';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  parseErrorMessage,
  exportToCSV,
  exportToJSON,
  formatNumber
} from '../utils/helpers';

const Dashboard: React.FC = () => {
  // Date range state
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Log data state
  const [logs, setLogs] = useState<SyslogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState('');

  // UI state
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);

  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchParams>({
    severity: '',
    facility: '',
    hostname: '',
    start_time: '',
    end_time: '',
  });

  // Stats
  const [stats, setStats] = useState({
    total: 0,
    errors: 0,
    warnings: 0,
  });

  // Initialize with last 7 days
  useEffect(() => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 7);

    setEndDate(end.toISOString().slice(0, 16));
    setStartDate(start.toISOString().slice(0, 16));
  }, []);

  const fetchLogs = async (showLoader = true) => {
    if (showLoader) {
      setIsLoading(true);
    } else {
      setIsRefreshing(true);
    }
    setError('');

    try {
      const params: SearchParams = {
        query: searchQuery || undefined,
        severity: filters.severity || undefined,
        facility: filters.facility || undefined,
        hostname: filters.hostname || undefined,
        start_time: startDate ? new Date(startDate).toISOString() : undefined,
        end_time: endDate ? new Date(endDate).toISOString() : undefined,
        page: currentPage,
        page_size: pageSize,
        sort_by: 'timestamp',
        sort_order: 'desc',
      };

      const response = await api.searchLogs(params);

      // Backend returns {total, page, page_size, logs} not OpenSearch format
      const logEntries = response.logs || [];

      setLogs(logEntries);
      setTotal(response.total || 0);

      // Calculate stats
      const errorCount = logEntries.filter((log: any) =>
        ['emergency', 'alert', 'critical', 'error'].includes(log.severity_name)
      ).length;
      const warningCount = logEntries.filter((log: any) =>
        log.severity_name === 'warning'
      ).length;

      setStats({
        total: response.total || 0,
        errors: errorCount,
        warnings: warningCount,
      });
    } catch (err) {
      setError(parseErrorMessage(err));
      console.error('Failed to fetch logs:', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    if (startDate && endDate) {
      fetchLogs();
    }
  }, [currentPage, pageSize, startDate, endDate]);

  const handleSearch = () => {
    setCurrentPage(1);
    fetchLogs();
  };

  const handleFilterChange = (key: keyof SearchParams, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleApplyFilters = () => {
    setCurrentPage(1);
    fetchLogs();
    setShowFilters(false);
  };

  const handleClearFilters = () => {
    setFilters({
      severity: '',
      facility: '',
      hostname: '',
      start_time: '',
      end_time: '',
    });
    setSearchQuery('');
    setCurrentPage(1);
    fetchLogs();
  };

  const handleExportCSV = () => {
    if (logs.length === 0) return;

    const exportData = logs.map(log => ({
      timestamp: log.timestamp,
      severity: log.severity_name,
      facility: log.facility_name,
      hostname: log.hostname,
      app_name: log.app_name || '',
      message: log.message,
      threat_detected: log.has_threat_indicators || false,
      threat_type: log.threat_keywords?.join(', ') || '',
    }));

    exportToCSV(exportData, `logs_export_${new Date().toISOString()}`);
  };

  const handleExportJSON = () => {
    if (logs.length === 0) return;
    exportToJSON(logs, `logs_export_${new Date().toISOString()}`);
  };

  const handleQuickDateRange = (days: number) => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - days);

    setEndDate(end.toISOString().slice(0, 16));
    setStartDate(start.toISOString().slice(0, 16));
    setCurrentPage(1);
  };

  const totalPages = Math.ceil(total / pageSize);
  const hasActiveFilters = !!(
    searchQuery ||
    filters.severity ||
    filters.facility ||
    filters.hostname
  );

  // Validate date range (max 180 days)
  const validateDateRange = () => {
    if (!startDate || !endDate) return true;
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    return diffDays <= 180;
  };

  if (isLoading && !logs.length) {
    return <LoadingSpinner fullScreen text="Loading logs..." />;
  }

  return (
    <div className="dashboard-page">
      {/* Header with Stats */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Log Viewer</h1>
          <p className="page-subtitle">
            {total.toLocaleString()} logs found in selected date range
          </p>
        </div>
        <div className="page-actions">
          <button
            className="action-button"
            onClick={() => fetchLogs(false)}
            disabled={isRefreshing}
          >
            <RefreshCw size={18} className={isRefreshing ? 'spinning' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-card-icon" style={{ backgroundColor: '#3b82f620', color: '#3b82f6' }}>
              <FileText size={24} />
            </div>
            <div className="stat-card-content">
              <h3 className="stat-card-title">Total Logs</h3>
              <p className="stat-card-value">{formatNumber(stats.total)}</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-card-icon" style={{ backgroundColor: '#ef444420', color: '#ef4444' }}>
              <AlertCircle size={24} />
            </div>
            <div className="stat-card-content">
              <h3 className="stat-card-title">Errors</h3>
              <p className="stat-card-value">{formatNumber(stats.errors)}</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-card-icon" style={{ backgroundColor: '#f59e0b20', color: '#f59e0b' }}>
              <AlertTriangle size={24} />
            </div>
            <div className="stat-card-content">
              <h3 className="stat-card-title">Warnings</h3>
              <p className="stat-card-value">{formatNumber(stats.warnings)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Date Range Selector */}
      <div className="date-range-section card" style={{ marginBottom: '24px' }}>
        <div className="date-range-header" style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Calendar size={20} style={{ color: 'var(--cyber-primary)' }} />
          <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Date Range (Max 180 days)</h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '16px' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Start Date</label>
            <input
              type="datetime-local"
              className="form-input"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              max={endDate}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">End Date</label>
            <input
              type="datetime-local"
              className="form-input"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              min={startDate}
            />
          </div>
        </div>

        {!validateDateRange() && (
          <div className="warning-message" style={{ marginBottom: '16px' }}>
            <AlertTriangle size={18} />
            <span>Date range cannot exceed 180 days</span>
          </div>
        )}

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button className="btn-sm" onClick={() => handleQuickDateRange(1)}>Today</button>
          <button className="btn-sm" onClick={() => handleQuickDateRange(7)}>Last 7 Days</button>
          <button className="btn-sm" onClick={() => handleQuickDateRange(30)}>Last 30 Days</button>
          <button className="btn-sm" onClick={() => handleQuickDateRange(90)}>Last 90 Days</button>
          <button className="btn-sm" onClick={() => handleQuickDateRange(180)}>Last 180 Days</button>
          <button
            className="btn-primary btn-sm"
            onClick={() => fetchLogs()}
            disabled={!validateDateRange()}
          >
            Apply Date Range
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="search-section" style={{ marginBottom: '24px' }}>
        <div className="search-bar">
          <SearchIcon size={20} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search logs by message content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          {searchQuery && (
            <button
              className="clear-button"
              onClick={() => {
                setSearchQuery('');
                setCurrentPage(1);
                fetchLogs();
              }}
            >
              <X size={18} />
            </button>
          )}
          <button className="search-button" onClick={handleSearch}>
            Search
          </button>
        </div>

        <div style={{ display: 'flex', gap: '12px', marginTop: '12px', flexWrap: 'wrap' }}>
          <button
            className="action-button"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter size={18} />
            Filters
            {hasActiveFilters && <span className="filter-badge">Active</span>}
          </button>
          <div className="dropdown">
            <button className="action-button">
              <Download size={18} />
              Export
            </button>
            <div className="dropdown-content">
              <button onClick={handleExportCSV}>Export as CSV</button>
              <button onClick={handleExportJSON}>Export as JSON</button>
            </div>
          </div>
        </div>
      </div>

      {/* Advanced Filters Panel */}
      {showFilters && (
        <div className="filters-panel card" style={{ marginBottom: '24px' }}>
          <div className="filters-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ margin: 0 }}>Advanced Filters</h3>
            <button className="close-button" onClick={() => setShowFilters(false)}>
              <X size={18} />
            </button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '16px' }}>
            <div className="filter-group">
              <label className="filter-label">Severity</label>
              <select
                className="filter-select"
                value={filters.severity}
                onChange={(e) => handleFilterChange('severity', e.target.value)}
              >
                <option value="">All Severities</option>
                <option value="emergency">Emergency</option>
                <option value="alert">Alert</option>
                <option value="critical">Critical</option>
                <option value="error">Error</option>
                <option value="warning">Warning</option>
                <option value="notice">Notice</option>
                <option value="info">Info</option>
                <option value="debug">Debug</option>
              </select>
            </div>

            <div className="filter-group">
              <label className="filter-label">Facility</label>
              <select
                className="filter-select"
                value={filters.facility}
                onChange={(e) => handleFilterChange('facility', e.target.value)}
              >
                <option value="">All Facilities</option>
                <option value="kern">Kern</option>
                <option value="user">User</option>
                <option value="mail">Mail</option>
                <option value="daemon">Daemon</option>
                <option value="auth">Auth</option>
                <option value="syslog">Syslog</option>
                <option value="local0">Local0</option>
                <option value="local1">Local1</option>
              </select>
            </div>

            <div className="filter-group">
              <label className="filter-label">Hostname</label>
              <input
                type="text"
                className="filter-input"
                placeholder="Filter by hostname"
                value={filters.hostname}
                onChange={(e) => handleFilterChange('hostname', e.target.value)}
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button className="secondary-button" onClick={handleClearFilters}>
              Clear All
            </button>
            <button className="primary-button" onClick={handleApplyFilters}>
              Apply Filters
            </button>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="error-message" style={{ marginBottom: '24px' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
          <button onClick={() => fetchLogs()}>Retry</button>
        </div>
      )}

      {/* Logs Table */}
      <div className="logs-content">
        {logs.length > 0 ? (
          <LogTable logs={logs} />
        ) : (
          <div className="empty-state">
            <FileText size={48} className="empty-state-icon" />
            <h3 className="empty-state-title">No logs found</h3>
            <p className="empty-state-text">
              Try adjusting your date range or filters
            </p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {logs.length > 0 && (
        <div className="pagination" style={{ marginTop: '24px' }}>
          <div className="pagination-info">
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, total)} of {total.toLocaleString()} logs
          </div>
          <div className="pagination-controls">
            <select
              className="page-size-select"
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
            >
              <option value={25}>25 per page</option>
              <option value={50}>50 per page</option>
              <option value={100}>100 per page</option>
              <option value={200}>200 per page</option>
            </select>

            <div className="pagination-buttons">
              <button
                className="pagination-button"
                onClick={() => setCurrentPage(1)}
                disabled={currentPage === 1}
              >
                First
              </button>
              <button
                className="pagination-button"
                onClick={() => setCurrentPage(prev => prev - 1)}
                disabled={currentPage === 1}
              >
                <ChevronLeft size={18} />
              </button>
              <span className="pagination-current">
                Page {currentPage} of {totalPages}
              </span>
              <button
                className="pagination-button"
                onClick={() => setCurrentPage(prev => prev + 1)}
                disabled={currentPage >= totalPages}
              >
                <ChevronRight size={18} />
              </button>
              <button
                className="pagination-button"
                onClick={() => setCurrentPage(totalPages)}
                disabled={currentPage >= totalPages}
              >
                Last
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
