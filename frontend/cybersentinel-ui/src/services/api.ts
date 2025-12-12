/**
 * API Service for CyberSentinel
 * Handles all HTTP requests to the backend API
 */
import axios, { AxiosInstance } from 'axios';

// Get API URL from runtime config (injected by Docker) or build-time env var
declare global {
  interface Window {
    ENV?: {
      REACT_APP_API_URL?: string;
    };
  }
}

const API_BASE_URL = window.ENV?.REACT_APP_API_URL || process.env.REACT_APP_API_URL || 'http://localhost:8000';

class APIService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load token from localStorage
    this.token = localStorage.getItem('token');
    if (this.token) {
      this.setAuthToken(this.token);
    }

    // Response interceptor for handling errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setAuthToken(token: string) {
    this.token = token;
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('token', token);
  }

  logout() {
    this.token = null;
    delete this.client.defaults.headers.common['Authorization'];
    localStorage.removeItem('token');
  }

  // Authentication
  async login(username: string, password: string) {
    const response = await this.client.post('/auth/login', { username, password });
    this.setAuthToken(response.data.access_token);
    return response.data;
  }

  // Health check
  async getHealth() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Search logs
  async searchLogs(params: {
    query?: string;
    start_time?: string;
    end_time?: string;
    severity?: string;
    facility?: string;
    hostname?: string;
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: string;
  }) {
    console.log('API Service: Searching logs with params:', params);
    console.log('API Service: Using base URL:', API_BASE_URL);
    try {
      const response = await this.client.post('/logs/search', params);
      console.log('API Service: Search successful, response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('API Service: Search failed:', error);
      console.error('API Service: Error response:', error.response?.data);
      throw error;
    }
  }

  // Get statistics
  async getStatistics(hours: number = 24) {
    const response = await this.client.get(`/logs/statistics?hours=${hours}`);
    return response.data;
  }

  // Get threat logs
  async getThreatLogs(params: {
    start_time?: string;
    end_time?: string;
    threat_type?: string;
    size?: number;
  }) {
    const response = await this.client.get('/logs/threats', { params });
    return response.data;
  }

  // Get aggregations
  async getAggregations(field: string, hours: number = 24) {
    const response = await this.client.get(`/logs/aggregations/${field}?hours=${hours}`);
    return response.data;
  }
}

export default new APIService();
