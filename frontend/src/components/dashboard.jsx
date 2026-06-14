import React from 'react';
import { Card, Badge } from './common';
import { formatBytes, formatPercentage, getStatusColor } from '../utils/helpers';
import { Activity, AlertCircle, CheckCircle } from 'lucide-react';

export const MetricsCard = ({ title, value, unit = '', change = null, icon: Icon, className = '' }) => {
  const isPositive = change?.value > 0;

  return (
    <Card className={`p-6 animate-fade-in ${className}`}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="stat-label">{title}</p>
          <div className="flex items-baseline gap-2 mt-3">
            <span className="stat-value">{value}</span>
            {unit && <span className="text-dark-400 text-sm">{unit}</span>}
          </div>
        </div>
        {Icon && (
          <div className="p-3 bg-primary-600/20 rounded-lg">
            <Icon className="w-6 h-6 text-primary-400" />
          </div>
        )}
      </div>
      {change && (
        <div className="flex items-center gap-2 text-sm">
          <span className={isPositive ? 'text-green-400' : 'text-red-400'}>
            {isPositive ? '↑' : '↓'} {Math.abs(change.value)}{change.unit}
          </span>
          <span className="text-dark-400">{change.label}</span>
        </div>
      )}
    </Card>
  );
};

export const ChartCard = ({ title, children, className = '' }) => {
  return (
    <Card className={`p-6 animate-fade-in ${className}`}>
      <h3 className="text-lg font-semibold mb-4 text-white">{title}</h3>
      <div className="w-full h-80">
        {children}
      </div>
    </Card>
  );
};

export const HostCard = ({ host, onSelect, selected }) => {
  const isOnline = host.last_seen_seconds_ago != null && host.last_seen_seconds_ago <= 60;
  const lastSeenMinutes = host.last_seen_seconds_ago != null ? Math.floor(host.last_seen_seconds_ago / 60) : null;
  const lastSeenText = host.last_seen_seconds_ago == null
    ? 'Unknown'
    : lastSeenMinutes >= 1
      ? `${lastSeenMinutes}m ${host.last_seen_seconds_ago % 60}s ago`
      : `${host.last_seen_seconds_ago}s ago`;

  return (
    <Card
      className={`p-5 cursor-pointer transition-all ${selected ? 'border-primary-500 border-2' : 'border border-white/10'} hover:border-primary-500`}
      onClick={() => onSelect(host.hostname)}
    >
      <div className="flex items-start justify-between gap-3 mb-4">
        <div>
          <h4 className="font-semibold text-white truncate">{host.hostname}</h4>
          <p className="text-sm text-dark-400 truncate">{host.operating_system}</p>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${isOnline ? 'bg-emerald-500/15 text-emerald-300' : 'bg-red-500/15 text-red-300'}`}>
          {isOnline ? 'Online' : 'Offline'}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4">
        {[
          { label: 'CPU', value: `${host.cpu_usage}%` },
          { label: 'Memory', value: `${host.memory_usage}%` },
          { label: 'Disk', value: `${host.disk_usage}%` },
        ].map((item) => (
          <div key={item.label} className="rounded-xl bg-dark-700/60 p-3">
            <p className="text-xs text-dark-400">{item.label}</p>
            <p className="text-base font-semibold text-white mt-1">{item.value}</p>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between text-sm text-dark-400">
        <span>Last seen</span>
        <span className="text-white">{lastSeenText}</span>
      </div>
    </Card>
  );
};

export const ContainerCard = ({
  id,
  name,
  image,
  status,
  cpu,
  memory,
  uptime,
  onClick,
  onAction,
}) => {
  const statusBadgeClass = getStatusColor(status);

  return (
    <Card
      className="p-5 hover:shadow-glow-lg cursor-pointer animate-fade-in"
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-white truncate">{name}</h4>
          <p className="text-xs text-dark-400 truncate">{image}</p>
        </div>
        <Badge variant={status === 'running' ? 'success' : status === 'stopped' ? 'error' : 'warning'}>
          {status}
        </Badge>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-dark-400">CPU</span>
          <span className="text-white font-medium">{formatPercentage(cpu)}</span>
        </div>
        <div className="w-full bg-dark-700 rounded-full h-2">
          <div
            className="bg-primary-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${Math.min(cpu * 100, 100)}%` }}
          />
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-dark-400">Memory</span>
          <span className="text-white font-medium">{formatBytes(memory)}</span>
        </div>
        <div className="w-full bg-dark-700 rounded-full h-2">
          <div
            className="bg-cyan-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${Math.min((memory / (1024 * 1024 * 1024)) * 100, 100)}%` }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-white/10">
        <span className="text-xs text-dark-400">Uptime: {uptime}</span>
        <div className="flex gap-2">
          {status === 'running' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onAction?.('stop');
              }}
              className="btn-secondary px-3 py-1 text-xs"
            >
              Stop
            </button>
          )}
          {status === 'stopped' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onAction?.('start');
              }}
              className="btn-primary px-3 py-1 text-xs"
            >
              Start
            </button>
          )}
        </div>
      </div>
    </Card>
  );
};

export const DeploymentCard = ({ deployment, onAction }) => {
  const statusIcon = {
    completed: <CheckCircle className="w-4 h-4 text-green-400" />,
    in_progress: <Activity className="w-4 h-4 text-blue-400 animate-spin" />,
    failed: <AlertCircle className="w-4 h-4 text-red-400" />,
  };

  const statusColor = {
    completed: 'bg-green-900/30 text-green-400',
    in_progress: 'bg-blue-900/30 text-blue-400',
    failed: 'bg-red-900/30 text-red-400',
  };

  return (
    <Card className="p-4 animate-fade-in">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          {statusIcon[deployment.status]}
          <div>
            <h4 className="font-semibold text-white">{deployment.name}</h4>
            <p className="text-xs text-dark-400">{deployment.version}</p>
          </div>
        </div>
        <span className={`badge-info text-xs px-2 py-1 rounded ${statusColor[deployment.status]}`}>
          {deployment.status}
        </span>
      </div>

      <div className="space-y-2 text-sm mb-3">
        <div className="flex justify-between">
          <span className="text-dark-400">Environment:</span>
          <span className="text-white">{deployment.environment}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-dark-400">Deployed:</span>
          <span className="text-white">{new Date(deployment.deployed_at).toLocaleDateString()}</span>
        </div>
      </div>

      {deployment.status === 'in_progress' && (
        <div className="w-full bg-dark-700 rounded-full h-2 mb-3">
          <div
            className="bg-primary-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${deployment.progress || 0}%` }}
          />
        </div>
      )}

      <div className="flex gap-2">
        {deployment.status === 'completed' && (
          <button onClick={() => onAction?.('rollback')} className="btn-secondary w-full text-xs py-1">
            Rollback
          </button>
        )}
        {deployment.status === 'failed' && (
          <button onClick={() => onAction?.('retry')} className="btn-primary w-full text-xs py-1">
            Retry
          </button>
        )}
      </div>
    </Card>
  );
};

export const IncidentCard = ({ incident, onAction }) => {
  const priorityColor = {
    critical: 'text-red-400 bg-red-900/30',
    high: 'text-orange-400 bg-orange-900/30',
    medium: 'text-yellow-400 bg-yellow-900/30',
    low: 'text-blue-400 bg-blue-900/30',
  };

  return (
    <Card className="p-4 animate-fade-in">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h4 className="font-semibold text-white">{incident.title}</h4>
          <p className="text-sm text-dark-400 mt-1">{incident.description}</p>
        </div>
        <span className={`badge-info text-xs px-2 py-1 rounded ${priorityColor[incident.priority]}`}>
          {incident.priority}
        </span>
      </div>

      <div className="space-y-2 text-sm mb-3">
        <div className="flex justify-between">
          <span className="text-dark-400">Service:</span>
          <span className="text-white">{incident.service}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-dark-400">Detected:</span>
          <span className="text-white">{new Date(incident.detected_at).toLocaleString()}</span>
        </div>
      </div>

      <div className="flex gap-2">
        <button onClick={() => onAction?.('details')} className="btn-secondary w-full text-xs py-1">
          View
        </button>
        {incident.status !== 'resolved' && (
          <button onClick={() => onAction?.('resolve')} className="btn-primary text-xs py-1 flex-1">
            Resolve
          </button>
        )}
      </div>
    </Card>
  );
};

export const ActivityLog = ({ activities }) => {
  return (
    <Card className="p-6 animate-fade-in">
      <h3 className="text-lg font-semibold mb-4 text-white">Recent Activity</h3>
      <div className="space-y-4">
        {activities && activities.map((activity, idx) => (
          <div key={idx} className="flex items-start gap-3 pb-4 border-b border-white/10 last:border-0">
            <div className="w-2 h-2 rounded-full bg-primary-500 mt-2" />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white font-medium">{activity.action}</p>
              <p className="text-xs text-dark-400 mt-1">{activity.resource}</p>
              <p className="text-xs text-dark-500 mt-1">{new Date(activity.timestamp).toLocaleString()}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export const StatBox = ({ label, value, unit = '', trend }) => {
  return (
    <div className="glass-card p-4 text-center">
      <p className="stat-label text-xs">{label}</p>
      <p className="stat-value text-2xl mt-2">
        {value}
        {unit && <span className="text-dark-400 text-lg ml-1">{unit}</span>}
      </p>
      {trend && (
        <p className={`text-xs mt-2 ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
        </p>
      )}
    </div>
  );
};
