import React from 'react';
import { Squares2X2Icon, ListBulletIcon } from '@heroicons/react/24/outline';

interface ViewToggleProps {
  mode: 'grid' | 'list';
  onChange: (mode: 'grid' | 'list') => void;
}

const ViewToggle: React.FC<ViewToggleProps> = ({ mode, onChange }) => {
  return (
    <div className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
      <button
        onClick={() => onChange('list')}
        className={`p-2 rounded-md transition-colors ${
          mode === 'list'
            ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
            : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
        }`}
        title="List view"
      >
        <ListBulletIcon className="h-4 w-4" />
      </button>
      <button
        onClick={() => onChange('grid')}
        className={`p-2 rounded-md transition-colors ${
          mode === 'grid'
            ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
            : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
        }`}
        title="Grid view"
      >
        <Squares2X2Icon className="h-4 w-4" />
      </button>
    </div>
  );
};

export default ViewToggle;
