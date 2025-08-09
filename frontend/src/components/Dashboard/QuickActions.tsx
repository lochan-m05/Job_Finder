import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MagnifyingGlassIcon,
  PlusIcon,
  ChartBarIcon,
  BookmarkIcon,
} from '@heroicons/react/24/outline';

const QuickActions: React.FC = () => {
  const navigate = useNavigate();

  const actions = [
    {
      title: 'Start Job Search',
      description: 'Search for jobs using hashtags',
      icon: MagnifyingGlassIcon,
      color: 'bg-blue-500',
      action: () => navigate('/search'),
    },
    {
      title: 'View Analytics',
      description: 'See job market trends',
      icon: ChartBarIcon,
      color: 'bg-green-500',
      action: () => navigate('/analytics'),
    },
    {
      title: 'Saved Jobs',
      description: 'View your bookmarked jobs',
      icon: BookmarkIcon,
      color: 'bg-purple-500',
      action: () => navigate('/search?filter=saved'),
    },
    {
      title: 'Add Keywords',
      description: 'Set up job alerts',
      icon: PlusIcon,
      color: 'bg-yellow-500',
      action: () => navigate('/settings'),
    },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
      <div className="p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h3>
        <div className="space-y-3">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={action.action}
              className="w-full flex items-center p-3 text-left bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-150"
            >
              <div className={`flex-shrink-0 p-2 rounded-md ${action.color}`}>
                <action.icon className="h-5 w-5 text-white" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {action.title}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {action.description}
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default QuickActions;
