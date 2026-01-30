/* TaskListClient - client wrapper for task list with interactions.

[Task]: T022, T037-T039, T021
[From]: specs/005-ux-improvement/tasks.md, specs/007-intermediate-todo-features/tasks.md (US3)

This component:
- Wraps TaskList with client-side features (filters, search, pagination)
- Receives initial tasks from Server Component (fast first paint)
- Handles user interactions and refetches data as needed
- Uses nuqs for type-safe URL query state management
- Uses useMemo for optimized client-side search [T021]
*/
'use client';

import { useEffect, useState, useRef, useMemo } from 'react';
import { useQueryStates } from 'nuqs';
import { TaskList } from './TaskList';
import { FilterBar } from './FilterBar';
import { Pagination } from './Pagination';
import { taskApi } from '@/lib/task-api';
import { filterParsers } from '@/types/filters';
import type { Task } from '@/types/task';
import { TaskSkeleton } from './TaskSkeleton';

const ITEMS_PER_PAGE = 50;

interface TaskListClientProps {
  initialTasks: Task[];
  initialTotal: number;
}

export function TaskListClient({ initialTasks, initialTotal }: TaskListClientProps) {
  const [filters] = useQueryStates(filterParsers);
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [total, setTotal] = useState(initialTotal);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Track if this is the first render
  const isFirstRender = useRef(true);

  // [T021] Optimized client-side search with useMemo
  // Only re-filter when tasks or search query changes
  const filteredTasks = useMemo(() => {
    let result = tasks;

    // Apply search query filter
    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase();
      result = result.filter(task => {
        const titleMatch = task.title.toLowerCase().includes(query);
        const descMatch = task.description?.toLowerCase().includes(query) || false;
        return titleMatch || descMatch;
      });
    }

    // Apply due date filter (client-side for now)
    if (filters.dueDate) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      result = result.filter(task => {
        if (!task.due_date) return false;
        const dueDate = new Date(task.due_date);
        dueDate.setHours(0, 0, 0, 0);
        const dayDiff = Math.floor((dueDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

        switch (filters.dueDate) {
          case 'overdue':
            return dayDiff < 0;
          case 'today':
            return dayDiff === 0;
          case 'week':
            return dayDiff >= 0 && dayDiff <= 7;
          case 'month':
            return dayDiff >= 0 && dayDiff <= 30;
          default:
            return true;
        }
      });
    }

    // Apply tags filter [T036] - client-side for now
    if (filters.tags && filters.tags.length > 0) {
      result = result.filter(task => {
        const taskTags = task.tags || [];
        // Return tasks that have ALL the selected tags (AND logic)
        return filters.tags!.every((tag: string) => taskTags.includes(tag));
      });
    }

    return result;
  }, [tasks, filters.searchQuery, filters.dueDate, filters.tags]);

  // Load tasks when URL params change
  useEffect(() => {
    // Skip on first render (we have initial data from server)
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    const loadTasks = async () => {
      setLoading(true);
      setError(null);

      try {
        const page = filters.page;
        const offset = (page - 1) * ITEMS_PER_PAGE;

        const params: {
          limit: number;
          offset: number;
          completed?: boolean;
          search?: string;
          priority?: 'LOW' | 'MEDIUM' | 'HIGH';
          tags?: string[];
          due_date?: 'overdue' | 'today' | 'week' | 'month';
          sort_by?: 'created_at' | 'due_date' | 'priority' | 'title';
          sort_order?: 'asc' | 'desc';
        } = {
          limit: ITEMS_PER_PAGE,
          offset,
        };

        // Convert status filter to completed boolean
        if (filters.status === 'active') {
          params.completed = false;
        } else if (filters.status === 'completed') {
          params.completed = true;
        }

        // Add priority filter if present [T018]
        if (filters.priority) {
          params.priority = filters.priority;
        }

        // Add tags filter if present [T037]
        if (filters.tags && filters.tags.length > 0) {
          params.tags = filters.tags;
        }

        // Add due_date filter if present [T047]
        if (filters.dueDate) {
          params.due_date = filters.dueDate;
        }

        // Add sort parameters if present [T056]
        if (filters.sortBy) {
          params.sort_by = filters.sortBy;
          params.sort_order = filters.sortOrder || 'asc';
        }

        const response = await taskApi.listTasks(params);
        setTasks(response.tasks);
        setTotal(response.total);
      } catch (err: any) {
        setError(err.message || 'Failed to load tasks');
      } finally {
        setLoading(false);
      }
    };

    loadTasks();
  }, [filters.status, filters.priority, filters.tags, filters.dueDate, filters.sortBy, filters.sortOrder, filters.page]);

  return (
    <>
      <FilterBar />

      {/* [T042] Filter count display */}
      {!loading && !error && (
        <div className="text-sm text-muted-foreground mb-4">
          Showing {filteredTasks.length} of {total} tasks
        </div>
      )}

      {loading ? (
        <TaskSkeleton />
      ) : error ? (
        <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg">
          {error}
        </div>
      ) : (
        <>
          {/* [T027] Empty search results handling */}
          {filteredTasks.length === 0 && (filters.searchQuery || filters.dueDate || (filters.tags && filters.tags.length > 0)) ? (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-semibold text-gray-900">No tasks match your search</h3>
              <p className="mt-1 text-sm text-gray-500">
                {filters.searchQuery && `No tasks found matching "${filters.searchQuery}"`}
                {!filters.searchQuery && filters.dueDate && `No tasks due ${filters.dueDate}`}
                {!filters.searchQuery && !filters.dueDate && filters.tags && filters.tags.length > 0 && `No tasks tagged with ${filters.tags.map((t: string) => `#${t}`).join(', ')}`}
              </p>
            </div>
          ) : (
            <>
              <TaskList tasks={filteredTasks} />
              <Pagination
                total={filteredTasks.length}
                limit={ITEMS_PER_PAGE}
                currentPage={filters.page}
              />
            </>
          )}
        </>
      )}
    </>
  );
}
