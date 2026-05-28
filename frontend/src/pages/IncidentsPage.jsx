import React, { useState, useEffect } from 'react';
import { AlertCircle, Filter } from 'lucide-react';
import { IncidentCard, Card, Button, Badge } from '../components';
import { incidentService } from '../services/api';

export const IncidentsPage = () => {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchIncidents = async () => {
    try {
      const response = await incidentService.getIncidents();
      setIncidents(response.data);
    } catch (error) {
      console.error('Error fetching incidents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleIncidentAction = async (incidentId, action) => {
    try {
      if (action === 'resolve') {
        await incidentService.resolveIncident(incidentId);
        fetchIncidents();
      }
    } catch (error) {
      console.error(`Error ${action}:`, error);
    }
  };

  const criticalCount = incidents.filter((i) => i.priority === 'critical').length;
  const resolvedCount = incidents.filter((i) => i.status === 'resolved').length;
  const activeCount = incidents.filter((i) => i.status !== 'resolved').length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Incidents</h1>
        <p className="text-dark-400 mt-1">Monitor system alerts and issues</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <p className="stat-label">Total Incidents</p>
          <p className="stat-value mt-2">{incidents.length}</p>
        </Card>
        <Card className="p-4">
          <p className="stat-label">Active</p>
          <p className="stat-value text-red-400 mt-2">{activeCount}</p>
        </Card>
        <Card className="p-4">
          <p className="stat-label">Critical</p>
          <p className="stat-value text-orange-400 mt-2">{criticalCount}</p>
        </Card>
        <Card className="p-4">
          <p className="stat-label">Resolved</p>
          <p className="stat-value text-green-400 mt-2">{resolvedCount}</p>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {['all', 'active', 'resolved', 'critical'].map((f) => (
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

      {/* Incidents List */}
      <div className="space-y-4">
        {incidents.length === 0 ? (
          <Card className="p-8 text-center">
            <AlertCircle className="w-12 h-12 text-dark-600 mx-auto mb-4" />
            <p className="text-dark-400">No incidents found</p>
          </Card>
        ) : (
          incidents.map((incident) => (
            <IncidentCard
              key={incident.id}
              incident={incident}
              onAction={(action) => handleIncidentAction(incident.id, action)}
            />
          ))
        )}
      </div>

      {/* Legend */}
      <Card className="p-4 mt-6">
        <h3 className="font-semibold text-white mb-3">Priority Levels</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { level: 'critical', color: 'text-red-400' },
            { level: 'high', color: 'text-orange-400' },
            { level: 'medium', color: 'text-yellow-400' },
            { level: 'low', color: 'text-blue-400' },
          ].map((item) => (
            <div key={item.level} className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${item.color}`} />
              <span className="text-sm text-dark-400 capitalize">{item.level}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
