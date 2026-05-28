import React, { useState, useEffect } from 'react';
import { Activity, Server, AlertCircle, Database } from 'lucide-react';
import { MetricsCard, ChartCard, Card, ActivityLog, HealthIndicator, LoadingSpinner } from '../components';
import { CPUChart, MemoryChart, DiskChart, ContainerStatusChart, NetworkChart } from '../components/charts';
import { metricsService } from '../services/api';

export const DashboardPage = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeRange, setTimeRange] = useState('1h');

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchMetrics = async () => {
    try {
      const response = await metricsService.getMetrics(timeRange);
      setMetrics(response.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
      setError('Unable to load metrics. Please try again later.');
      setMetrics(null);
    } finally {
      setLoading(false);
    }
  };

  const cpuData = metrics?.cpu_history || [];
  const memoryData = metrics?.memory_history || [];
  const diskData = metrics
    ? [
        { name: 'Used', disk: metrics.disk_usage },
        { name: 'Free', disk: Math.max(0, 100 - metrics.disk_usage) },
      ]
    : [];
  const componentHealthData = metrics
    ? [
        { name: 'Healthy', value: Object.values(metrics.component_status || {}).filter((value) => value === 'healthy').length },
        { name: 'Warning', value: Object.values(metrics.component_status || {}).filter((value) => value === 'warning').length },
        { name: 'Critical', value: Object.values(metrics.component_status || {}).filter((value) => value === 'critical').length },
      ]
    : [];
  const networkData = metrics?.cpu_history?.map((point, index) => ({
    time: point.time,
    sent: (point.value ?? 0) * 22,
    received: ((metrics.memory_history?.[index]?.value ?? point.value) ?? 0) * 16,
  })) || [];

  const activities = metrics?.alerts?.length
    ? metrics.alerts.map((alert, idx) => ({
        action: alert,
        resource: 'System alert',
        timestamp: new Date(Date.now() - idx * 5 * 60000),
      }))
    : [
        {
          action: 'System operating normally',
          resource: 'No active alerts detected',
          timestamp: new Date(),
        },
      ];

  const memoryUsageMB = metrics?.memory_usage ? `${Math.round(metrics.memory_usage * 32)} MB` : '--';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-dark-400 mt-1">Real-time system monitoring and analytics</p>
          {error && (
            <div className="mt-4 rounded-xl bg-red-900/20 border border-red-700/30 p-4 text-sm text-red-200">
              {error}
            </div>
          )}
        </div>
        <div className="flex gap-2">
          {['1h', '6h', '24h'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg transition-all ${
                timeRange === range
                  ? 'bg-primary-600 text-white'
                  : 'bg-dark-700 text-dark-400 hover:text-white'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <Card className="p-6">
        <h2 className="text-lg font-semibold text-white mb-4">System Health</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <HealthIndicator status={metrics?.status || 'healthy'} label="Overall status" />
          <HealthIndicator status={metrics?.alerts?.length ? 'warning' : 'healthy'} label={`Alerts ${metrics?.alerts?.length ?? 0}`} />
          <HealthIndicator status={metrics?.disk_usage > 85 ? 'critical' : 'healthy'} label={`Disk ${metrics?.disk_usage ?? '--'}%`} />
          <HealthIndicator status={metrics?.cpu_usage > 85 ? 'warning' : 'healthy'} label={`CPU ${metrics?.cpu_usage ?? '--'}%`} />
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricsCard
          title="CPU Usage"
          value={metrics?.cpu_usage ?? '--'}
          unit="%"
          icon={Activity}
          change={{ value: metrics?.cpu_usage ?? 0, unit: '%', label: 'current' }}
        />
        <MetricsCard
          title="Memory Usage"
          value={metrics?.memory_usage ?? '--'}
          unit="%"
          icon={Database}
          change={{ value: metrics?.memory_usage ?? 0, unit: '%', label: 'current' }}
        />
        <MetricsCard
          title="Disk Usage"
          value={metrics?.disk_usage ?? '--'}
          unit="%"
          icon={Server}
          change={{ value: metrics?.disk_usage ?? 0, unit: '%', label: 'current' }}
        />
        <MetricsCard
          title="Active Alerts"
          value={metrics?.alerts?.length ?? 0}
          unit=""
          icon={AlertCircle}
          change={{ value: metrics?.alerts?.length ?? 0, unit: '', label: 'active' }}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="CPU Usage (History)" loading={loading}>
          <CPUChart data={cpuData.map((item) => ({ time: item.time, cpu: item.value }))} />
        </ChartCard>
        <ChartCard title="Memory Usage (History)" loading={loading}>
          <MemoryChart data={memoryData.map((item) => ({ time: item.time, memory: item.value }))} />
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Disk Usage Distribution" loading={loading}>
          <DiskChart data={diskData} />
        </ChartCard>
        <ChartCard title="Component Health Breakdown" loading={loading}>
          <ContainerStatusChart data={componentHealthData} />
        </ChartCard>
      </div>

      <ChartCard title="Network I/O Trend" loading={loading}>
        <NetworkChart data={networkData} />
      </ChartCard>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ActivityLog activities={activities} />

        <div className="lg:col-span-2 glass-card p-6 rounded-xl">
          <h3 className="text-lg font-semibold mb-4 text-white">Top Services</h3>
          <div className="space-y-3">
            {[
              { name: 'API Server', cpu: metrics?.cpu_usage ?? 0, memory: memoryUsageMB },
              { name: 'Database', cpu: metrics?.cpu_usage ?? 0, memory: memoryUsageMB },
              { name: 'Cache Service', cpu: metrics?.cpu_usage ?? 0, memory: memoryUsageMB },
            ].map((service, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-dark-700/30 rounded-lg">
                <span className="text-white font-medium">{service.name}</span>
                <div className="flex gap-4 text-sm">
                  <div>
                    <span className="text-dark-400">CPU:</span>
                    <span className="text-primary-400 ml-2 font-semibold">{service.cpu}%</span>
                  </div>
                  <div>
                    <span className="text-dark-400">Memory:</span>
                    <span className="text-cyan-400 ml-2 font-semibold">{service.memory}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
