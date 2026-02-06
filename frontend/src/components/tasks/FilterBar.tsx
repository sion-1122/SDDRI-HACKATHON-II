/* FilterBar component - filter and search controls with Notion-inspired design.

[Task]: T034-T039, T074, T036
[From]: specs/005-ux-improvement/tasks.md, specs/007-intermediate-todo-features/tasks.md

This client component:
- Status filter: all/active/completed
- Priority filter: low/medium/high
- Due date filter: all/overdue/today/week/month
- Tags filter: multi-select dropdown
- Search input with debouncing
- Clear filters button
- URL param synchronization using nuqs for type-safe state
- Notion-inspired minimalistic styling
- Refactored to use shadcn UI components for consistent styling
*/
'use client';

import { useState, useEffect } from 'react';
import { useQueryStates } from 'nuqs';
import { Search, X, ChevronDown, Check, ArrowUpDown } from 'lucide-react';
import { debounce } from '@/lib/utils';
import { cn } from '@/lib/utils';
import { taskApi } from '@/lib/task-api';
import type { TagInfo } from '@/lib/task-api';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { DateRangeFilter } from '@/components/tasks/DateRangeFilter';

// nuqs parsers for type-safe URL state
import { filterParsers } from '@/types/filters';

export function FilterBar() {
  const [filters, setFilters] = useQueryStates(filterParsers);
  const [availableTags, setAvailableTags] = useState<TagInfo[]>([]);
  const [showTagsDropdown, setShowTagsDropdown] = useState(false);

  // Fetch all tags on mount [T038]
  useEffect(() => {
    taskApi.getAllTags().then(data => {
      setAvailableTags(data.tags);
    }).catch(() => {
      // Silently fail - tags will just be empty
    });
  }, []);

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

  const handlePriorityChange = (value: 'all' | 'LOW' | 'MEDIUM' | 'HIGH') => {
    setFilters({ priority: value === 'all' ? null : value });
  };

  const handleDueDateChange = (value: 'all' | 'overdue' | 'today' | 'week' | 'month') => {
    setFilters({ dueDate: value === 'all' ? null : value });
  };

  // Toggle tag filter [T036]
  const handleTagToggle = (tagName: string) => {
    const currentTags = filters.tags || [];
    const newTags = currentTags.includes(tagName)
      ? currentTags.filter((t: string) => t !== tagName)
      : [...currentTags, tagName];
    setFilters({ tags: newTags.length > 0 ? newTags : null });
  };

  // Handle sort by change [T053]
  const handleSortByChange = (value: 'created_at' | 'due_date' | 'priority' | 'title' | '') => {
    setFilters({ sortBy: value || null });
  };

  // Handle sort order toggle [T054]
  const handleSortOrderToggle = () => {
    setFilters({ sortOrder: filters.sortOrder === 'asc' ? 'desc' : 'asc' });
  };

  // Clear all filters
  const handleClearFilters = () => {
    setFilters({
      status: 'all',
      searchQuery: '',
      priority: null,
      dueDate: null,
      due_before: null,
      due_after: null,
      tags: null,
      sortBy: null,
      sortOrder: 'asc',
    });
  };

  const hasActiveFilters =
    filters.status !== 'all' ||
    filters.searchQuery !== '' ||
    filters.priority !== null ||
    filters.dueDate !== null ||
    filters.due_before !== null ||
    filters.due_after !== null ||
    (filters.tags !== null && filters.tags.length > 0) ||
    filters.sortBy !== null;

  return (
    <div className="mb-6">
      {/* Notion-inspired filter bar - clean and minimalistic */}
      <div className="flex flex-col lg:flex-row gap-3 items-stretch lg:items-center">
        {/* Search input - prominent position */}
        <div className="flex-1 lg:flex-[2]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
            <Input
              id="search-input"
              type="text"
              placeholder="Search tasks..."
              value={filters.searchQuery}
              onChange={handleSearchChange}
              className="pl-10 pr-10"
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
          <Select
            value={filters.status}
            onValueChange={(value) => handleStatusChange(value as 'all' | 'active' | 'completed')}
          >
            <SelectTrigger id="status-filter" className="w-fit min-w-[140px]">
              <SelectValue placeholder="All Tasks" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Tasks</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
            </SelectContent>
          </Select>

          {/* Priority filter */}
          <Select
            value={filters.priority || 'all'}
            onValueChange={(value) => handlePriorityChange(value as 'all' | 'LOW' | 'MEDIUM' | 'HIGH')}
          >
            <SelectTrigger id="priority-filter" className="w-fit min-w-[140px]">
              <SelectValue placeholder="All Priorities" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priorities</SelectItem>
              <SelectItem value="HIGH">High</SelectItem>
              <SelectItem value="MEDIUM">Medium</SelectItem>
              <SelectItem value="LOW">Low</SelectItem>
            </SelectContent>
          </Select>

          {/* Due date filter */}
          <Select
            value={filters.dueDate || 'all'}
            onValueChange={(value) => handleDueDateChange(value as 'all' | 'overdue' | 'today' | 'week' | 'month')}
          >
            <SelectTrigger id="duedate-filter" className="w-fit min-w-[140px]">
              <SelectValue placeholder="All Dates" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Dates</SelectItem>
              <SelectItem value="overdue">Overdue</SelectItem>
              <SelectItem value="today">Due Today</SelectItem>
              <SelectItem value="week">This Week</SelectItem>
              <SelectItem value="month">This Month</SelectItem>
            </SelectContent>
          </Select>

          {/* Tags filter [T036] - multi-select dropdown */}
          {availableTags.length > 0 && (
            <div className="relative">
              <Button
                type="button"
                variant={filters.tags && filters.tags.length > 0 ? "default" : "secondary"}
                onClick={() => setShowTagsDropdown(!showTagsDropdown)}
                className="flex items-center gap-2"
              >
                <span>Tags</span>
                {filters.tags && filters.tags.length > 0 && (
                  <span className="text-muted-foreground">({filters.tags.length})</span>
                )}
                <ChevronDown className={cn(
                  "w-4 h-4 transition-transform",
                  showTagsDropdown && "rotate-180"
                )} />
              </Button>

              {/* Tags dropdown */}
              {showTagsDropdown && (
                <div className="absolute top-full mt-1 right-0 z-50 min-w-[200px] bg-background border border-input rounded-lg shadow-lg p-2">
                  <div className="max-h-64 overflow-y-auto">
                    {availableTags.map((tagInfo) => {
                      const isSelected = filters.tags?.includes(tagInfo.tag);
                      return (
                        <button
                          key={tagInfo.tag}
                          type="button"
                          onClick={() => handleTagToggle(tagInfo.tag)}
                          className={cn(
                            "w-full px-3 py-2 text-sm rounded-md flex items-center justify-between gap-2",
                            "hover:bg-muted/50 transition-colors",
                            isSelected && "bg-muted"
                          )}
                        >
                          <span>#{tagInfo.tag}</span>
                          <span className="text-muted-foreground text-xs">{tagInfo.count}</span>
                          {isSelected && <Check className="w-4 h-4 text-primary" />}
                        </button>
                      );
                    })}
                    {availableTags.length === 0 && (
                      <div className="px-3 py-2 text-sm text-muted-foreground">
                        No tags available
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Date range filter [T036] - custom date range */}
          <DateRangeFilter
            dueBefore={filters.due_before}
            dueAfter={filters.due_after}
            onChange={(dueBefore, dueAfter) =>
              setFilters({ due_before: dueBefore, due_after: dueAfter })
            }
          />
        </div>

        {/* Sort controls [T053, T054] */}
        <div className="flex gap-2">
          {/* Sort by dropdown */}
          <Select
            value={filters.sortBy || 'default'}
            onValueChange={(value) => handleSortByChange(value === 'default' ? '' : value as 'created_at' | 'due_date' | 'priority' | 'title')}
          >
            <SelectTrigger id="sort-by" className="w-fit min-w-[160px]">
              <SelectValue placeholder="Sort: Default" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="default">Sort: Default</SelectItem>
              <SelectItem value="created_at">Date Created</SelectItem>
              <SelectItem value="due_date">Due Date</SelectItem>
              <SelectItem value="priority">Priority</SelectItem>
              <SelectItem value="title">Title (A-Z)</SelectItem>
            </SelectContent>
          </Select>

          {/* Sort order toggle button */}
          <Button
            type="button"
            variant={filters.sortBy ? "default" : "secondary"}
            onClick={handleSortOrderToggle}
            disabled={!filters.sortBy}
            title={`Sort order: ${filters.sortOrder === 'asc' ? 'Ascending' : 'Descending'}`}
            className="flex items-center gap-2"
          >
            <ArrowUpDown className={cn(
              "w-4 h-4",
              filters.sortOrder === 'asc' ? "rotate-0" : "rotate-180"
            )} />
            <span className="hidden sm:inline">{filters.sortOrder === 'asc' ? 'Asc' : 'Desc'}</span>
          </Button>
        </div>

        {/* Clear filters button - only show when filters are active */}
        {hasActiveFilters && (
          <Button
            variant="secondary"
            onClick={handleClearFilters}
            className="whitespace-nowrap"
          >
            Clear
          </Button>
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
          {filters.due_before && (
            <span className="flex items-center gap-1">
              Before: <strong className="text-foreground">{new Date(filters.due_before).toLocaleDateString()}</strong>
            </span>
          )}
          {filters.due_after && (
            <span className="flex items-center gap-1">
              After: <strong className="text-foreground">{new Date(filters.due_after).toLocaleDateString()}</strong>
            </span>
          )}
          {filters.tags && filters.tags.length > 0 && (
            <span className="flex items-center gap-1">
              Tags: <strong className="text-foreground">{filters.tags.map((t: string) => `#${t}`).join(', ')}</strong>
            </span>
          )}
          {filters.searchQuery && (
            <span className="flex items-center gap-1">
              Search: <strong className="text-foreground">&quot;{filters.searchQuery}&quot;</strong>
            </span>
          )}
          {filters.sortBy && (
            <span className="flex items-center gap-1">
              Sort: <strong className="text-foreground capitalize">{filters.sortBy.replace('_', ' ')}</strong>
              <strong className="text-foreground">({filters.sortOrder})</strong>
            </span>
          )}
        </div>
      )}
    </div>
  );
}
