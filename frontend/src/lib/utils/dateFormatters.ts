/* Date formatting utilities for task due dates.

[Task]: T021-T023
[From]: specs/008-advanced-features/tasks.md (Phase 2)

Provides formatted date strings for display, relative time calculations,
and overdue detection with timezone handling.
*/

import { format, formatDistanceToNow, differenceInHours, differenceInDays, isPast, isToday as isTodayDateFns } from 'date-fns';
import type { Task } from '@/types/task';

/**
 * Format relative time string (e.g., "Due in 2 days", "Overdue by 3 days").
 *
 * [Task]: T022
 *
 * @param date - Date to format
 * @returns Formatted relative time string
 */
export function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) {
    return 'just now';
  } else if (diffMins < 60) {
    return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  } else if (diffDays < 7) {
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  } else {
    return format(date, 'PPPP'); // "January 4, 2026"
  }
}

/**
 * Format due date for display with overdue check.
 *
 * [Task]: T023
 *
 * @param task - Task with due_date
 * @returns Formatted due date string
 */
export function formatDueDate(task: Task): string {
  if (!task.due_date) {
    return 'No due date';
  }

  const dueDate = new Date(task.due_date);
  const now = new Date();

  if (isOverdue(task)) {
    const distance = formatDistanceToNow(dueDate, { addSuffix: false });
    return `Overdue ${distance} ago`;
  }

  if (isToday(dueDate)) {
    return `Due today at ${format(dueDate, 'h:mm a')}`;
  }

  const daysUntil = differenceInDays(dueDate, now);
  if (daysUntil === 0) {
    return 'Due today';
  } else if (daysUntil === 1) {
    return 'Due tomorrow';
  } else if (daysUntil < 7) {
    return `Due in ${daysUntil} days`;
  } else {
    return format(dueDate, 'PPPP'); // "January 4, 2026"
  }
}

/**
 * Check if a task is overdue.
 *
 * [Task]: T040 (also defined here as utility)
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
 * Check if a date is today.
 *
 * @param date - Date to check
 * @returns True if date is today
 */
export function isToday(date: Date): boolean {
  return isTodayDateFns(date);
}

/**
 * Format date and time for input fields.
 *
 * @param date - Date to format
 * @returns ISO 8601 string for input value
 */
export function formatDateTimeLocal(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

/**
 * Parse date from input value.
 *
 * @param value - ISO 8601 string
 * @returns Date object
 */
export function parseDateTimeLocal(value: string): Date {
  return new Date(value);
}

/**
 * Format date for API submission (UTC).
 *
 * @param date - Date to format
 * @returns ISO 8601 UTC string
 */
export function formatUTC(date: Date): string {
  return date.toISOString();
}

/**
 * Format date for display (local timezone).
 *
 * @param dateString - ISO 8601 string
 * @returns Formatted date string
 */
export function formatDisplayDate(dateString: string): string {
  const date = new Date(dateString);
  return format(date, 'PPp'); // "Jan 4, 2026 at 11:30 AM"
}

/**
 * Format short date for list items.
 *
 * @param dateString - ISO 8601 string
 * @returns Formatted date string
 */
export function formatShortDate(dateString: string): string {
  const date = new Date(dateString);
  return format(date, 'MMM d'); // "Jan 4"
}

/**
 * Get color class for due date urgency.
 *
 * @param dateString - ISO 8601 date string or null
 * @returns Tailwind color class name
 */
export function getDueDateColor(dateString: string | null): string {
  if (!dateString) {
    return 'text-gray-400';
  }

  const date = new Date(dateString);
  const now = new Date();
  const daysUntil = differenceInDays(date, now);

  if (isPast(date)) {
    return 'text-red-500'; // Overdue
  } else if (daysUntil === 0) {
    return 'text-orange-500'; // Due today
  } else if (daysUntil <= 2) {
    return 'text-yellow-500'; // Due soon
  } else {
    return 'text-gray-400'; // Due later
  }
}
