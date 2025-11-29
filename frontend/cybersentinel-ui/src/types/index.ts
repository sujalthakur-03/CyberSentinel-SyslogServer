/**
 * TypeScript Type Definitions for CyberSentinel
 * Comprehensive type definitions for all data models in the application
 */

export interface User {
  id: string;
  username: string;
  email?: string;
  role?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user?: User;
}

export interface SyslogEntry {
  id?: string;
  timestamp: string;
  hostname: string;
  facility: string;
  facility_name?: string;
  severity: string;
  severity_name?: string;
  message: string;
  app_name?: string;
  proc_id?: string;
  msg_id?: string;
  structured_data?: Record<string, any>;
  raw_message?: string;
  threat_detected?: boolean;
  threat_type?: string;
  threat_score?: number;
  has_threat_indicators?: boolean;
  threat_keywords?: string[];
}

export interface SearchParams {
  query?: string;
  start_time?: string;
  end_time?: string;
  severity?: string;
  facility?: string;
  hostname?: string;
  size?: number;
  from?: number;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_field?: string;
  sort_order?: 'asc' | 'desc';
}

export interface SearchResponse {
  hits: {
    total: {
      value: number;
      relation: string;
    };
    hits: Array<{
      _id: string;
      _source: SyslogEntry;
      _score?: number;
    }>;
  };
  took: number;
}

export interface Statistics {
  total_logs: number;
  total_errors: number;
  total_warnings: number;
  total_threats: number;
  logs_per_hour: Array<{
    timestamp: string;
    count: number;
  }>;
  severity_distribution: Array<{
    severity: string;
    count: number;
  }>;
  top_hosts: Array<{
    hostname: string;
    count: number;
  }>;
  recent_logs: SyslogEntry[];
}

export interface ThreatLog extends SyslogEntry {
  threat_detected: true;
  threat_type: string;
  threat_score: number;
  threat_indicators?: string[];
}

export interface ThreatParams {
  start_time?: string;
  end_time?: string;
  threat_type?: string;
  size?: number;
  min_score?: number;
}

export interface Aggregation {
  key: string;
  doc_count: number;
  percentage?: number;
}

export interface AggregationResponse {
  field: string;
  buckets: Aggregation[];
  total: number;
}

export interface HealthStatus {
  status: string;
  opensearch: {
    status: string;
    cluster_name?: string;
    nodes?: number;
  };
  kafka?: {
    status: string;
    brokers?: number;
  };
  timestamp: string;
  version?: string;
}

export interface FilterOptions {
  severity: string[];
  facility: string[];
  hostname: string[];
  threatType: string[];
}

export interface SavedSearch {
  id: string;
  name: string;
  description?: string;
  params: SearchParams;
  created_at: string;
  updated_at: string;
}

export interface SystemSettings {
  api_endpoint: string;
  refresh_interval: number;
  logs_per_page: number;
  theme: 'light' | 'dark';
  enable_notifications: boolean;
  enable_auto_refresh: boolean;
}

export interface Alert {
  id: string;
  type: 'threat' | 'error' | 'warning' | 'info';
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  message: string;
  timestamp: string;
  source?: string;
  acknowledged: boolean;
  details?: Record<string, any>;
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  timestamp: string;
  read: boolean;
}

export type SeverityLevel = 'emergency' | 'alert' | 'critical' | 'error' | 'warning' | 'notice' | 'info' | 'debug';

export type FacilityType = 'kern' | 'user' | 'mail' | 'daemon' | 'auth' | 'syslog' | 'lpr' | 'news' | 'uucp' | 'cron' | 'authpriv' | 'ftp' | 'local0' | 'local1' | 'local2' | 'local3' | 'local4' | 'local5' | 'local6' | 'local7';

export type ThreatType = 'sql_injection' | 'xss' | 'brute_force' | 'port_scan' | 'malware' | 'dos' | 'unauthorized_access' | 'data_exfiltration' | 'suspicious_activity';
