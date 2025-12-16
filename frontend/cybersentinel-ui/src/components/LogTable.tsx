import React, { useState } from 'react';
import { SyslogEntry } from '../types';
import { formatTimestamp, getSeverityColor, truncateText, extractDeviceName } from '../utils/helpers';
import { Eye, AlertTriangle } from 'lucide-react';
interface LogTableProps {
  logs: SyslogEntry[];
  onLogClick?: (log: SyslogEntry) => void;
  maxHeight?: string;
}
const LogTable: React.FC<LogTableProps> = ({ logs, onLogClick, maxHeight = '600px' }) => {
  const [selectedLog, setSelectedLog] = useState<SyslogEntry | null>(null);
  const handleRowClick = (log: SyslogEntry) => {
    setSelectedLog(log);
    if (onLogClick) {
      onLogClick(log);
    }
  };
  const closeModal = () => {
    setSelectedLog(null);
  };
  if (logs.length === 0) {
    return (
      <div className="empty-state">
        <p>No logs found</p>
      </div>
    );
  }
  return (
    <>
      <div className="log-table-container" style={{ maxHeight }}>
        <table className="log-table">
          <thead>
            <tr>
              <th>Timestamp (IST)</th>
              <th>Severity</th>
              <th>Hostname</th>
              <th>Facility</th>
              <th>Message</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, index) => {
              const deviceName = extractDeviceName(log.message);
              return (
                <tr
                  key={log.id || index}
                  className={log.has_threat_indicators ? 'threat-row' : ''}
                  onClick={() => handleRowClick(log)}
                >
                  <td className="timestamp-cell">
                    {formatTimestamp(log.timestamp)}
                  </td>
                  <td>
                    <span
                      className="severity-badge"
                      style={{
                        backgroundColor: getSeverityColor(log.severity_name || log.severity),
                        color: '#fff'
                      }}
                    >
                      {log.severity_name || log.severity}
                    </span>
                  </td>
                  <td>{deviceName || log.hostname}</td>
                  <td>{log.facility_name || log.facility}</td>
                  <td className="message-cell">
                    {log.has_threat_indicators && (
                      <AlertTriangle size={16} className="threat-icon" />
                    )}
                    {truncateText(log.message, 100)}
                  </td>
                  <td>
                    <button
                      className="icon-button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRowClick(log);
                      }}
                      title="View details"
                    >
                      <Eye size={18} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {selectedLog && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Log Details</h2>
              <button className="modal-close" onClick={closeModal}>×</button>
            </div>
            <div className="modal-body">
              <div className="log-detail-grid">
                <div className="log-detail-item">
                  <strong>Timestamp:</strong>
                  <span>{formatTimestamp(selectedLog.timestamp)}</span>
                </div>
                <div className="log-detail-item">
                  <strong>Severity:</strong>
                  <span
                    className="severity-badge"
                    style={{
                      backgroundColor: getSeverityColor(selectedLog.severity_name || selectedLog.severity),
                      color: '#fff'
                    }}
                  >
                    {selectedLog.severity_name || selectedLog.severity}
                  </span>
                </div>
                <div className="log-detail-item">
                  <strong>Hostname:</strong>
                  <span>{selectedLog.hostname}</span>
                </div>
                <div className="log-detail-item">
                  <strong>Facility:</strong>
                  <span>{selectedLog.facility_name || selectedLog.facility}</span>
                </div>
                {selectedLog.app_name && (
                  <div className="log-detail-item">
                    <strong>Application:</strong>
                    <span>{selectedLog.app_name}</span>
                  </div>
                )}
                {selectedLog.proc_id && (
                  <div className="log-detail-item">
                    <strong>Process ID:</strong>
                    <span>{selectedLog.proc_id}</span>
                  </div>
                )}
                {selectedLog.has_threat_indicators && (
                  <>
                    <div className="log-detail-item threat-item">
                      <strong>Threat Keywords:</strong>
                      <span className="threat-badge">{selectedLog.threat_keywords?.join(', ') || 'N/A'}</span>
                    </div>
                    <div className="log-detail-item threat-item">
                      <strong>Threat Score:</strong>
                      <span className="threat-score">
                        {selectedLog.threat_score || 0}
                      </span>
                    </div>
                  </>
                )}
                <div className="log-detail-item full-width">
                  <strong>Message:</strong>
                  <pre className="log-message">{selectedLog.message}</pre>
                </div>
                {selectedLog.raw_message && (
                  <div className="log-detail-item full-width">
                    <strong>Raw Message:</strong>
                    <pre className="log-message">{selectedLog.raw_message}</pre>
                  </div>
                )}
                {selectedLog.structured_data && Object.keys(selectedLog.structured_data).length > 0 && (
                  <div className="log-detail-item full-width">
                    <strong>Structured Data:</strong>
                    <pre className="log-message">
                      {JSON.stringify(selectedLog.structured_data, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
export default LogTable;
