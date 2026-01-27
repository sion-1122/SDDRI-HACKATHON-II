/* FilterBar component - filter and search controls with Notion-inspired design.

[Task]: T034-T039, T074
[From]: specs/005-ux-improvement/tasks.md

This client component:
- Status filter: all/active/completed
- Priority filter: low/medium/high
- Due date filter: all/overdue/today/week/month
- Search input with debouncing
- Clear filters button
- URL param synchronization using nuqs for type-safe state
- Notion-inspired minimalistic styling
*/
'use client';

import { useQueryStates } from 'nuqs';
import { Search, X } from 'lucide-react';
import { debounce } from '@/lib/utils';
import { cn } from '@/lib/utils';

// nuqs parsers for type-safe URL state
import { filterParsers } from '@/types/filters';

export function FilterBar() {
  const [filters, setFilters] = useQueryStates(filterParsers);

  // Update search with debouncing
  const debouncedSetSearch = debounce((value: string) => {
    setFilters({ searchQuery: value });
  }, 300);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Immediate UI update
    setFilters({ searchQuery: value });
    // Debounced API call
    debouncedSetSearch(value);
  };

  const handleStatusChange = (value: 'all' | 'active' | 'completed') => {
    setFilters({ status: value });
  };

  const handlePriorityChange = (value: 'all' | 'low' | 'medium' | 'high') => {
    setFilters({ priority: value === 'all' ? null : value });
  };

  const handleDueDateChange = (value: 'all' | 'overdue' | 'today' | 'week' | 'month') => {
    setFilters({ dueDate: value === 'all' ? null : value });
  };

  // Clear all filters
  const handleClearFilters = () => {
    setFilters({
      status: 'all',
      searchQuery: '',
      priority: null,
      dueDate: null,
    });
  };

  const hasActiveFilters =
    filters.status !== 'all' ||
    filters.searchQuery !== '' ||
    filters.priority !== null ||
    filters.dueDate !== null;

  return (
    <div className="mb-6">
      {/* Notion-inspired filter bar - clean and minimalistic */}
      <div className="flex flex-col lg:flex-row gap-3 items-stretch lg:items-center">
        {/* Search input - prominent position */}
        <div className="flex-1 lg:flex-[2]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
            <input
              id="search-input"
              type="text"
              placeholder="Search tasks..."
              value={filters.searchQuery}
              onChange={handleSearchChange}
              className={cn(
                "w-full pl-10 pr-10 py-2.5",
                "bg-background border border-input rounded-lg",
                "text-sm text-foreground placeholder:text-muted-foreground",
                "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
                "transition-shadow",
                "focus:shadow-sm"
              )}
            />
            {filters.searchQuery && (
              <button
                onClick={() => setFilters({ searchQuery: '' })}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 rounded-md hover:bg-muted transition-colors"
                aria-label="Clear search"
              >
                <X className="w-3.5 h-3.5 text-muted-foreground" />
              </button>
            )}
          </div>
        </div>

        {/* Filter dropdowns - styled as pill buttons */}
        <div className="flex flex-wrap gap-2">
          {/* Status filter */}
          <select
            id="status-filter"
            value={filters.status}
            onChange={(e) => handleStatusChange(e.target.value as 'all' | 'active' | 'completed')}
            className={cn(
              "px-4 py-2.5 text-sm bg-background border border-input rounded-lg",
              "text-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
              "cursor-pointer hover:bg-muted/50 transition-colors appearance-none",
              "pr-8" // space for dropdown arrow
            )}
          >
            <option value="all">All Tasks</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>

          {/* Priority filter */}
          <select
            id="priority-filter"
            value={filters.priority || 'all'}
            onChange={(e) => handlePriorityChange(e.target.value as 'all' | 'low' | 'medium' | 'high')}
            className={cn(
              "px-4 py-2.5 text-sm bg-background border border-input rounded-lg",
              "text-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
              "cursor-pointer hover:bg-muted/50 transition-colors appearance-none",
              "pr-8"
            )}
          >
            <option value="all">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          {/* Due date filter */}
          <select
            id="duedate-filter"
            value={filters.dueDate || 'all'}
            onChange={(e) => handleDueDateChange(e.target.value as 'all' | 'overdue' | 'today' | 'week' | 'month')}
            className={cn(
              "px-4 py-2.5 text-sm bg-background border border-input rounded-lg",
              "text-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
              "cursor-pointer hover:bg-muted/50 transition-colors appearance-none",
              "pr-8"
            )}
          >
            <option value="all">All Dates</option>
            <option value="overdue">Overdue</option>
            <option value="today">Due Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
        </div>

        {/* Clear filters button - only show when filters are active */}
        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            className="px-4 py-2.5 text-sm bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors whitespace-nowrap"
          >
            Clear
          </button>
        )}
      </div>

      {/* Active filter summary - subtle display */}
      {hasActiveFilters && (
        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
          {filters.status !== 'all' && (
            <span className="flex items-center gap-1">
              Status: <strong className="text-foreground capitalize">{filters.status}</strong>
            </span>
          )}
          {filters.priority && (
            <span className="flex items-center gap-1">
              Priority: <strong className="text-foreground capitalize">{filters.priority}</strong>
            </span>
          )}
          {filters.dueDate && (
            <span className="flex items-center gap-1">
              Due: <strong className="text-foreground capitalize">{filters.dueDate}</strong>
            </span>
          )}
          {filters.searchQuery && (
            <span className="flex items-center gap-1">
              Search: <strong className="text-foreground">&quot;{filters.searchQuery}&quot;</strong>
            </span>
          )}
        </div>
      )}
    </div>
  );
}
