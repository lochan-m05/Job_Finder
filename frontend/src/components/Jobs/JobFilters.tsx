import React from 'react';

interface JobFiltersProps {
  filters: any;
  onChange: (filters: any) => void;
}

const JobFilters: React.FC<JobFiltersProps> = ({ filters, onChange }) => {
  const timeFilterOptions = [
    { value: '1h', label: 'Last Hour' },
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
  ];

  const jobTypeOptions = [
    { value: '', label: 'All Types' },
    { value: 'full_time', label: 'Full Time' },
    { value: 'part_time', label: 'Part Time' },
    { value: 'contract', label: 'Contract' },
    { value: 'internship', label: 'Internship' },
  ];

  const experienceLevelOptions = [
    { value: '', label: 'All Levels' },
    { value: 'fresher', label: 'Fresher' },
    { value: 'entry_level', label: 'Entry Level' },
    { value: 'mid_level', label: 'Mid Level' },
    { value: 'senior_level', label: 'Senior Level' },
  ];

  const sourceOptions = [
    { value: 'linkedin', label: 'LinkedIn' },
    { value: 'naukri', label: 'Naukri' },
    { value: 'indeed', label: 'Indeed' },
    { value: 'twitter', label: 'Twitter' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Time Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Posted
        </label>
        <select
          value={filters.timeFilter}
          onChange={(e) => onChange({ ...filters, timeFilter: e.target.value })}
          className="form-select w-full"
        >
          {timeFilterOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Job Type */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Job Type
        </label>
        <select
          value={filters.jobType}
          onChange={(e) => onChange({ ...filters, jobType: e.target.value })}
          className="form-select w-full"
        >
          {jobTypeOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Experience Level */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Experience
        </label>
        <select
          value={filters.experienceLevel}
          onChange={(e) => onChange({ ...filters, experienceLevel: e.target.value })}
          className="form-select w-full"
        >
          {experienceLevelOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Location */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Location
        </label>
        <input
          type="text"
          value={filters.location}
          onChange={(e) => onChange({ ...filters, location: e.target.value })}
          placeholder="e.g., Mumbai, Bangalore"
          className="form-input w-full"
        />
      </div>

      {/* Sources */}
      <div className="md:col-span-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Sources
        </label>
        <div className="flex flex-wrap gap-2">
          {sourceOptions.map((source) => (
            <label key={source.value} className="inline-flex items-center">
              <input
                type="checkbox"
                checked={filters.sources.includes(source.value)}
                onChange={(e) => {
                  const newSources = e.target.checked
                    ? [...filters.sources, source.value]
                    : filters.sources.filter((s: string) => s !== source.value);
                  onChange({ ...filters, sources: newSources });
                }}
                className="form-checkbox h-4 w-4 text-primary-600"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                {source.label}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Additional filters */}
      <div className="md:col-span-2">
        <div className="flex items-center space-x-4">
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              checked={filters.hasContacts}
              onChange={(e) => onChange({ ...filters, hasContacts: e.target.checked })}
              className="form-checkbox h-4 w-4 text-primary-600"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Has Contact Info
            </span>
          </label>
          
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              checked={filters.remoteOnly}
              onChange={(e) => onChange({ ...filters, remoteOnly: e.target.checked })}
              className="form-checkbox h-4 w-4 text-primary-600"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Remote Only
            </span>
          </label>
        </div>
      </div>
    </div>
  );
};

export default JobFilters;
