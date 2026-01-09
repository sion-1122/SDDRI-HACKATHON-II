/* FilterBar component - filter and search controls.

[Task]: T046, T047, T049, T050
[From]: specs/003-frontend-task-manager/plan.md

This client component:
- Dropdown for status filter: all/active/completed
- Search input field
- Debounced search (300ms)
- Clear filters button
- URL param synchronization (?status=active&search=query)
*/
'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { debounce } from '@/lib/utils';
import type { TaskFilter } from '@/types/filters';

export function FilterBar() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
  const [statusFilter, setStatusFilter] = useState<TaskFilter>(
    (searchParams.get('status') as TaskFilter) || 'all'
  );

  // Update URL params when filters change (T047)
  useEffect(() => {
    const params = new URLSearchParams();

    if (statusFilter !== 'all') {
      params.set('status', statusFilter);
    }
    if (searchQuery) {
      params.set('search', searchQuery);
    }

    const queryString = params.toString();
    router.push(`${queryString ? `?${queryString}` : ''}`);
  }, [statusFilter, searchQuery, router]);

  // Debounced search (T049)
  const debouncedSearch = debounce((value: string) => {
    setSearchQuery(value);
  }, 300);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    debouncedSearch(value);
  };

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(e.target.value as TaskFilter);
  };

  // Clear filters button (T050)
  const handleClearFilters = () => {
    setSearchQuery('');
    setStatusFilter('all');
    router.push('');
  };

  const hasActiveFilters = statusFilter !== 'all' || searchQuery;

  return (
    <div className="bg-white shadow rounded-lg p-4 mb-6">
      <div className="flex flex-col md:flex-row gap-4 items-center">
        {/* Status filter */}
        <div className="flex-1">
          <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
            Filter by Status
          </label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={handleStatusChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Tasks</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        {/* Search input */}
        <div className="flex-1">
          <label htmlFor="search-input" className="block text-sm font-medium text-gray-700 mb-1">
            Search Tasks
          </label>
          <input
            id="search-input"
            type="text"
            placeholder="Search by title or description..."
            defaultValue={searchQuery}
            onChange={handleSearchChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Clear filters button */}
        {hasActiveFilters && (
          <div className="flex items-end">
            <button
              onClick={handleClearFilters}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm font-medium"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
