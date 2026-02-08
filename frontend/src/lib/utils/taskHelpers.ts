/* Task helper utilities.

[Task]: T040 (isOverdue function)
[From]: specs/008-advanced-features/tasks.md (Phase 3)

Provides utility functions for task operations including
overdue detection, urgency calculation, and task status helpers.
*/
import { isPast } from 'date-fns';
import type { Task, TaskUrgency } from '@/types/task';

/**
 * Check if a task is overdue.
 *
 * [Task]: T040
 *
 * A task is overdue if:
 * - It has a due_date set
 * - The due_date is in the past
 * - The task is not completed
 *
 * @param task - Task to check
 * @returns True if task is overdue, False otherwise
 */
export function isOverdue(task: Task): boolean {
  if (!task.due_date || task.completed) {
    return false;
  }
  return isPast(new Date(task.due_date));
}

/**
 * Calculate task urgency based on due date.
 *
 * @param task - Task to check
 * @returns Task urgency level
 */
export function getTaskUrgency(task: Task): TaskUrgency {
  if (!task.due_date) {
    return 'none';
  }

  const dueDate = new Date(task.due_date);
  const now = new Date();

  if (task.completed) {
    return 'none';
  }

  if (isPast(dueDate)) {
    return 'overdue';
  }

  const diffMs = dueDate.getTime() - now.getTime();
  const diffHours = diffMs / (1000 * 60 * 60);
  const diffDays = diffMs / (1000 * 60 * 60 * 24);

  if (diffHours <= 24) {
    return 'due-today';
  } else if (diffDays <= 7) {
    return 'due-soon';
  } else {
    return 'due-later';
  }
}

/**
 * Sort tasks by due date (putting nulls last).
 *
 * @param tasks - Tasks to sort
 * @returns Sorted tasks
 */
export function sortByDueDate(tasks: Task[]): Task[] {
  return [...tasks].sort((a, b) => {
    // Both null - maintain order
    if (!a.due_date && !b.due_date) {
      return 0;
    }
    // a is null - put last
    if (!a.due_date) {
      return 1;
    }
    // b is null - put first
    if (!b.due_date) {
      return -1;
    }
    // Both have dates - sort ascending
    return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
  });
}

/**
 * Group tasks by urgency.
 *
 * @param tasks - Tasks to group
 * @returns Tasks grouped by urgency
 */
export function groupByUrgency(tasks: Task[]): Record<TaskUrgency, Task[]> {
  const grouped: Record<TaskUrgency, Task[]> = {
    overdue: [],
    'due-today': [],
    'due-soon': [],
    'due-later': [],
    none: [],
  };

  for (const task of tasks) {
    const urgency = getTaskUrgency(task);
    grouped[urgency].push(task);
  }

  return grouped;
}
