import React, { useState, useEffect, useMemo } from 'react';
import { Activity, Server, AlertCircle, Database } from 'lucide-react';
import { HostCard, MetricsCard, ChartCard, Card, ActivityLog, LoadingSpinner } from '../components';
import { agentMonitoringService, agentInsightsService } from '../services/api';
import { CPUChart, MemoryChart, DiskChart, ContainerStatusChart } from '../components/charts';

const hostHealthColor = (value) => {
  if (value >= 90) return 'text-red-400';
  if (value >= 70) return 'text-orange-400';
  return 'text-emerald-400';
};

export const AgentDashboardPage = () => {
  const [hosts, setHosts] = useState([]);
  const [selectedHost, setSelectedHost] = useState(null);
  const [hostHistory, setHostHistory] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('');
  const [refreshCounter, setRefreshCounter] = useState(0);

  useEffect(() => {
    fetchHostData();
    const interval = setInterval(() => setRefreshCounter((prev) => prev + 1), 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (refreshCounter > 0) {
      fetchHostData();
    }
  }, [refreshCounter]);

  useEffect(() => {
    if (selectedHost) {
      fetchHostHistory(selectedHost);
    }
  }, [selectedHost]);

  const fetchHostData = async () => {
    setLoading(true);
    setError('');
    try {
      const [hostsResponse, insightsResponse] = await Promise.all([
        agentMonitoringService.getLatestHosts(),
        agentInsightsService.getInsights(),
      ]);
      setHosts(hostsResponse.data.hostnames || []);
      setInsights(insightsResponse.data);
      if (!selectedHost && hostsResponse.data.hostnames?.length > 0) {
        setSelectedHost(hostsResponse.data.hostnames[0].hostname);
      }
    } catch (err) {
      console.error('Error fetching agent monitoring data:', err);
      setError('Unable to load agent metrics. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchHostHistory = async (hostname) => {
    try {
      const response = await agentMonitoringService.getHostHistory(hostname, 24);
      setHostHistory(response.data.metrics || []);
    } catch (err) {
      console.error('Error fetching host history:', err);
      setHostHistory([]);
    }
  };

  const filteredHosts = useMemo(() => {
    return hosts.filter((host) => host.hostname.toLowerCase().includes(filter.toLowerCase()));
  }, [hosts, filter]);

  const selectedMetrics = hosts.find((host) => host.hostname === selectedHost) || {};
  const cpuHistory = hostHistory.map((item) => ({ time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), cpu: item.cpu_usage }));
  const memoryHistory = hostHistory.map((item) => ({ time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), memory: item.memory_usage }));
  const diskHistory = hostHistory.map((item) => ({ time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), disk: item.disk_usage }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Agent Monitoring</h1>
          <p className="text-dark-400 mt-1">Monitor your agents across all installed machines.</p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter by hostname"
            className="input-field bg-dark-800 px-4 py-2 rounded-xl w-full max-w-sm"
          />
          <button
            onClick={fetchHostData}
            className="btn-secondary"
          >
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl bg-red-900/20 border border-red-700/30 p-4 text-sm text-red-200">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-[300px_1fr] gap-6">
        <div className="space-y-4">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-white">Monitored Hosts</h2>
                <p className="text-dark-400 text-sm">{hosts.length} host(s) reporting</p>
              </div>
              <span className="text-dark-400 text-sm">Auto-refresh every 10s</span>
            </div>

            <div className="space-y-3 max-h-[520px] overflow-y-auto pr-2">
              {loading ? (
                <div className="flex justify-center py-16">
                  <LoadingSpinner />
                </div>
              ) : filteredHosts.length ? (
                filteredHosts.map((host) => (
                  <HostCard
                    key={host.hostname}
                    host={host}
                    onSelect={setSelectedHost}
                    selected={selectedHost === host.hostname}
                  />
                ))
              ) : (
                <p className="text-dark-400">No hosts match the filter or no agents have reported yet.</p>
              )}
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">AI Insights</h3>
            {insights ? (
              <div className="space-y-3">
                <div className="rounded-xl bg-dark-700/30 p-4">
                  <p className="text-dark-400 text-sm mb-2">Summary</p>
                  <p className="text-white text-sm">{insights.health_summary}</p>
                </div>
                <div className="rounded-xl bg-dark-700/30 p-4">
                  <p className="text-dark-400 text-sm mb-2">Recommendations</p>
                  <ul className="list-disc list-inside text-sm text-white space-y-2">
                    {insights.recommendations.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div className="rounded-xl bg-dark-700/30 p-4">
                  <p className="text-dark-400 text-sm mb-2">Alerts</p>
                  {insights.alerts.length ? (
                    <ul className="list-disc list-inside text-sm text-white space-y-2">
                      {insights.alerts.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-white text-sm">No alerts detected.</p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-dark-400">Loading insights...</p>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <MetricsCard
              title="CPU"
              value={selectedMetrics.cpu_usage ?? '--'}
              unit="%"
              icon={Activity}
              change={{ value: selectedMetrics.cpu_usage ?? 0, unit: '%', label: 'current' }}
            />
            <MetricsCard
              title="Memory"
              value={selectedMetrics.memory_usage ?? '--'}
              unit="%"
              icon={Database}
              change={{ value: selectedMetrics.memory_usage ?? 0, unit: '%', label: 'current' }}
            />
            <MetricsCard
              title="Disk"
              value={selectedMetrics.disk_usage ?? '--'}
              unit="%"
              icon={Server}
              change={{ value: selectedMetrics.disk_usage ?? 0, unit: '%', label: 'current' }}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <ChartCard title="CPU History" loading={loading}>
              <CPUChart data={cpuHistory} />
            </ChartCard>
            <ChartCard title="Memory History" loading={loading}>
              <MemoryChart data={memoryHistory} />
            </ChartCard>
            <ChartCard title="Disk History" loading={loading}>
              <DiskChart data={diskHistory} />
            </ChartCard>
          </div>

          <Card className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Selected Host Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="rounded-xl bg-dark-700/30 p-4">
                <p className="text-dark-400 text-sm">Hostname</p>
                <p className="text-white mt-2">{selectedMetrics.hostname || 'N/A'}</p>
              </div>
              <div className="rounded-xl bg-dark-700/30 p-4">
                <p className="text-dark-400 text-sm">OS</p>
                <p className="text-white mt-2">{selectedMetrics.operating_system || 'N/A'}</p>
              </div>
              <div className="rounded-xl bg-dark-700/30 p-4">
                <p className="text-dark-400 text-sm">Last Seen</p>
                <p className="text-white mt-2">{selectedMetrics.last_seen_seconds_ago != null ? `${Math.floor(selectedMetrics.last_seen_seconds_ago / 60)}m ${selectedMetrics.last_seen_seconds_ago % 60}s ago` : 'Unknown'}</p>
              </div>
              <div className="rounded-xl bg-dark-700/30 p-4">
                <p className="text-dark-400 text-sm">Health</p>
                <p className={`mt-2 font-semibold ${hostHealthColor(selectedMetrics.cpu_usage || 0)}`}>{selectedMetrics.cpu_usage != null ? (selectedMetrics.cpu_usage >= 90 ? 'Critical' : selectedMetrics.cpu_usage >= 70 ? 'Warning' : 'Healthy') : 'Unknown'}</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
