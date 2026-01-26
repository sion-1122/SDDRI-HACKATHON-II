/* Filter state type definitions.

[Task]: T012, T013, T014, T015
[From]: specs/003-frontend-task-manager/data-model.md, specs/005-ux-improvement/data-model.md
*/

export type TaskFilter = 'all' | 'active' | 'completed';

// Task priority filter type [T013]
export type TaskPriority = 'low' | 'medium' | 'high';

// Due date range filter type [T014]
export type DueDateFilter = 'overdue' | 'today' | 'week' | 'month';

export interface FilterState {
  status: TaskFilter;
  searchQuery: string;
  priority?: TaskPriority;      // [T012]
  dueDate?: DueDateFilter;       // [T012]
  page: number;                  // [T012]
}

export interface FilterActions {
  setStatus: (status: TaskFilter) => void;
  setSearchQuery: (query: string) => void;
  setPriority: (priority: TaskPriority) => void;
  setDueDate: (dueDate: DueDateFilter) => void;
  setPage: (page: number) => void;
  clearFilters: () => void;
}

// nuqs filter parsers for type-safe URL state [T015]
// These are used with useQueryStates hook from nuqs
export const filterParsers = {
  // Status parser: defaults to 'all' when not in URL
  status: {
    defaultValue: 'all' as TaskFilter,
    parse: (value: string | null): TaskFilter =>
      value === 'active' || value === 'completed' ? value : 'all',
    serialize: (value: TaskFilter): string | null =>
      value === 'all' ? null : value,
  },

  // Search query parser
  searchQuery: {
    defaultValue: '',
    parse: (value: string | null): string => value ?? '',
    serialize: (value: string): string | null =>
      value ? value : null,
  },

  // Priority parser: optional filter
  priority: {
    defaultValue: null as TaskPriority | null,
    parse: (value: string | null): TaskPriority | null =>
      value === 'low' || value === 'medium' || value === 'high' ? value : null,
    serialize: (value: TaskPriority | null): string | null => value,
  },

  // Due date parser: optional filter
  dueDate: {
    defaultValue: null as DueDateFilter | null,
    parse: (value: string | null): DueDateFilter | null => {
      if (value === 'overdue' || value === 'today' || value === 'week' || value === 'month') {
        return value;
      }
      return null;
    },
    serialize: (value: DueDateFilter | null): string | null => value,
  },

  // Page parser: defaults to 1
  page: {
    defaultValue: 1,
    parse: (value: string | null): number => {
      const parsed = value ? parseInt(value, 10) : 1;
      return isNaN(parsed) || parsed < 1 ? 1 : parsed;
    },
    serialize: (value: number): string | null =>
      value === 1 ? null : value.toString(),
  },
};

// URL Representation:
// status: ?status=active or ?status=completed (all = no param)
// searchQuery: ?search=query+string
// priority: ?priority=high|medium|low
// dueDate: ?dueDate=overdue|today|week|month
// page: ?page=2
// Combined: ?status=active&search=query&priority=high&page=1
