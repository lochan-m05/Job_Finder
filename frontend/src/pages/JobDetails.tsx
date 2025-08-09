import React from 'react';
import { useParams } from 'react-router-dom';

const JobDetails: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
        Job Details
      </h1>
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <p className="text-gray-600 dark:text-gray-400">
          Job details for ID: {jobId}
        </p>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          This page will show detailed job information, contact details, and application options.
        </p>
      </div>
    </div>
  );
};

export default JobDetails;
