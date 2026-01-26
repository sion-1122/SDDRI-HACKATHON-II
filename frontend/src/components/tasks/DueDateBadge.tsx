/* DueDateBadge component - displays task due date with urgency color coding.

[Task]: T027
[From]: specs/005-ux-improvement/tasks.md

This component:
- Displays due date with relative time (Today, Tomorrow, In 3 days, etc.)
- Color-coded by urgency (overdue=red, today=yellow, soon=green, later=gray)
- Uses Notion-inspired color palette from CSS variables
- Handles tasks without due dates gracefully (no "missing" indicators)
*/
import type { TaskUrgency } from '@/types/task';
import { formatRelativeDate } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface DueDateBadgeProps {
  dueDate: string | null;
  urgency?: TaskUrgency;
  className?: string;
}

const urgencyConfig = {
  overdue: {
    className: 'bg-urgency-overdue/10 text-urgency-overdue border-urgency-overdue/20',
    dotColor: 'bg-urgency-overdue',
  },
  'due-today': {
    className: 'bg-urgency-due-today/10 text-urgency-due-today border-urgency-due-today/20',
    dotColor: 'bg-urgency-due-today',
  },
  'due-soon': {
    className: 'bg-urgency-due-soon/10 text-urgency-due-soon border-urgency-due-soon/20',
    dotColor: 'bg-urgency-due-soon',
  },
  'due-later': {
    className: 'bg-urgency-due-later/10 text-urgency-due-later border-urgency-due-later/20',
    dotColor: 'bg-urgency-due-later',
  },
  none: {
    className: 'bg-muted/10 text-muted-foreground border-border',
    dotColor: 'bg-muted-foreground',
  },
};

export function DueDateBadge({ dueDate, urgency = 'none', className }: DueDateBadgeProps) {
  // Handle tasks without due dates gracefully - don't show anything
  if (!dueDate) {
    return null;
  }

  const config = urgencyConfig[urgency];
  const relativeDate = formatRelativeDate(dueDate);

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium border',
        config.className,
        className
      )}
    >
      <span className={cn('h-1.5 w-1.5 rounded-full', config.dotColor)} />
      <span>{relativeDate}</span>
    </div>
  );
}
