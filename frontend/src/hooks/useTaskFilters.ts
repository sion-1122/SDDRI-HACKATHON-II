/* useTaskFilters hook - manages task filter state with URL synchronization.

[Task]: T020
[From]: specs/007-intermediate-todo-features/tasks.md (User Story 3)

This hook:
- Manages filter state (status, priority, search query, due date)
- Synchronizes state with URL params using nuqs
- Provides memoized filter predicates
- Handles filter reset and persistence
*/
'use client';

import { useMemo } from 'react';
import { useQueryStates } from 'nuqs';
import { filterParsers, type FilterState } from '@/types/filters';

interface UseTaskFiltersReturn extends FilterState {
  setFilters: (updates: Partial<FilterState>) => void;
  clearFilters: () => void;
  hasActiveFilters: boolean;
  searchQuery: string;
}

export function useTaskFilters(): UseTaskFiltersReturn {
  const [filters, setFilters] = useQueryStates(filterParsers);

  // Memoize active filters check
  const hasActiveFilters = useMemo(
    () =>
      filters.status !== 'all' ||
      !!filters.searchQuery ||
      filters.priority !== null ||
      filters.dueDate !== null ||
      (filters.tags !== null && filters.tags.length > 0),
    [filters]
  );

  // Clear all filters to default state
  const clearFilters = () => {
    setFilters({
      status: 'all',
      searchQuery: '',
      priority: null,
      dueDate: null,
      tags: null,
      sortBy: null,
      sortOrder: 'asc',
      page: 1,
    });
  };

  return {
    ...filters,
    setFilters: (updates) => setFilters(updates as Partial<FilterState>),
    clearFilters,
    hasActiveFilters,
    searchQuery: filters.searchQuery,
  };
}

export default useTaskFilters;
