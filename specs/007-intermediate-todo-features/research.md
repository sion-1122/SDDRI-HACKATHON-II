# Research Report: Intermediate Todo Features

**Feature**: 007-intermediate-todo-features
**Date**: 2026-01-28
**Phase**: Phase 0 (Research)

## Overview

This document consolidates research findings for implementing intermediate todo features (priority management, tags, search, filtering, sorting, and UI fixes) in the existing FastAPI + Next.js application with Neon PostgreSQL and OpenAI Agents SDK.

---

## 1. Priority Extraction from Natural Language

### Decision
**Use OpenAI Agents SDK with Pydantic `output_type` for structured priority extraction**

### Rationale
The OpenAI Agents SDK provides native support for structured outputs through Pydantic models. This approach ensures:
- **Type Safety**: Pydantic models provide compile-time type checking and runtime validation
- **Explicit Schema**: Define exact priority levels (`high`, `medium`, `low`) as an enum
- **Built-in Validation**: Automatic validation against the schema
- **Pattern Matching**: The LLM extracts priority from natural language patterns

### Implementation Pattern

```python
from pydantic import BaseModel, Field
from agents import Agent
from enum import Enum

class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskCommand(BaseModel):
    """Structured output for task command extraction"""
    title: str
    description: str | None = None
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    due_date: str | None = None

# Create agent with structured output
priority_extractor = Agent(
    name="priority_extractor",
    instructions="""Extract task priority from natural language.

Priority guidelines:
- High: urgent, ASAP, today, critical, important, emergency
- Medium: normal tasks, default priority
- Low: whenever, optional, nice-to-have, later
    """,
    output_type=TaskCommand
)
```

### Alternatives Considered

| Approach | Pros | Cons | Rejection Reason |
|----------|------|------|------------------|
| Regex Pattern Matching | Fast, no API cost | Limited, misses context | Can't understand semantic meaning |
| Keyword-based Heuristics | Simple, predictable | Brittle, language-specific | Doesn't handle variations well |
| Fine-tuned Model | Optimized for domain | Expensive to train/maintain | Overkill for this use case |

### Integration Point
- File: `/backend/ai_agent/agent.py` (extends existing OpenAI Agents integration)
- MCP Tools: Add priority extraction before task creation

---

## 2. Client-Side Search Implementation

### Decision
**Use React's `useMemo` for filtering with URL state synchronization via `nuqs`**

### Rationale
For task lists under 100 items:
1. **Simple filtering is sufficient** - Array.filter() is fast for <100 items
2. **useMemo prevents recalculation** - Only re-filter when dependencies change
3. **URL state via nuqs** - Already installed and working in the codebase
4. **Instant feedback** - No network latency for client-side filtering

### Implementation Pattern

```typescript
import { useMemo } from 'react';
import { useQueryStates } from 'nuqs';

function TaskListClient({ tasks }: { tasks: Task[] }) {
  const [filters] = useQueryStates(filterParsers);

  // Memoized filtering - only re-runs when tasks or filters change
  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      // Search filter
      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase();
        const matchesTitle = task.title.toLowerCase().includes(query);
        const matchesDesc = task.description?.toLowerCase().includes(query);
        if (!matchesTitle && !matchesDesc) return false;
      }
      // Priority filter
      if (filters.priority && task.priority !== filters.priority) return false;
      // Status filter
      if (filters.status === 'active' && task.completed) return false;
      if (filters.status === 'completed' && !task.completed) return false;
      return true;
    });
  }, [tasks, filters]);

  return <TaskList tasks={filteredTasks} />;
}
```

### Performance Targets

| List Size | Filter Time | Approach |
|-----------|-------------|----------|
| < 100 items | < 5ms | Client-side with useMemo |
| ≥ 100 items | < 500ms | Server-side with debounce |

### Integration Point
- File: `/frontend/src/components/tasks/TaskListClient.tsx` (extends existing filtering logic)
- URL state: Uses existing `nuqs` integration from `FilterBar.tsx`

---

## 3. Tag Color Consistency

### Decision
**Use a deterministic hash function (stringHash) mapped to a curated HSL color palette**

### Rationale
1. **Consistency**: Same tag always gets same color across renders/sessions
2. **Visual Distinction**: Hash function distributes tags across color palette
3. **Readability**: Use HSL with fixed lightness/saturation for consistent contrast
4. **No server storage**: Colors derived deterministically from tag names

### Implementation Pattern

```typescript
// lib/tagColors.ts
const COLOR_PALETTE = [
  { h: 0, s: 70, l: 60 },   // Red
  { h: 30, s: 80, l: 55 },  // Orange
  { h: 120, s: 60, l: 50 }, // Green
  { h: 210, s: 80, l: 55 }, // Blue
  { h: 270, s: 70, l: 60 }, // Purple
];

function stringHash(str: string): number {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i);
  }
  return Math.abs(hash);
}

export function getTagColor(tagName: string): string {
  const hash = stringHash(tagName);
  const color = COLOR_PALETTE[hash % COLOR_PALETTE.length];
  return `hsl(${color.h}, ${color.s}%, ${color.l}%)`;
}
```

### Alternatives Considered

| Approach | Pros | Cons | Rejection Reason |
|----------|------|------|------------------|
| Random colors | Simple | Colors change on reload | Poor UX |
| Server-stored colors | Full control | Database overhead | Unnecessary complexity |
| Color from hash (RGB) | Simple | Can produce ugly colors | Poor visual quality |

### Integration Point
- New file: `/frontend/src/lib/tagColors.ts`

---

## 4. shadcn/ui Component Fixes

### Decision
**Custom width overrides via Tailwind utility classes on component instances**

### Rationale
1. **Current implementation is correct** - Dialog uses `sm:max-w-lg` with responsive `w-[95vw]`
2. **Tailwind CSS v4 compatible** - Existing code uses standard Tailwind utilities
3. **Override via className** - User-provided classes override defaults via `twMerge`
4. **No breaking changes needed** - Components already support custom widths

### Dialog Width Customization

```typescript
// Default behavior
"w-[95vw] sm:w-full sm:max-w-lg"

// Custom wide dialog
<DialogContent className="sm:max-w-2xl">
  {/* Content */}
</DialogContent>

// Custom narrow dialog
<DialogContent className="sm:max-w-md">
  {/* Content */}
</DialogContent>
```

### Sheet Width Customization

```typescript
// Default (right/left sheets)
"w-full sm:max-w-sm"

// Custom wider sheet
<SheetContent className="sm:max-w-md">
  {/* Content */}
</SheetContent>
```

### Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Dialog too narrow | Default `max-w-lg` (512px) | Add `className="sm:max-w-2xl"` |
| Dialog too wide | Large content expands it | Add `className="sm:max-w-md"` |
| Sheet not visible | Width 0 or hidden parent | Check parent container `overflow` |

### Integration Point
- Files: `/frontend/src/components/ui/dialog.tsx`, `/frontend/src/components/ui/sheet.tsx`
- Fix: Add className overrides where needed

---

## 5. Debounce Implementation

### Decision
**Use existing `debounce()` utility (already implemented in `lib/utils.ts`)**

### Rationale
The existing implementation is correct and production-ready:

```typescript
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);  // Proper cleanup
    timeout = setTimeout(() => func(...args), wait);
  };
}
```

This implementation:
- Properly cleans up previous timeouts
- Type-safe with TypeScript generics
- Prevents duplicate calls
- No memory leaks

### Usage Pattern

```typescript
const debouncedSearch = debounce((value: string) => {
  setFilters({ searchQuery: value });
  // Trigger API call
}, 300);

const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const value = e.target.value;
  debouncedSearch(value);
};
```

### Performance Metrics

| Delay (ms) | UX Impact | Network Savings |
|------------|-----------|-----------------|
| 300 | Good | Significant |
| 500 | Noticeable lag | High |

### Integration Point
- File: `/frontend/src/lib/utils.ts` (already exists)
- Usage: Apply to search input in `FilterBar.tsx`

---

## 6. Timezone Handling

### Decision
**Store all dates in UTC (PostgreSQL `TIMESTAMPTZ`), convert to user's timezone in frontend**

### Rationale
1. **Database stores UTC** - Use `TIMESTAMPTZ` for all timestamps
2. **Frontend detects timezone** - Use `Intl.DateTimeFormat().resolvedOptions().timeZone`
3. **"Due today" calculation** - Convert user's "today" to UTC range before querying
4. **Display in local time** - Format dates using user's timezone

### Backend Implementation

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def get_due_today_tasks(user_id: uuid.UUID, user_timezone: str = "UTC"):
    tz = ZoneInfo(user_timezone)
    now = datetime.now(tz)

    # Calculate today's start and end in user's timezone
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Convert to UTC for database query
    today_start_utc = today_start.astimezone(timezone.utc)
    today_end_utc = today_end.astimezone(timezone.utc)

    return session.query(Task).filter(
        Task.user_id == user_id,
        Task.due_date >= today_start_utc,
        Task.due_date <= today_end_utc
    ).all()
```

### Frontend Implementation

```typescript
// lib/timezone.ts
export function getUserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

export function formatDateInUserTimezone(date: string | Date): string {
  const tz = getUserTimezone();
  return new Date(date).toLocaleString('en-US', {
    timeZone: tz,
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
```

### Database Schema

```sql
-- Ensure timezone-aware timestamps
ALTER TABLE tasks
ALTER COLUMN due_date TYPE TIMESTAMPTZ,
ALTER COLUMN created_at TYPE TIMESTAMPTZ,
ALTER COLUMN updated_at TYPE TIMESTAMPTZ;
```

### Alternatives Considered

| Approach | Pros | Cons | Rejection Reason |
|----------|------|------|------------------|
| Store local time | Simple display | Breaks for traveling users | Database integrity issues |
| Store timezone with date | Explicit | Complex queries | Unnecessary complexity |
| UTC everywhere | Standard, reliable | Requires conversion | Industry best practice |

### Integration Point
- Backend: `/backend/api/tasks.py` (add timezone-aware filtering)
- Frontend: `/frontend/src/lib/timezone.ts` (new file)

---

## Summary of Decisions

| Feature | Approach | Complexity | Status |
|---------|----------|------------|--------|
| Priority Extraction | OpenAI Agents SDK with Pydantic | Low | Ready to implement |
| Client-Side Search | useMemo + nuqs (existing) | Low | Already implemented |
| Tag Colors | Hash function + HSL palette | Low | Ready to implement |
| Dialog/Sheet Width | Tailwind className overrides | Low | Already supported |
| Debounce | Existing utility | None | Already implemented |
| Timezone Handling | UTC storage + frontend conversion | Medium | Ready to implement |

---

## Technology Compatibility

| Technology | Status | Notes |
|------------|--------|-------|
| FastAPI | Compatible | Python 3.13+, async/await |
| Next.js 16 | Compatible | App Router, Server Components |
| React 19 | Compatible | All patterns work |
| Tailwind CSS 4 | Compatible | Standard utility classes |
| SQLModel | Compatible | TIMESTAMPTZ support |
| Neon PostgreSQL | Compatible | Full timezone support |
| OpenAI Agents SDK | Compatible | Already in use |
| nuqs | Compatible | Already installed |

---

## Next Steps

1. **Phase 1**: Create data-model.md with Task entity extensions
2. **Phase 1**: Generate API contracts for new endpoints
3. **Phase 1**: Create quickstart.md for development setup
4. **Phase 1**: Update agent context with new technologies
