import React from 'react';
import { 
  MapPinIcon, 
  ClockIcon, 
  CurrencyRupeeIcon,
  BuildingOfficeIcon 
} from '@heroicons/react/24/outline';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  skills: string[];
  posted_at?: string;
  source: string;
  salary?: {
    min?: number;
    max?: number;
    currency?: string;
  };
}

interface JobCardProps {
  job: Job;
  compact?: boolean;
  onClick?: () => void;
}

const JobCard: React.FC<JobCardProps> = ({ job, compact = false, onClick }) => {
  const formatSalary = (salary: any) => {
    if (!salary || (!salary.min && !salary.max)) return null;
    
    const formatAmount = (amount: number) => {
      if (amount >= 100000) {
        return `${(amount / 100000).toFixed(1)}L`;
      }
      return `${(amount / 1000).toFixed(0)}K`;
    };

    if (salary.min && salary.max) {
      return `₹${formatAmount(salary.min)} - ${formatAmount(salary.max)}`;
    }
    return `₹${formatAmount(salary.min || salary.max)}`;
  };

  const formatTimeAgo = (dateString: string) => {
    if (!dateString) return 'Recently';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return date.toLocaleDateString();
  };

  return (
    <div 
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow duration-200 ${
        onClick ? 'cursor-pointer' : ''
      } ${compact ? 'p-4' : 'p-6'}`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          {/* Job Title */}
          <h3 className={`font-semibold text-gray-900 dark:text-white ${
            compact ? 'text-sm' : 'text-lg'
          } truncate`}>
            {job.title}
          </h3>
          
          {/* Company */}
          <div className="flex items-center mt-1 text-gray-600 dark:text-gray-400">
            <BuildingOfficeIcon className="h-4 w-4 mr-1" />
            <span className={compact ? 'text-xs' : 'text-sm'}>{job.company}</span>
          </div>
          
          {/* Location */}
          <div className="flex items-center mt-1 text-gray-500 dark:text-gray-400">
            <MapPinIcon className="h-4 w-4 mr-1" />
            <span className={compact ? 'text-xs' : 'text-sm'}>{job.location}</span>
          </div>
        </div>
        
        {/* Source badge */}
        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
          job.source === 'linkedin' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
          job.source === 'naukri' ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' :
          job.source === 'indeed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
          'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
        }`}>
          {job.source}
        </span>
      </div>
      
      {/* Description */}
      {!compact && job.description && (
        <p className="mt-3 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
          {job.description}
        </p>
      )}
      
      {/* Skills */}
      {job.skills && job.skills.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {job.skills.slice(0, compact ? 3 : 5).map((skill, index) => (
            <span
              key={index}
              className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200"
            >
              {skill}
            </span>
          ))}
          {job.skills.length > (compact ? 3 : 5) && (
            <span className="text-xs text-gray-500 dark:text-gray-400">
              +{job.skills.length - (compact ? 3 : 5)} more
            </span>
          )}
        </div>
      )}
      
      {/* Footer */}
      <div className="mt-4 flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
        <div className="flex items-center space-x-4">
          {/* Salary */}
          {job.salary && (
            <div className="flex items-center">
              <CurrencyRupeeIcon className="h-4 w-4 mr-1" />
              <span>{formatSalary(job.salary)}</span>
            </div>
          )}
          
          {/* Posted time */}
          <div className="flex items-center">
            <ClockIcon className="h-4 w-4 mr-1" />
            <span>{formatTimeAgo(job.posted_at || '')}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobCard;
