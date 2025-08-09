import React, { useState } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  showSuggestions?: boolean;
  className?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = "Search jobs...",
  onSearch,
  showSuggestions = false,
  className = ""
}) => {
  const [query, setQuery] = useState('');
  const [showSuggestionsList, setShowSuggestionsList] = useState(false);

  const suggestions = [
    '#python #developer',
    '#react #frontend',
    '#node #backend',
    '#fullstack #javascript',
    '#data #science',
    '#machine #learning',
    '#bca #fresher',
    '#mca #experienced'
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch && query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestionsList(false);
    if (onSearch) {
      onSearch(suggestion);
    }
  };

  return (
    <div className={`relative ${className}`}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => showSuggestions && setShowSuggestionsList(true)}
            onBlur={() => setTimeout(() => setShowSuggestionsList(false), 200)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white dark:bg-gray-800 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 text-sm"
            placeholder={placeholder}
          />
        </div>
      </form>

      {/* Suggestions dropdown */}
      {showSuggestions && showSuggestionsList && query.length === 0 && (
        <div className="absolute z-10 mt-1 w-full bg-white dark:bg-gray-800 shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
          <div className="px-3 py-2 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
            Popular searches
          </div>
          {suggestions.map((suggestion, index) => (
            <div
              key={index}
              className="cursor-pointer select-none relative py-2 pl-3 pr-9 text-gray-900 dark:text-gray-100 hover:bg-primary-50 dark:hover:bg-gray-700"
              onClick={() => handleSuggestionClick(suggestion)}
            >
              <span className="block truncate">{suggestion}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
