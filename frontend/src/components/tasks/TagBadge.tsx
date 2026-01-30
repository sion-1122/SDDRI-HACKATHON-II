/* TagBadge component - displays task tags with consistent colors.

[Task]: T030
[From]: specs/007-intermediate-todo-features/tasks.md (User Story 2)

This component:
- Displays tag name with deterministically assigned color
- Uses getTagColor utility for consistent colors across renders
- Supports click handlers for filtering by tag
- Notion-inspired minimalistic design
*/
import { getTagBadgeStyles } from '@/lib/tagColors';
import type { TaskTagName } from '@/types/task';
import { cn } from '@/lib/utils';

interface TagBadgeProps {
  name: TaskTagName;
  onClick?: (name: TaskTagName) => void;
  className?: string;
}

export function TagBadge({ name, onClick, className }: TagBadgeProps) {
  const { style: dynamicStyle } = getTagBadgeStyles(name);

  return (
    <span
      onClick={() => onClick?.(name)}
      className={cn(
        'inline-flex items-center gap-1 text-xs font-medium rounded-md px-2 py-0.5',
        'hover:opacity-80 transition-opacity',
        'cursor-pointer',
        className
      )}
      style={dynamicStyle}
    >
      #{name}
    </span>
  );
}

// Display multiple tags as a group
interface TagBadgeGroupProps {
  tags: TaskTagName[];
  onTagClick?: (name: TaskTagName) => void;
  className?: string;
  maxDisplay?: number;
}

export function TagBadgeGroup({ tags, onTagClick, className, maxDisplay = 5 }: TagBadgeGroupProps) {
  if (!tags || tags.length === 0) {
    return null;
  }

  const displayTags = maxDisplay ? tags.slice(0, maxDisplay) : tags;
  const hasMore = maxDisplay && tags.length > maxDisplay;

  return (
    <div className={cn('flex flex-wrap gap-1.5', className)}>
      {displayTags.map((tag) => (
        <TagBadge key={tag} name={tag} onClick={onTagClick} />
      ))}
      {hasMore && (
        <span className="text-xs text-muted-foreground">
          +{tags.length - maxDisplay} more
        </span>
      )}
    </div>
  );
}
