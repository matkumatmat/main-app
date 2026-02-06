import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002/api/admin';
const ADMIN_HASH_KEY = import.meta.env.VITE_ADMIN_HASH_KEY || 'e735701752cf53d884140a8993418caa04dbad43ac5ed134144583e79b2105fe';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-Admin-Key': ADMIN_HASH_KEY,
  },
  timeout: 30000,
});

apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    if (error.response) {
      console.error(`[API Error] ${error.response.status}:`, error.response.data);

      if (error.response.status === 401) {
        console.error('Authentication failed - invalid admin key');
      } else if (error.response.status === 404) {
        console.error('Resource not found');
      } else if (error.response.status >= 500) {
        console.error('Server error occurred');
      }
    } else if (error.request) {
      console.error('[API Error] No response received:', error.message);
    } else {
      console.error('[API Error]:', error.message);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
