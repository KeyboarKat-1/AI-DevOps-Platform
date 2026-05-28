import React, { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import { ContainerCard, Card, Button, Modal } from '../components';
import { dockerService } from '../services/api';

export const DockerPage = () => {
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchContainers();
    const interval = setInterval(fetchContainers, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchContainers = async () => {
    try {
      const response = await dockerService.getContainers();
      setContainers(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Error fetching containers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContainerAction = async (containerId, action) => {
    try {
      if (action === 'start') {
        await dockerService.startContainer(containerId);
      } else if (action === 'stop') {
        await dockerService.stopContainer(containerId);
      }
      fetchContainers();
    } catch (error) {
      console.error(`Error performing ${action}:`, error);
    }
  };

  const filteredContainers = containers.filter((c) => {
    if (filter === 'running') return c.status === 'running';
    if (filter === 'stopped') return c.status === 'stopped';
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Docker Containers</h1>
          <p className="text-dark-400 mt-1">Monitor and manage your containers</p>
        </div>
        <Button variant="primary" onClick={fetchContainers} disabled={loading}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 text-center">
          <p className="stat-label">Total Containers</p>
          <p className="stat-value mt-2">{containers.length}</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="stat-label">Running</p>
          <p className="stat-value text-green-400 mt-2">
            {containers.filter((c) => c.status === 'running').length}
          </p>
        </Card>
        <Card className="p-4 text-center">
          <p className="stat-label">Stopped</p>
          <p className="stat-value text-red-400 mt-2">
            {containers.filter((c) => c.status === 'stopped').length}
          </p>
        </Card>
        <Card className="p-4 text-center">
          <p className="stat-label">Paused</p>
          <p className="stat-value text-yellow-400 mt-2">
            {containers.filter((c) => c.status === 'paused').length}
          </p>
        </Card>
      </div>

      <div className="flex gap-2">
        {['all', 'running', 'stopped'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg transition-all capitalize ${
              filter === f
                ? 'bg-primary-600 text-white'
                : 'bg-dark-700 text-dark-400 hover:text-white'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredContainers.map((container) => (
          <ContainerCard
            key={container.id}
            id={container.id}
            name={container.name}
            image={container.image}
            status={container.status}
            cpu={container.cpu_usage || 0}
            memory={container.memory_usage || 0}
            uptime={container.uptime || 'unknown'}
            onClick={() => setSelectedContainer(container)}
            onAction={(action) => handleContainerAction(container.id, action)}
          />
        ))}
      </div>

      {selectedContainer && (
        <Modal
          isOpen={!!selectedContainer}
          onClose={() => setSelectedContainer(null)}
          title={selectedContainer.name}
          actions={[
            { label: 'Close', variant: 'secondary', onClick: () => setSelectedContainer(null) },
          ]}
        >
          <div className="space-y-4">
            <div>
              <p className="text-sm text-dark-400">Image</p>
              <p className="text-white font-mono text-sm mt-1">{selectedContainer.image}</p>
            </div>
            <div>
              <p className="text-sm text-dark-400">Container ID</p>
              <p className="text-white font-mono text-sm mt-1">{selectedContainer.id?.substring(0, 12)}</p>
            </div>
            <div>
              <p className="text-sm text-dark-400">Status</p>
              <p className="text-white font-mono text-sm mt-1">{selectedContainer.status}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-dark-400">CPU</p>
                <p className="text-primary-400 font-semibold mt-1">
                  {(selectedContainer.cpu_usage || 0).toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-dark-400">Memory</p>
                <p className="text-cyan-400 font-semibold mt-1">
                  {((selectedContainer.memory_usage || 0) / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <div>
              <p className="text-sm text-dark-400">Uptime</p>
              <p className="text-white font-mono text-sm mt-1">{selectedContainer.uptime || 'unknown'}</p>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
