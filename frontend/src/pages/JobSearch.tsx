import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { useSearchParams } from 'react-router-dom';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowPathIcon,
  MapPinIcon,
  BriefcaseIcon,
  CalendarIcon,
  AdjustmentsHorizontalIcon,
} from '@heroicons/react/24/outline';

import { apiService } from '../services/api';
import JobCard from '../components/Jobs/JobCard';
import JobFilters from '../components/Jobs/JobFilters';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import Pagination from '../components/UI/Pagination';
import SearchBar from '../components/Search/SearchBar';
import SortDropdown from '../components/UI/SortDropdown';
import ViewToggle from '../components/UI/ViewToggle';

interface SearchFilters {
  hashtags: string[];
  sources: string[];
  timeFilter: string;
  location: string;
  jobType: string;
  experienceLevel: string;
  salaryMin: number | null;
  salaryMax: number | null;
  skills: string[];
  hasContacts: boolean;
  remoteOnly: boolean;
}

const JobSearch: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
  const [sortBy, setSortBy] = useState('relevance');
  const [currentPage, setCurrentPage] = useState(1);
  const [isSearching, setIsSearching] = useState(false);

  const [filters, setFilters] = useState<SearchFilters>({
    hashtags: searchParams.get('hashtags')?.split(',') || [],
    sources: ['linkedin', 'naukri', 'indeed', 'twitter'],
    timeFilter: searchParams.get('timeFilter') || '24h',
    location: searchParams.get('location') || '',
    jobType: searchParams.get('jobType') || '',
    experienceLevel: searchParams.get('experienceLevel') || '',
    salaryMin: null,
    salaryMax: null,
    skills: [],
    hasContacts: false,
    remoteOnly: false,
  });

  // Search jobs query
  const {
    data: searchResults,
    isLoading,
    refetch,
    isFetching,
  } = useQuery(
    ['searchJobs', filters, sortBy, currentPage],
    () => apiService.searchJobs({ ...filters, sortBy, page: currentPage, limit: 20 }),
    {
      enabled: false, // Don't auto-fetch, wait for user action
      keepPreviousData: true,
    }
  );

  // Update URL params when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    
    if (filters.hashtags.length > 0) {
      params.set('hashtags', filters.hashtags.join(','));
    }
    if (filters.timeFilter !== '24h') {
      params.set('timeFilter', filters.timeFilter);
    }
    if (filters.location) {
      params.set('location', filters.location);
    }
    if (filters.jobType) {
      params.set('jobType', filters.jobType);
    }
    if (filters.experienceLevel) {
      params.set('experienceLevel', filters.experienceLevel);
    }

    setSearchParams(params);
  }, [filters, setSearchParams]);

  const handleSearch = async (searchQuery?: string) => {
    if (searchQuery) {
      // Parse hashtags from search query
      const hashtags = searchQuery.match(/#\w+/g) || [];
      const cleanedHashtags = hashtags.map(tag => tag.replace('#', ''));
      
      setFilters(prev => ({ ...prev, hashtags: cleanedHashtags }));
    }

    setIsSearching(true);
    setCurrentPage(1);
    
    try {
      await refetch();
    } finally {
      setIsSearching(false);
    }
  };

  const handleFilterChange = (newFilters: Partial<SearchFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setCurrentPage(1);
  };

  const handleStartScraping = async () => {
    try {
      setIsSearching(true);
      await apiService.startScraping({
        hashtags: filters.hashtags,
        sources: filters.sources,
        timeFilter: filters.timeFilter,
      });
      
      // Refetch results after a delay to get new data
      setTimeout(() => {
        refetch();
      }, 2000);
    } catch (error) {
      console.error('Failed to start scraping:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const sortOptions = [
    { value: 'relevance', label: 'Most Relevant' },
    { value: 'date_desc', label: 'Newest First' },
    { value: 'date_asc', label: 'Oldest First' },
    { value: 'quality_desc', label: 'Highest Quality' },
    { value: 'salary_desc', label: 'Highest Salary' },
  ];

  const jobs = searchResults?.jobs || [];
  const totalPages = Math.ceil((searchResults?.total || 0) / 20);
  const hasResults = jobs.length > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
            Job Search
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Discover job opportunities using AI-powered hashtag search
          </p>
        </div>
      </div>

      {/* Search section */}
      <div className="card">
        <div className="card-body">
          <div className="space-y-4">
            {/* Search bar */}
            <div className="flex space-x-4">
              <div className="flex-1">
                <SearchBar
                  placeholder="Enter hashtags like #bca #fresher #javascript..."
                  onSearch={handleSearch}
                  showSuggestions
                />
              </div>
              <button
                onClick={handleStartScraping}
                disabled={isSearching || filters.hashtags.length === 0}
                className="btn btn-primary flex items-center space-x-2"
              >
                {isSearching ? (
                  <ArrowPathIcon className="h-5 w-5 animate-spin" />
                ) : (
                  <MagnifyingGlassIcon className="h-5 w-5" />
                )}
                <span>{isSearching ? 'Searching...' : 'Start Search'}</span>
              </button>
            </div>

            {/* Active filters */}
            {filters.hashtags.length > 0 && (
              <div className="flex flex-wrap items-center space-x-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Searching for:
                </span>
                {filters.hashtags.map((hashtag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200"
                  >
                    #{hashtag}
                    <button
                      type="button"
                      className="ml-1 text-primary-600 hover:text-primary-500"
                      onClick={() => {
                        const newHashtags = filters.hashtags.filter((_, i) => i !== index);
                        handleFilterChange({ hashtags: newHashtags });
                      }}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Filters and controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn btn-outline flex items-center space-x-2"
          >
            <FunnelIcon className="h-5 w-5" />
            <span>Filters</span>
            {showFilters && (
              <span className="ml-1 text-xs bg-primary-500 text-white rounded-full px-1.5 py-0.5">
                {Object.values(filters).filter(v => v && (Array.isArray(v) ? v.length > 0 : true)).length}
              </span>
            )}
          </button>

          {hasResults && (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {searchResults?.total.toLocaleString()} jobs found
            </div>
          )}
        </div>

        {hasResults && (
          <div className="flex items-center space-x-4">
            <SortDropdown
              options={sortOptions}
              value={sortBy}
              onChange={setSortBy}
            />
            <ViewToggle mode={viewMode} onChange={setViewMode} />
          </div>
        )}
      </div>

      {/* Filters panel */}
      {showFilters && (
        <div className="card">
          <div className="card-body">
            <JobFilters
              filters={filters}
              onChange={handleFilterChange}
            />
          </div>
        </div>
      )}

      {/* Results */}
      <div className="space-y-6">
        {(isLoading || isFetching) && (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
            <span className="ml-3 text-gray-600 dark:text-gray-400">
              {isSearching ? 'Discovering new jobs...' : 'Loading results...'}
            </span>
          </div>
        )}

        {!isLoading && !isFetching && !hasResults && filters.hashtags.length > 0 && (
          <div className="text-center py-12">
            <BriefcaseIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              No jobs found
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Try adjusting your search terms or filters to find more opportunities.
            </p>
            <div className="mt-6">
              <button
                onClick={handleStartScraping}
                disabled={isSearching}
                className="btn btn-primary"
              >
                Search Again
              </button>
            </div>
          </div>
        )}

        {!isLoading && !isFetching && filters.hashtags.length === 0 && (
          <div className="text-center py-12">
            <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              Start your job search
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Enter hashtags related to your desired job or skills to begin discovering opportunities.
            </p>
            <div className="mt-6">
              <div className="max-w-md mx-auto">
                <SearchBar
                  placeholder="#react #developer #mumbai"
                  onSearch={handleSearch}
                />
              </div>
            </div>
          </div>
        )}

        {hasResults && (
          <>
            {/* Job listings */}
            <div className={`
              ${viewMode === 'grid' 
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
                : 'space-y-4'
              }
            `}>
              {jobs.map((job: any) => (
                <JobCard
                  key={job.id}
                  job={job}
                  compact={viewMode === 'grid'}
                />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center">
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={setCurrentPage}
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default JobSearch;
