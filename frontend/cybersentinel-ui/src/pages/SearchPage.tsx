/**
 * Search Page Component
 * Advanced search interface with multiple filter options and saved searches
 */
import React, { useState } from 'react';
import { Search as SearchIcon, Save, X, Clock, Trash2 } from 'lucide-react';
import api from '../services/api';
import { SyslogEntry, SearchParams, SavedSearch } from '../types';
import LogTable from '../components/LogTable';
import LoadingSpinner from '../components/LoadingSpinner';
import { parseErrorMessage, exportToCSV, exportToJSON } from '../utils/helpers';

const SearchPage: React.FC = () => {
  const [logs, setLogs] = useState<SyslogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState('');

  const [searchParams, setSearchParams] = useState<SearchParams>({
    query: '',
    severity: '',
    facility: '',
    hostname: '',
    start_time: '',
    end_time: '',
    size: 100,
  });

  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>(() => {
    const saved = localStorage.getItem('savedSearches');
    return saved ? JSON.parse(saved) : [];
  });

  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [searchName, setSearchName] = useState('');
  const [searchDescription, setSearchDescription] = useState('');

  const handleParamChange = (key: keyof SearchParams, value: string | number) => {
    setSearchParams(prev => ({ ...prev, [key]: value }));
  };

  const handleSearch = async () => {
    setIsSearching(true);
    setError('');

    try {
      const params = {
        ...searchParams,
        query: searchParams.query || undefined,
        severity: searchParams.severity || undefined,
        facility: searchParams.facility || undefined,
        hostname: searchParams.hostname || undefined,
        start_time: searchParams.start_time || undefined,
        end_time: searchParams.end_time || undefined,
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
      console.error('Search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleClearSearch = () => {
    setSearchParams({
      query: '',
      severity: '',
      facility: '',
      hostname: '',
      start_time: '',
      end_time: '',
      size: 100,
    });
    setLogs([]);
    setTotal(0);
    setError('');
  };

  const handleSaveSearch = () => {
    if (!searchName) {
      alert('Please enter a name for this search');
      return;
    }

    const newSearch: SavedSearch = {
      id: Date.now().toString(),
      name: searchName,
      description: searchDescription,
      params: { ...searchParams },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const updated = [...savedSearches, newSearch];
    setSavedSearches(updated);
    localStorage.setItem('savedSearches', JSON.stringify(updated));

    setShowSaveDialog(false);
    setSearchName('');
    setSearchDescription('');
  };

  const handleLoadSearch = (search: SavedSearch) => {
    setSearchParams(search.params);
  };

  const handleDeleteSearch = (id: string) => {
    const updated = savedSearches.filter(s => s.id !== id);
    setSavedSearches(updated);
    localStorage.setItem('savedSearches', JSON.stringify(updated));
  };

  return (
    <div className="search-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Advanced Search</h1>
          <p className="page-subtitle">
            Search and filter logs with advanced criteria
          </p>
        </div>
      </div>

      <div className="search-layout">
        <div className="search-sidebar">
          <div className="search-form-section">
            <h3 className="section-title">Search Criteria</h3>

            <div className="form-group">
              <label className="form-label">Search Query</label>
              <input
                type="text"
                className="form-input"
                placeholder="Enter search terms..."
                value={searchParams.query}
                onChange={(e) => handleParamChange('query', e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Severity</label>
              <select
                className="form-select"
                value={searchParams.severity}
                onChange={(e) => handleParamChange('severity', e.target.value)}
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

            <div className="form-group">
              <label className="form-label">Facility</label>
              <select
                className="form-select"
                value={searchParams.facility}
                onChange={(e) => handleParamChange('facility', e.target.value)}
              >
                <option value="">All Facilities</option>
                <option value="kern">Kernel</option>
                <option value="user">User</option>
                <option value="mail">Mail</option>
                <option value="daemon">Daemon</option>
                <option value="auth">Auth</option>
                <option value="syslog">Syslog</option>
                <option value="local0">Local0</option>
                <option value="local1">Local1</option>
                <option value="local2">Local2</option>
                <option value="local3">Local3</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Hostname</label>
              <input
                type="text"
                className="form-input"
                placeholder="Filter by hostname"
                value={searchParams.hostname}
                onChange={(e) => handleParamChange('hostname', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Start Time</label>
              <input
                type="datetime-local"
                className="form-input"
                value={searchParams.start_time ? new Date(searchParams.start_time).toISOString().slice(0, 16) : ''}
                onChange={(e) => handleParamChange('start_time', e.target.value ? new Date(e.target.value).toISOString() : '')}
              />
            </div>

            <div className="form-group">
              <label className="form-label">End Time</label>
              <input
                type="datetime-local"
                className="form-input"
                value={searchParams.end_time ? new Date(searchParams.end_time).toISOString().slice(0, 16) : ''}
                onChange={(e) => handleParamChange('end_time', e.target.value ? new Date(e.target.value).toISOString() : '')}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Max Results</label>
              <select
                className="form-select"
                value={searchParams.size}
                onChange={(e) => handleParamChange('size', Number(e.target.value))}
              >
                <option value={50}>50</option>
                <option value={100}>100</option>
                <option value={200}>200</option>
                <option value={500}>500</option>
                <option value={1000}>1000</option>
              </select>
            </div>

            <div className="form-actions">
              <button
                className="primary-button full-width"
                onClick={handleSearch}
                disabled={isSearching}
              >
                <SearchIcon size={18} />
                {isSearching ? 'Searching...' : 'Search'}
              </button>
              <button
                className="secondary-button full-width"
                onClick={handleClearSearch}
              >
                <X size={18} />
                Clear
              </button>
              <button
                className="secondary-button full-width"
                onClick={() => setShowSaveDialog(true)}
                disabled={!searchParams.query && !searchParams.severity && !searchParams.facility}
              >
                <Save size={18} />
                Save Search
              </button>
            </div>
          </div>

          {savedSearches.length > 0 && (
            <div className="saved-searches-section">
              <h3 className="section-title">Saved Searches</h3>
              <div className="saved-searches-list">
                {savedSearches.map(search => (
                  <div key={search.id} className="saved-search-item">
                    <div className="saved-search-info">
                      <h4 className="saved-search-name">{search.name}</h4>
                      {search.description && (
                        <p className="saved-search-description">{search.description}</p>
                      )}
                      <div className="saved-search-meta">
                        <Clock size={12} />
                        <span>{new Date(search.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="saved-search-actions">
                      <button
                        className="icon-button"
                        onClick={() => handleLoadSearch(search)}
                        title="Load search"
                      >
                        <SearchIcon size={16} />
                      </button>
                      <button
                        className="icon-button danger"
                        onClick={() => handleDeleteSearch(search.id)}
                        title="Delete search"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="search-results">
          {isSearching ? (
            <LoadingSpinner text="Searching..." />
          ) : error ? (
            <div className="error-state">
              <p className="error-message">{error}</p>
              <button onClick={handleSearch} className="retry-button">
                Retry
              </button>
            </div>
          ) : logs.length > 0 ? (
            <>
              <div className="results-header">
                <h3>Search Results</h3>
                <div className="results-actions">
                  <span className="results-count">
                    {total.toLocaleString()} results found
                  </span>
                  <button
                    className="action-button"
                    onClick={() => exportToCSV(logs, `search_results_${new Date().toISOString()}`)}
                  >
                    Export CSV
                  </button>
                  <button
                    className="action-button"
                    onClick={() => exportToJSON(logs, `search_results_${new Date().toISOString()}`)}
                  >
                    Export JSON
                  </button>
                </div>
              </div>
              <LogTable logs={logs} />
            </>
          ) : (
            <div className="empty-state">
              <SearchIcon size={64} className="empty-icon" />
              <h3>No results yet</h3>
              <p>Enter your search criteria and click Search to find logs</p>
            </div>
          )}
        </div>
      </div>

      {showSaveDialog && (
        <div className="modal-overlay" onClick={() => setShowSaveDialog(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Save Search</h2>
              <button className="modal-close" onClick={() => setShowSaveDialog(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Search Name</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Enter a name for this search"
                  value={searchName}
                  onChange={(e) => setSearchName(e.target.value)}
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label className="form-label">Description (optional)</label>
                <textarea
                  className="form-textarea"
                  placeholder="Describe what this search is for"
                  value={searchDescription}
                  onChange={(e) => setSearchDescription(e.target.value)}
                  rows={3}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="secondary-button"
                onClick={() => setShowSaveDialog(false)}
              >
                Cancel
              </button>
              <button
                className="primary-button"
                onClick={handleSaveSearch}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
