/* RecurrenceBadge component - displays recurring task indicator.

[Task]: T073
[From]: specs/008-advanced-features/tasks.md (User Story 3)

This component:
- Displays a visual indicator for recurring tasks
- Shows the recurrence pattern (daily, weekly, monthly)
- Uses Notion-inspired styling
*/
import { Repeat } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { RecurrenceRule } from '@/types/recurrence';

interface RecurrenceBadgeProps {
  recurrence: RecurrenceRule | null;
  className?: string;
}

const frequencyLabels: Record<string, string> = {
  daily: 'Daily',
  weekly: 'Weekly',
  monthly: 'Monthly',
};

export function RecurrenceBadge({ recurrence, className }: RecurrenceBadgeProps) {
  if (!recurrence) {
    return null;
  }

  const frequency = recurrence.frequency;
  const interval = recurrence.interval || 1;
  const label = frequencyLabels[frequency] || frequency;

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium border',
        'bg-primary/10 text-primary border-primary/20',
        className
      )}
      title={`Repeats ${interval > 1 ? `every ${interval} ${label.toLowerCase()}(s)` : label.toLowerCase()}`}
    >
      <Repeat className="h-3 w-3" />
      <span>
        {interval > 1 ? `Every ${interval} ` : ''}{label}
      </span>
    </div>
  );
}
