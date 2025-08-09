import React from 'react';
import {
  MagnifyingGlassIcon,
  BookmarkIcon,
  EyeIcon,
  UserIcon,
} from '@heroicons/react/24/outline';

interface Activity {
  id: string;
  type: 'search' | 'save' | 'view' | 'contact';
  description: string;
  timestamp: string;
  metadata?: any;
}

const RecentActivity: React.FC = () => {
  // Mock activity data
  const activities: Activity[] = [
    {
      id: '1',
      type: 'search',
      description: 'Searched for #python #developer jobs',
      timestamp: '2 hours ago',
    },
    {
      id: '2',
      type: 'save',
      description: 'Saved Python Developer at TechCorp',
      timestamp: '4 hours ago',
    },
    {
      id: '3',
      type: 'view',
      description: 'Viewed React Developer job details',
      timestamp: '6 hours ago',
    },
    {
      id: '4',
      type: 'contact',
      description: 'Extracted contact for HR Manager',
      timestamp: '1 day ago',
    },
    {
      id: '5',
      type: 'search',
      description: 'Searched for #react #frontend jobs',
      timestamp: '1 day ago',
    },
  ];

  const getIcon = (type: string) => {
    switch (type) {
      case 'search':
        return MagnifyingGlassIcon;
      case 'save':
        return BookmarkIcon;
      case 'view':
        return EyeIcon;
      case 'contact':
        return UserIcon;
      default:
        return MagnifyingGlassIcon;
    }
  };

  const getIconColor = (type: string) => {
    switch (type) {
      case 'search':
        return 'text-blue-500';
      case 'save':
        return 'text-green-500';
      case 'view':
        return 'text-purple-500';
      case 'contact':
        return 'text-yellow-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
      <div className="p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Recent Activity
        </h3>
        <div className="flow-root">
          <ul className="-mb-8">
            {activities.map((activity, index) => {
              const Icon = getIcon(activity.type);
              const isLast = index === activities.length - 1;
              
              return (
                <li key={activity.id}>
                  <div className="relative pb-8">
                    {!isLast && (
                      <span
                        className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-600"
                        aria-hidden="true"
                      />
                    )}
                    <div className="relative flex space-x-3">
                      <div>
                        <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white dark:ring-gray-800 bg-gray-100 dark:bg-gray-700`}>
                          <Icon className={`h-4 w-4 ${getIconColor(activity.type)}`} />
                        </span>
                      </div>
                      <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                        <div>
                          <p className="text-sm text-gray-900 dark:text-white">
                            {activity.description}
                          </p>
                        </div>
                        <div className="text-right text-sm whitespace-nowrap text-gray-500 dark:text-gray-400">
                          <time>{activity.timestamp}</time>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default RecentActivity;
