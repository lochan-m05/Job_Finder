import React from 'react';
import { useQuery } from 'react-query';
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, BarChart, Bar } from 'recharts';
import { apiService } from '../services/api';

const Analytics: React.FC = () => {
  const { data, isLoading, error } = useQuery(['analytics', 'dashboard'], () => apiService.getDashboardData('30d'));

  if (isLoading) {
    return <div className="p-6">Loading analytics...</div>;
  }
  if (error) {
    return <div className="p-6 text-red-600">Failed to load analytics.</div>;
  }

  const jobTrends = data?.jobTrends ?? [];
  const skillTrends = data?.skillTrends ?? [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Jobs over time (30d)</h3>
          </div>
          <div className="card-body h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={jobTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="jobs" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Top skills</h3>
          </div>
          <div className="card-body h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={skillTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="skill" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
