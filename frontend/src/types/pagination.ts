/* Pagination state type definitions.

[Task]: T013
[From]: specs/003-frontend-task-manager/data-model.md
*/

export interface PaginationState {
  offset: number;          // Current offset (0-based)
  limit: number;           // Items per page (default: 50)
  total: number;           // Total number of tasks
}

export interface PaginationActions {
  nextPage: () => void;
  prevPage: () => void;
  goToPage: (page: number) => void;
}

export interface PaginationComputed {
  currentPage: number;     // Current page (1-based)
  totalPages: number;      // Total pages
  hasNextPage: boolean;    // Has next page?
  hasPrevPage: boolean;    // Has previous page?
}

// URL Representation:
// Page number: ?page=2 (1-based)
// Converted to offset: offset = (page - 1) * limit
