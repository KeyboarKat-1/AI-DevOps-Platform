import React, { useState, useEffect } from 'react';
import { Rocket, CheckCircle, AlertCircle } from 'lucide-react';
import { DeploymentCard, Card, Button, ChartCard } from '../components';
import { ComparisonChart } from '../components/charts';
import { deploymentService } from '../services/api';

export const DeploymentsPage = () => {
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchDeployments();
    const interval = setInterval(fetchDeployments, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDeployments = async () => {
    try {
      const response = await deploymentService.getDeployments();
      setDeployments(response.data);
    } catch (error) {
      console.error('Error fetching deployments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeploymentAction = async (deploymentId, action) => {
    try {
      if (action === 'rollback') {
        // Implement rollback
        fetchDeployments();
      } else if (action === 'retry') {
        // Implement retry
        fetchDeployments();
      }
    } catch (error) {
      console.error(`Error ${action}:`, error);
    }
  };

  const deploymentTimeline = [
    { name: 'v2.1.0', duration: 45 },
    { name: 'v2.0.5', duration: 38 },
    { name: 'v2.0.4', duration: 42 },
    { name: 'v2.0.3', duration: 41 },
  ];

  const stats = {
    total: deployments.length,
    completed: deployments.filter((d) => d.status === 'completed').length,
    failed: deployments.filter((d) => d.status === 'failed').length,
    inProgress: deployments.filter((d) => d.status === 'in_progress').length,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Deployments</h1>
        <p className="text-dark-400 mt-1">Track and manage application deployments</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <p className="stat-label">Total Deployments</p>
          <p className="stat-value mt-2">{stats.total}</p>
        </Card>
        <Card className="p-4">
          <p className="stat-label">Completed</p>
          <p className="stat-value text-green-400 mt-2">{stats.completed}</p>
        </Card>
        <Card className="p-4">
          <p className="stat-label">In Progress</p>
          <p className="stat-value text-blue-400 mt-2">{stats.inProgress}</p>
        </Card>
        <Card className="p-4">
          <p className="stat-label">Failed</p>
          <p className="stat-value text-red-400 mt-2">{stats.failed}</p>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {['all', 'completed', 'in_progress', 'failed'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg transition-all capitalize ${
              filter === f
                ? 'bg-primary-600 text-white'
                : 'bg-dark-700 text-dark-400 hover:text-white'
            }`}
          >
            {f === 'in_progress' ? 'In Progress' : f}
          </button>
        ))}
      </div>

      {/* Deployments List */}
      <div className="space-y-4">
        {deployments.length === 0 ? (
          <Card className="p-8 text-center">
            <Rocket className="w-12 h-12 text-dark-600 mx-auto mb-4" />
            <p className="text-dark-400">No deployments found</p>
          </Card>
        ) : (
          deployments.map((deployment) => (
            <DeploymentCard
              key={deployment.id}
              deployment={deployment}
              onAction={(action) => handleDeploymentAction(deployment.id, action)}
            />
          ))
        )}
      </div>

      {/* Deployment Timeline */}
      <ChartCard title="Recent Deployment Times">
        <div className="flex flex-col gap-3">
          {deploymentTimeline.map((item, idx) => (
            <div key={idx} className="flex items-center gap-4">
              <div className="w-16">
                <p className="text-sm font-mono text-primary-400">{item.name}</p>
              </div>
              <div className="flex-1 bg-dark-700 rounded-full h-2">
                <div
                  className="bg-primary-500 h-2 rounded-full"
                  style={{ width: `${(item.duration / 50) * 100}%` }}
                />
              </div>
              <p className="text-xs text-dark-400 w-8 text-right">{item.duration}s</p>
            </div>
          ))}
        </div>
      </ChartCard>
    </div>
  );
};
