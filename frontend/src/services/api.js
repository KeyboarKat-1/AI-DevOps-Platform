import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const deploymentService = {
  getDeployments: () =>
    api.get('/api/deployments'),
  getDeploymentById: (id) =>
    api.get(`/api/deployments/${id}`),
  createDeployment: (data) =>
    api.post('/api/deployments', data),
  updateDeployment: (id, data) =>
    api.put(`/api/deployments/${id}`, data),
  deleteDeployment: (id) =>
    api.delete(`/api/deployments/${id}`),
};

export const dockerService = {
  getContainers: () =>
    api.get('/api/docker/containers'),
  getContainerStats: (containerId) =>
    api.get(`/api/docker/containers/${containerId}/stats`),
  startContainer: (containerId) =>
    api.post(`/api/docker/containers/${containerId}/start`),
  stopContainer: (containerId) =>
    api.post(`/api/docker/containers/${containerId}/stop`),
};

export const metricsService = {
  getMetrics: (timeRange = '1h') =>
    api.get(`/api/metrics?time_range=${timeRange}`),
  getCPUMetrics: (timeRange = '1h') =>
    api.get(`/api/metrics/cpu?time_range=${timeRange}`),
  getMemoryMetrics: (timeRange = '1h') =>
    api.get(`/api/metrics/memory?time_range=${timeRange}`),
  getDiskMetrics: (timeRange = '1h') =>
    api.get(`/api/metrics/disk?time_range=${timeRange}`),
};

export const incidentService = {
  getIncidents: () =>
    api.get('/api/incidents'),
  getIncidentById: (id) =>
    api.get(`/api/incidents/${id}`),
  createIncident: (data) =>
    api.post('/api/incidents', data),
  resolveIncident: (id) =>
    api.put(`/api/incidents/${id}/resolve`),
};

export const profileService = {
  getProfile: () => api.get('/api/me'),
  updateProfile: (payload) => api.put('/api/profile/update', payload),
};

export const insightsService = {
  getInsights: () =>
    api.get('/api/insights'),
  getAISuggestions: (context) =>
    api.post('/api/insights/ai-suggestions', { context }),
};

export const agentMonitoringService = {
  getLatestHosts: () =>
    api.get('/api/agent/metrics/latest'),
  getHostHistory: (hostname, hours = 24) =>
    api.get(`/api/agent/metrics/history/${encodeURIComponent(hostname)}?hours=${hours}`),
};

export const agentInsightsService = {
  getInsights: () => api.get('/api/agent/insights'),
};

export default api;
