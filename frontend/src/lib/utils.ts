import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import type { TaskUrgency } from "@/types/task";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Debounce function to delay function execution
// [Task]: T016
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/* --- Date & Utility Functions for UX Improvements --- */

// Format relative date string (e.g., "Today", "Yesterday", "In 3 days", "2 weeks ago")
// [Task]: T016
export function formatRelativeDate(dateString: string | null): string {
  if (!dateString) return '';

  const date = new Date(dateString);
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  // Reset to midnight for accurate day comparison
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const taskDate = new Date(date);
  taskDate.setHours(0, 0, 0, 0);
  const dayDiff = Math.floor((taskDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

  if (dayDiff === 0) return 'Today';
  if (dayDiff === 1) return 'Tomorrow';
  if (dayDiff === -1) return 'Yesterday';
  if (dayDiff < -1 && dayDiff >= -7) return `${Math.abs(dayDiff)} days ago`;
  if (dayDiff > 1 && dayDiff <= 7) return `In ${dayDiff} days`;
  if (dayDiff < -7 && dayDiff >= -30) return `${Math.floor(Math.abs(dayDiff) / 7)} weeks ago`;
  if (dayDiff > 7 && dayDiff <= 30) return `In ${Math.floor(dayDiff / 7)} weeks`;

  // Return formatted date for longer gaps
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// Calculate task urgency based on due date
// [Task]: T017
export function getTaskUrgency(dueDate: string | null): TaskUrgency {
  if (!dueDate) return 'none';

  const now = new Date();
  const due = new Date(dueDate);

  // Reset to midnight for accurate comparison
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const taskDueDate = new Date(due);
  taskDueDate.setHours(0, 0, 0, 0);

  const dayDiff = Math.floor((taskDueDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

  if (dayDiff < 0) return 'overdue';     // Past due
  if (dayDiff === 0) return 'due-today'; // Due today
  if (dayDiff <= 2) return 'due-soon';   // Due within 2 days
  return 'due-later';                     // Due later
}
