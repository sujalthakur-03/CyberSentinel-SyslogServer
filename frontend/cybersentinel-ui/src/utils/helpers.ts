/**
 * Utility Helper Functions
 * Common utility functions used throughout the application
 */
import { SeverityLevel } from '../types';
/**
 * Format timestamp to human-readable format in IST (Indian Standard Time)
 * Converts UTC timestamps to IST (Asia/Kolkata) timezone
 *
 * IMPORTANT: OpenSearch stores timestamps in UTC format without 'Z' suffix
 * We must explicitly treat them as UTC before converting to IST
 */
export const formatTimestamp = (timestamp: string): string => {
  try {
    // Ensure timestamp is treated as UTC
    // If no timezone indicator (Z or +/-), append 'Z' to treat as UTC
    let utcTimestamp = timestamp;

    if (!timestamp.endsWith('Z') && !timestamp.includes('+') && !timestamp.includes('T00:00:00')) {
      // Check if it has 'T' (ISO format) but no timezone
      if (timestamp.includes('T')) {
        utcTimestamp = timestamp + 'Z';
      }
    }

    // Parse the timestamp as UTC
    const date = new Date(utcTimestamp);

    // Check if date is valid
    if (isNaN(date.getTime())) {
      console.warn('Invalid timestamp:', timestamp);
      return timestamp;
    }

    // Format in IST timezone (UTC+5:30)
    const formattedDate = date.toLocaleString('en-GB', {
      timeZone: 'Asia/Kolkata',
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });

    // Return formatted timestamp (clean format without comma)
    return formattedDate.replace(',', '');
  } catch (error) {
    console.error('Error formatting timestamp:', error, timestamp);
    return timestamp;
  }
};
/**
 * Format timestamp to ISO format for API calls
 */
export const formatISOTimestamp = (date: Date): string => {
  return date.toISOString();
};
/**
 * Get relative time (e.g., "2 hours ago")
 */
export const getRelativeTime = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    if (diffSecs < 60) {
      return `${diffSecs} seconds ago`;
    } else if (diffMins < 60) {
      return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else {
      return formatTimestamp(timestamp);
    }
  } catch (error) {
    return timestamp;
  }
};
/**
 * Get color for severity level
 */
export const getSeverityColor = (severity: string): string => {
  const severityLower = severity.toLowerCase();
  const colorMap: Record<string, string> = {
    emergency: '#dc2626',
    alert: '#ea580c',
    critical: '#f97316',
    error: '#ef4444',
    warning: '#f59e0b',
    notice: '#3b82f6',
    info: '#10b981',
    debug: '#6b7280',
  };
  return colorMap[severityLower] || '#6b7280';
};
/**
 * Get background color for severity level (lighter version)
 */
export const getSeverityBgColor = (severity: string): string => {
  const severityLower = severity.toLowerCase();
  const colorMap: Record<string, string> = {
    emergency: '#fee2e2',
    alert: '#ffedd5',
    critical: '#fed7aa',
    error: '#fecaca',
    warning: '#fef3c7',
    notice: '#dbeafe',
    info: '#d1fae5',
    debug: '#f3f4f6',
  };
  return colorMap[severityLower] || '#f3f4f6';
};
/**
 * Get severity icon
 */
export const getSeverityIcon = (severity: string): string => {
  const severityLower = severity.toLowerCase();
  const iconMap: Record<string, string> = {
    emergency: '🔴',
    alert: '🟠',
    critical: '🟠',
    error: '🔴',
    warning: '🟡',
    notice: '🔵',
    info: '🟢',
    debug: '⚪',
  };
  return iconMap[severityLower] || '⚪';
};
/**
 * Truncate text to specified length
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};
/**
 * Format large numbers with commas
 */
export const formatNumber = (num: number): string => {
  return num.toLocaleString('en-US');
};
/**
 * Format bytes to human-readable size
 */
export const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};
/**
 * Calculate percentage
 */
export const calculatePercentage = (value: number, total: number): number => {
  if (total === 0) return 0;
  return Math.round((value / total) * 100 * 10) / 10;
};
/**
 * Debounce function for search inputs
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};
/**
 * Export data to CSV
 */
export const exportToCSV = (data: any[], filename: string): void => {
  if (data.length === 0) return;
  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(','),
    ...data.map(row =>
      headers.map(header => {
        const value = row[header];
        const stringValue = typeof value === 'object' ? JSON.stringify(value) : String(value);
        return `"${stringValue.replace(/"/g, '""')}"`;
      }).join(',')
    )
  ].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
/**
 * Export data to JSON
 */
export const exportToJSON = (data: any, filename: string): void => {
  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}.json`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
/**
 * Parse error message from API response
 */
export const parseErrorMessage = (error: any): string => {
  if (error.response?.data?.detail) {
    return typeof error.response.data.detail === 'string'
      ? error.response.data.detail
      : JSON.stringify(error.response.data.detail);
  }
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};
/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};
/**
 * Generate time range options for filters
 */
export const getTimeRangeOptions = () => {
  return [
    { label: 'Last 15 minutes', value: 15 },
    { label: 'Last 30 minutes', value: 30 },
    { label: 'Last 1 hour', value: 60 },
    { label: 'Last 4 hours', value: 240 },
    { label: 'Last 12 hours', value: 720 },
    { label: 'Last 24 hours', value: 1440 },
    { label: 'Last 7 days', value: 10080 },
    { label: 'Last 30 days', value: 43200 },
  ];
};
/**
 * Get start time based on time range in minutes
 */
export const getStartTime = (minutes: number): string => {
  const date = new Date();
  date.setMinutes(date.getMinutes() - minutes);
  return formatISOTimestamp(date);
};
/**
 * Highlight search text in string
 */
export const highlightText = (text: string, search: string): string => {
  if (!search) return text;
  const regex = new RegExp(`(${search})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
};
/**
 * Deep clone object
 */
export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj));
};
/**
 * Check if object is empty
 */
export const isEmpty = (obj: any): boolean => {
  return Object.keys(obj).length === 0;
};
/**
 * Get threat severity level
 */
export const getThreatSeverity = (score: number): 'low' | 'medium' | 'high' | 'critical' => {
  if (score >= 0.8) return 'critical';
  if (score >= 0.6) return 'high';
  if (score >= 0.4) return 'medium';
  return 'low';
};
/**
 * Format threat score as percentage
 */
export const formatThreatScore = (score: number): string => {
  return `${Math.round(score * 100)}%`;
};
/**
 * Extract device name from FortiGate log message
 * Looks for devname="DEVICE_NAME" pattern in the message
 */
export const extractDeviceName = (message: string): string | null => {
  if (!message) return null;
  // Match devname="DEVICE_NAME" pattern
  const match = message.match(/devname="([^"]+)"/);
  return match ? match[1] : null;
};
