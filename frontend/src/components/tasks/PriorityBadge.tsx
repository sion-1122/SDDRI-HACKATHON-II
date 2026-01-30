/* PriorityBadge component - displays task priority with Notion-inspired colors.

[Task]: T026
[From]: specs/005-ux-improvement/tasks.md

This component:
- Displays priority level (low, medium, high) with color-coded badge
- Uses Notion-inspired color palette from CSS variables
- Supports light and dark mode
*/
import type { TaskPriority } from '@/types/task';
import { cn } from '@/lib/utils';

interface PriorityBadgeProps {
  priority: TaskPriority;
  className?: string;
}

const priorityConfig = {
  low: {
    label: 'Low',
    className: 'bg-priority-low/10 text-priority-low border-priority-low/20',
  },
  medium: {
    label: 'Medium',
    className: 'bg-priority-medium/10 text-priority-medium border-priority-medium/20',
  },
  high: {
    label: 'High',
    className: 'bg-priority-high/10 text-priority-high border-priority-high/20',
  },
};

export function PriorityBadge({ priority, className }: PriorityBadgeProps) {
  const config = priorityConfig[priority] || {
    label: priority || 'Unknown',
    className: 'bg-gray-100 text-gray-600 border-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border',
        config.className,
        className
      )}
    >
      {config.label}
    </span>
  );
}
