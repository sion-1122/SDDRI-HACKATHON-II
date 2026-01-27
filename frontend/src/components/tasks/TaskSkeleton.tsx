/* TaskSkeleton component - loading placeholder for task cards.

[Task]: T019
[From]: specs/005-ux-improvement/tasks.md

This component:
- Displays skeleton placeholders while tasks load
- Matches the grid layout of TaskList (3 columns on large screens)
- Provides visual feedback during server-side data fetching
*/
import { Skeleton } from '@/components/ui/skeleton';

export function TaskSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="bg-card border border-border rounded-lg p-4 space-y-3">
          {/* Title skeleton */}
          <Skeleton className="h-5 w-3/4" />
          {/* Description skeleton lines */}
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
          {/* Meta info skeleton */}
          <div className="flex justify-between items-center pt-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-6 w-16 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  );
}
