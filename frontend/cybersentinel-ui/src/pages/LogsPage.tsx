/**
 * Logs Page Component
 * Displays paginated logs with filtering and search capabilities
 */
import React, { useState, useEffect } from 'react';
import {
  RefreshCw,
  Download,
  Filter,
  X,
  ChevronLeft,
  ChevronRight,
  Search as SearchIcon
} from 'lucide-react';
import api from '../services/api';
import { SyslogEntry, SearchParams } from '../types';
import LogTable from '../components/LogTable';
import LoadingSpinner from '../components/LoadingSpinner';
import { parseErrorMessage, exportToCSV, exportToJSON, getStartTime } from '../utils/helpers';

const LogsPage: React.FC = () => {
  const [logs, setLogs] = useState<SyslogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);

  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchParams>({
    severity: '',
    facility: '',
    hostname: '',
    start_time: '',
    end_time: '',
  });

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
        start_time: filters.start_time || undefined,
        end_time: filters.end_time || undefined,
        size: pageSize,
        from: (currentPage - 1) * pageSize,
      };

      const response = await api.searchLogs(params);

      const logEntries = response.hits.hits.map((hit: any) => ({
        id: hit._id,
        ...hit._source,
      }));

      setLogs(logEntries);
      setTotal(response.hits.total.value);
    } catch (err) {
      setError(parseErrorMessage(err));
      console.error('Failed to fetch logs:', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [currentPage, pageSize]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchLogs(false);
    }, 30000);

    return () => clearInterval(interval);
  }, [currentPage, pageSize, searchQuery, filters]);

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
      severity: log.severity,
      facility: log.facility,
      hostname: log.hostname,
      app_name: log.app_name || '',
      message: log.message,
      threat_detected: log.threat_detected || false,
      threat_type: log.threat_type || '',
    }));

    exportToCSV(exportData, `logs_export_${new Date().toISOString()}`);
  };

  const handleExportJSON = () => {
    if (logs.length === 0) return;
    exportToJSON(logs, `logs_export_${new Date().toISOString()}`);
  };

  const handleQuickFilter = (minutes: number) => {
    const startTime = getStartTime(minutes);
    setFilters(prev => ({ ...prev, start_time: startTime, end_time: '' }));
    setCurrentPage(1);
    fetchLogs();
  };

  const totalPages = Math.ceil(total / pageSize);
  const hasActiveFilters = !!(
    searchQuery ||
    filters.severity ||
    filters.facility ||
    filters.hostname ||
    filters.start_time ||
    filters.end_time
  );

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Loading logs..." />;
  }

  return (
    <div className="logs-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Logs</h1>
          <p className="page-subtitle">
            {total.toLocaleString()} total logs found
          </p>
        </div>
        <div className="page-actions">
          <button
            className="action-button"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter size={18} />
            Filters
            {hasActiveFilters && <span className="filter-badge">Active</span>}
          </button>
          <button
            className="action-button"
            onClick={() => fetchLogs(false)}
            disabled={isRefreshing}
          >
            <RefreshCw size={18} className={isRefreshing ? 'spinning' : ''} />
            Refresh
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

      <div className="search-section">
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

        <div className="quick-filters">
          <span className="quick-filter-label">Quick filters:</span>
          <button className="quick-filter-button" onClick={() => handleQuickFilter(15)}>
            Last 15min
          </button>
          <button className="quick-filter-button" onClick={() => handleQuickFilter(60)}>
            Last 1h
          </button>
          <button className="quick-filter-button" onClick={() => handleQuickFilter(240)}>
            Last 4h
          </button>
          <button className="quick-filter-button" onClick={() => handleQuickFilter(1440)}>
            Last 24h
          </button>
        </div>
      </div>

      {showFilters && (
        <div className="filters-panel">
          <div className="filters-header">
            <h3>Advanced Filters</h3>
            <button className="close-button" onClick={() => setShowFilters(false)}>
              <X size={18} />
            </button>
          </div>
          <div className="filters-grid">
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

            <div className="filter-group">
              <label className="filter-label">Start Time</label>
              <input
                type="datetime-local"
                className="filter-input"
                value={filters.start_time ? new Date(filters.start_time).toISOString().slice(0, 16) : ''}
                onChange={(e) => handleFilterChange('start_time', e.target.value ? new Date(e.target.value).toISOString() : '')}
              />
            </div>

            <div className="filter-group">
              <label className="filter-label">End Time</label>
              <input
                type="datetime-local"
                className="filter-input"
                value={filters.end_time ? new Date(filters.end_time).toISOString().slice(0, 16) : ''}
                onChange={(e) => handleFilterChange('end_time', e.target.value ? new Date(e.target.value).toISOString() : '')}
              />
            </div>
          </div>
          <div className="filters-actions">
            <button className="secondary-button" onClick={handleClearFilters}>
              Clear All
            </button>
            <button className="primary-button" onClick={handleApplyFilters}>
              Apply Filters
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button onClick={() => fetchLogs()}>Retry</button>
        </div>
      )}

      <div className="logs-content">
        <LogTable logs={logs} />
      </div>

      {logs.length > 0 && (
        <div className="pagination">
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

export default LogsPage;
