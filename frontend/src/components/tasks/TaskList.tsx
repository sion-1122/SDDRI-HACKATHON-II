/* TaskList component - displays list of tasks.

[Task]: T036, T051
[From]: specs/003-frontend-task-manager/plan.md

This server component:
- Receives tasks as prop
- Renders list of TaskItem components
- Displays empty state when no tasks
- Shows different message for filtered results vs no tasks at all
*/
'use client';

import { useSearchParams } from 'next/navigation';
import type { Task } from '@/types/task';
import { TaskItem } from './TaskItem';

interface TaskListProps {
  tasks: Task[];
}

export function TaskList({ tasks }: TaskListProps) {
  const searchParams = useSearchParams();
  const hasActiveFilters = searchParams.has('status') || searchParams.has('search');

  // Handle undefined or null tasks
  if (!tasks || tasks.length === 0) {
    if (hasActiveFilters) {
      // Empty state for filtered results (T051)
      return (
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
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No tasks match your filters</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your filters or search query
          </p>
        </div>
      );
    }

    // Empty state for no tasks at all
    return (
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
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
          />
        </svg>
        <h3 className="mt-2 text-sm font-semibold text-gray-900">No tasks</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by creating a new task.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {tasks.map((task) => (
        <TaskItem key={task.id} task={task} />
      ))}
    </div>
  );
}
