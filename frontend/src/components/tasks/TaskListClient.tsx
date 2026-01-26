/* TaskListClient - client wrapper for task list with interactions.

[Task]: T022, T037-T039
[From]: specs/005-ux-improvement/tasks.md

This component:
- Wraps TaskList with client-side features (filters, search, pagination)
- Receives initial tasks from Server Component (fast first paint)
- Handles user interactions and refetches data as needed
- Uses nuqs for type-safe URL query state management
*/
'use client';

import { useEffect, useState, useRef } from 'react';
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

        // Add search query if present
        if (filters.searchQuery) {
          params.search = filters.searchQuery;
        }

        // Note: priority and dueDate filters will be implemented on backend later
        // For now, we'll do client-side filtering for those

        const response = await taskApi.listTasks(params);
        let filteredTasks = response.tasks;

        // Apply priority filter (client-side for now)
        if (filters.priority) {
          filteredTasks = filteredTasks.filter(t => t.priority === filters.priority);
        }

        // Apply due date filter (client-side for now)
        if (filters.dueDate) {
          const today = new Date();
          today.setHours(0, 0, 0, 0);

          filteredTasks = filteredTasks.filter(t => {
            if (!t.due_date) return false;
            const dueDate = new Date(t.due_date);
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

        setTasks(filteredTasks);
        setTotal(filteredTasks.length);
      } catch (err: any) {
        setError(err.message || 'Failed to load tasks');
      } finally {
        setLoading(false);
      }
    };

    loadTasks();
  }, [filters.status, filters.searchQuery, filters.priority, filters.dueDate, filters.page]);

  return (
    <>
      <FilterBar />

      {loading ? (
        <TaskSkeleton />
      ) : error ? (
        <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg">
          {error}
        </div>
      ) : (
        <>
          <TaskList tasks={tasks} />
          <Pagination
            total={total}
            limit={ITEMS_PER_PAGE}
            currentPage={filters.page}
          />
        </>
      )}
    </>
  );
}
