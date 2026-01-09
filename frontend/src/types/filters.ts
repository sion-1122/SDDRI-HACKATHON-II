/* Filter state type definitions.

[Task]: T012
[From]: specs/003-frontend-task-manager/data-model.md
*/

export type TaskFilter = 'all' | 'active' | 'completed';

export interface FilterState {
  status: TaskFilter;
  searchQuery: string;
}

export interface FilterActions {
  setStatus: (status: TaskFilter) => void;
  setSearchQuery: (query: string) => void;
  clearFilters: () => void;
}

// URL Representation:
// status: ?status=active or ?status=completed (all = no param)
// searchQuery: ?search=query+string
// Both: ?status=active&search=query
