import React from 'react';

const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
        Settings
      </h1>
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <p className="text-gray-600 dark:text-gray-400">
          Settings page coming soon!
        </p>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          This page will allow you to configure search preferences, API keys, and notification settings.
        </p>
      </div>
    </div>
  );
};

export default Settings;
