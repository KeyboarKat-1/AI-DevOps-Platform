export const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

export const formatPercentage = (value, decimals = 1) => {
  return (Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)).toFixed(decimals) + '%';
};

export const formatUptime = (seconds) => {
  if (!seconds) return '0s';
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);

  return parts.slice(0, 2).join(' ');
};

export const getStatusColor = (status) => {
  const statusMap = {
    running: 'bg-green-900/30 text-green-400 border-green-700/30',
    stopped: 'bg-red-900/30 text-red-400 border-red-700/30',
    paused: 'bg-yellow-900/30 text-yellow-400 border-yellow-700/30',
    error: 'bg-red-900/30 text-red-400 border-red-700/30',
    pending: 'bg-blue-900/30 text-blue-400 border-blue-700/30',
    active: 'bg-green-900/30 text-green-400 border-green-700/30',
    inactive: 'bg-gray-900/30 text-gray-400 border-gray-700/30',
  };
  return statusMap[status] || statusMap.inactive;
};

export const getStatusIcon = (status) => {
  const iconMap = {
    running: '▶',
    stopped: '⏹',
    paused: '⏸',
    error: '⚠',
    pending: '⏳',
  };
  return iconMap[status] || '○';
};

export const cn = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

export const truncateText = (text, length = 30) => {
  if (!text) return '';
  return text.length > length ? text.substring(0, length) + '...' : text;
};

export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const calculateCPUUsage = (data) => {
  if (!data || !data.length) return 0;
  return data.reduce((sum, item) => sum + (item.cpu || 0), 0) / data.length;
};

export const calculateMemoryUsage = (data) => {
  if (!data || !data.length) return 0;
  return data.reduce((sum, item) => sum + (item.memory || 0), 0) / data.length;
};

export const getRandomColor = () => {
  const colors = [
    '#0ea5e9',
    '#06b6d4',
    '#10b981',
    '#f59e0b',
    '#ef4444',
    '#8b5cf6',
    '#ec4899',
  ];
  return colors[Math.floor(Math.random() * colors.length)];
};

export const parseJwt = (token) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    return null;
  }
};

export const isTokenExpired = (token) => {
  const decoded = parseJwt(token);
  if (!decoded || !decoded.exp) return true;
  return decoded.exp * 1000 < Date.now();
};

export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
