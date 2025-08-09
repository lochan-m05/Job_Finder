import React from 'react';

const Contacts: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
        Contacts
      </h1>
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <p className="text-gray-600 dark:text-gray-400">
          Contact management system coming soon!
        </p>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          This page will show extracted recruiter contacts, verification status, and communication tools.
        </p>
      </div>
    </div>
  );
};

export default Contacts;
