import React, { useState } from 'react';
import { useQuery } from 'react-query';
import {
  BriefcaseIcon,
  UsersIcon,
  ChartBarIcon,
  ClockIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  EyeIcon,
  BookmarkIcon,
} from '@heroicons/react/24/outline';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';

import { apiService } from '../services/api';
import JobCard from '../components/Jobs/JobCard';
import StatCard from '../components/Dashboard/StatCard';
import RecentActivity from '../components/Dashboard/RecentActivity';
import QuickActions from '../components/Dashboard/QuickActions';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Dashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');

  // Fetch dashboard data
  const { data: dashboardData, isLoading } = useQuery(
    ['dashboard', timeRange],
    () => apiService.getDashboardData(timeRange),
    {
      refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    }
  );

  const { data: recentJobs } = useQuery(
    'recentJobs',
    () => apiService.getRecentJobs(5),
    {
      refetchInterval: 2 * 60 * 1000, // Refetch every 2 minutes
    }
  );

  const { data: savedJobs } = useQuery(
    'savedJobs',
    () => apiService.getSavedJobs(),
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const stats = dashboardData?.stats || {
    totalJobs: 0,
    newJobs: 0,
    totalContacts: 0,
    savedJobs: 0,
    jobTrends: [],
    skillTrends: [],
    locationTrends: []
  };

  const jobTrendData = stats.jobTrends || [];
  const skillData = stats.skillTrends?.slice(0, 10) || [];
  const locationData = stats.locationTrends?.slice(0, 5) || [];

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
            Dashboard
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Welcome back! Here's what's happening with your job search.
          </p>
        </div>
        <div className="mt-4 flex md:mt-0 md:ml-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="form-select"
          >
            <option value="1d">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Jobs Found"
          value={stats.totalJobs.toLocaleString()}
          change={stats.jobsChange}
          changeType={stats.jobsChange >= 0 ? 'increase' : 'decrease'}
          icon={BriefcaseIcon}
          color="blue"
        />
        <StatCard
          title="New Jobs Today"
          value={stats.newJobs.toLocaleString()}
          change={stats.newJobsChange}
          changeType={stats.newJobsChange >= 0 ? 'increase' : 'decrease'}
          icon={ClockIcon}
          color="green"
        />
        <StatCard
          title="Contacts Found"
          value={stats.totalContacts.toLocaleString()}
          change={stats.contactsChange}
          changeType={stats.contactsChange >= 0 ? 'increase' : 'decrease'}
          icon={UsersIcon}
          color="purple"
        />
        <StatCard
          title="Saved Jobs"
          value={stats.savedJobs.toLocaleString()}
          change={stats.savedJobsChange}
          changeType={stats.savedJobsChange >= 0 ? 'increase' : 'decrease'}
          icon={BookmarkIcon}
          color="yellow"
        />
      </div>

      {/* Charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Job trends chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Job Discovery Trends
            </h3>
          </div>
          <div className="card-body">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={jobTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="jobs" 
                    stroke="#3B82F6" 
                    strokeWidth={2}
                    dot={{ fill: '#3B82F6' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Top skills chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Top Skills in Demand
            </h3>
          </div>
          <div className="card-body">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={skillData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="skill" type="category" width={80} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent jobs */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-header flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Recent Job Discoveries
              </h3>
              <button className="btn btn-sm btn-outline">
                View All
              </button>
            </div>
            <div className="card-body space-y-4">
              {recentJobs?.slice(0, 5).map((job: any) => (
                <JobCard key={job.id} job={job} compact />
              ))}
              {(!recentJobs || recentJobs.length === 0) && (
                <div className="text-center py-8">
                  <BriefcaseIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                    No jobs found yet
                  </h3>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Start a search to discover relevant job opportunities.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar content */}
        <div className="space-y-6">
          {/* Quick actions */}
          <QuickActions />

          {/* Location trends */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Top Locations
              </h3>
            </div>
            <div className="card-body">
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={locationData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {locationData.map((entry: { name: string; count: number }, index: number) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Recent activity */}
          <RecentActivity />
        </div>
      </div>

      {/* Saved jobs section */}
      {savedJobs && savedJobs.length > 0 && (
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Saved Jobs
            </h3>
            <span className="badge badge-primary">
              {savedJobs.length} saved
            </span>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {savedJobs.slice(0, 6).map((job: any) => (
                <JobCard key={job.id} job={job} compact />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
