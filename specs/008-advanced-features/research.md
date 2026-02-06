# Research: Advanced Todo Features

**Feature**: 008-advanced-features | **Date**: 2026-02-04 | **Status**: Complete

## Overview

This document consolidates research findings for implementing advanced time-based task management features: due dates with datetime picker, browser notifications for reminders, and recurring tasks with automatic rescheduling.

---

## Research Topic 1: Date/Time Picker Component

### Question

Which date/time picker component should we use for setting task due dates?

### Decision

**Use existing shadcn/ui Calendar component with react-day-picker**

### Rationale

1. **Already Installed**: The project has `react-day-picker: ^9.13.0` in package.json
2. **Consistency**: Matches existing shadcn/ui component library
3. **Customizable**: Built with Tailwind CSS, matches our design system
4. **Lightweight**: Tree-shakeable, adds minimal bundle size
5. **Time Input**: Combine calendar with native `<input type="time">` for datetime selection

### Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| @mui/x-date-pickers | Full-featured | Heavy (100KB+), need to install MUI | Too much weight for one feature |
| react-datepicker | Simple | Outdated Material UI style | Not consistent with shadcn/ui |
| Native datetime-local | No dependencies | Poor mobile UX, inconsistent styling | Bad user experience |

### Implementation Notes

```typescript
// Use Popover + Calendar for date
<Popover>
  <PopoverTrigger>
    <Button variant="outline">{formattedDate}</Button>
  </PopoverTrigger>
  <PopoverContent>
    <Calendar mode="single" selected={date} onSelect={setDate} />
  </PopoverContent>
</Popover>

// Use native input for time
<Input type="time" value={time} onChange={(e) => setTime(e.target.value)} />
```

---

## Research Topic 2: Browser Notifications Architecture

### Question

How should we implement browser notifications for task reminders?

### Decision

**Use Web Notifications API with client-side polling (1-minute interval)**

### Rationale

1. **No Backend Changes**: Client-side only, no new API endpoints
2. **Simple Implementation**: Standard browser API, well-documented
3. **Permission Model**: Built-in permission prompt
4. **Cross-Browser**: Supported on Chrome 22+, Firefox 22+, Safari 7+

### Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Service Workers + Push API | Works when browser closed | Complex, requires VAPID keys, SSL | Over-engineered for MVP |
| react-push-notification | Wrapper library | Unnecessary abstraction | Native API is sufficient |
| OneSignal / Firebase | Rich features | Third-party dependency, privacy | Want to avoid external services |

### Implementation Strategy

```typescript
// Permission request (user-triggered)
const requestPermission = async () => {
  const permission = await Notification.requestPermission();
  return permission === 'granted';
};

// Schedule check (runs every minute)
useEffect(() => {
  const interval = setInterval(() => {
    checkTasksDue(tasks);
  }, 60000); // 1 minute
  return () => clearInterval(interval);
}, [tasks]);

// Send notification
const showNotification = (task: Task) => {
  new Notification('Task Due', {
    body: task.title,
    icon: '/icon.png',
    tag: task.id, // Prevents duplicates
  });
};
```

### Limitations

- **Browser Must Be Open**: Notifications only show when browser is running
- **No Background Sync**: Doesn't work when browser is closed (acceptable for MVP)
- **Permission Required**: Users can deny notifications (handle gracefully)

---

## Research Topic 3: Date Arithmetic for Recurrence

### Question

Which library should we use for calculating recurring task dates?

### Decision

**Use date-fns for all date arithmetic**

### Rationale

1. **Already Installed**: The project has `date-fns: ^4.1.0` in package.json
2. **Tree-Shakeable**: Only imports used functions (small bundle)
3. **Immutable**: Returns new dates, doesn't mutate (safer)
4. **Type-Safe**: Full TypeScript support
5. **Timezone Support**: Works well with UTC storage

### Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Luxon | Chainable API, timezones | Larger bundle (76KB vs 30KB) | date-fns is smaller |
| Day.js | Moment-like API | Less type-safe, fewer features | Prefer strong typing |
| Moment.js | Familiar API | Deprecated, large (67KB) | No longer maintained |

### Implementation Examples

```typescript
import { addDays, addWeeks, addMonths, set } from 'date-fns';
import { utcToZonedTime, zonedTimeToUtc } from 'date-fns-tz';

// Daily recurrence
const nextDaily = addDays(currentDate, interval);

// Weekly recurrence
const nextWeekly = addWeeks(currentDate, interval);

// Monthly recurrence
const nextMonthly = addMonths(currentDate, interval);

// Preserve time component when advancing date
const nextDate = set(nextDaily, {
  hours: currentDate.getHours(),
  minutes: currentDate.getMinutes(),
  seconds: 0,
  milliseconds: 0,
});
```

---

## Research Topic 4: Recurrence Rule Storage Format

### Question

How should we store recurrence rules in the database?

### Decision

**Store as JSONB in PostgreSQL, serialize to/from TypeScript interface**

### Rationale

1. **Flexible Schema**: Can add fields without migration
2. **SQLModel Support**: Built-in JSON column type
3. **Queryable**: PostgreSQL JSON operators for filtering
4. **Type-Safe**: TypeScript interface on frontend, Pydantic on backend

### Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Separate table | Normalized | Over-engineered, more joins | Not needed for MVP |
| Cron string | Powerful | Complex for users, parsing overhead | Too technical for users |
| String enum | Simple | Can't add parameters | Too inflexible |

### Data Structure

```typescript
// TypeScript interface (frontend)
interface RecurrenceRule {
  frequency: 'daily' | 'weekly' | 'monthly';
  interval?: number;        // Every N days/weeks/months (default: 1)
  count?: number;           // Maximum occurrences
  end_date?: string;        // ISO 8601 date
}

// Example: "Every 2 weeks for 10 times"
{
  frequency: 'weekly',
  interval: 2,
  count: 10
}

// Example: "Daily until December 31, 2026"
{
  frequency: 'daily',
  end_date: '2026-12-31'
}
```

```python
# Pydantic model (backend)
from pydantic import BaseModel
from typing import Optional, Literal

class RecurrenceRule(BaseModel):
    frequency: Literal['daily', 'weekly', 'monthly']
    interval: Optional[int] = 1
    count: Optional[int] = None
    end_date: Optional[datetime] = None
```

```sql
-- PostgreSQL JSONB column
CREATE TABLE tasks (
  -- ... other fields
  recurrence JSONB
);

-- Query for recurring tasks
SELECT * FROM tasks WHERE recurrence IS NOT NULL;
```

---

## Research Topic 5: Recurrence Limit Strategy

### Question

How do we prevent infinite recurring task loops?

### Decision

**Limit to 100 instances per recurring task, enforce count or end_date**

### Rationale

1. **Database Protection**: Prevents runaway recursion
2. **User Expectation**: Most recurring tasks are finite
3. **Performance**: Limits query complexity
4. **Manual Override**: Users can extend if needed

### Implementation Strategy

```python
MAX_RECURRING_INSTANCES = 100

def create_recurring_task(task: Task) -> Task:
    # Check if limit reached
    instance_count = count_instances_with_parent(task.parent_task_id)
    if instance_count >= MAX_RECURRING_INSTANCES:
        raise RecurrenceLimitError()

    # Check count limit
    if task.recurrence.count:
        if instance_count >= task.recurrence.count:
            return None  # Stop recurring

    # Check end date
    if task.recurrence.end_date:
        if next_due_date > task.recurrence.end_date:
            return None  # Stop recurring

    # Create next instance
    return Task(
        title=task.title,
        due_date=next_due_date,
        parent_task_id=task.parent_task_id,
        recurrence=task.recurrence
    )
```

---

## Research Topic 6: Overdue Detection and Display

### Question

How should we detect and display overdue tasks?

### Decision

**Client-side comparison: `task.due_date < now && !task.completed`**

### Rationale

1. **Simple**: No backend query changes
2. **Real-Time**: Updates as time passes
3. **Timezone-Aware**: Compare in user's local timezone
4. **Visual Indicator**: Badge with red background + "Overdue" text

### Implementation

```typescript
// Detection
const isOverdue = (task: Task): boolean => {
  if (!task.due_date || task.completed) return false;
  return new Date(task.due_date) < new Date();
};

// Display
{isOverdue(task) && (
  <Badge variant="destructive">Overdue</Badge>
)}

// Relative time formatting
import { formatDistanceToNow } from 'date-fns';

const dueText = task.due_date
  ? isOverdue(task)
    ? `Overdue ${formatDistanceToNow(new Date(task.due_date))} ago`
    : `Due in ${formatDistanceToNow(new Date(task.due_date))}`
  : 'No due date';
```

---

## Research Topic 7: Timezone Handling Strategy

### Question

How do we handle timezones for due dates?

### Decision

**Store in UTC, display in user's local timezone**

### Rationale

1. **Database Standard**: UTC is storage best practice
2. **DST Safe**: Automatic daylight saving time adjustment
3. **User Expectation**: Dates display in their local time
4. **Consistent**: Matches existing Task model behavior

### Implementation

```python
# Backend: Store as UTC (already implemented)
from datetime import datetime, timezone

task.due_date = datetime.now(timezone.utc)  # Always UTC
```

```typescript
// Frontend: Display in local timezone
import { format } from 'date-fns';

const dueDate = new Date(task.due_date); // Browser auto-converts to local
const formatted = format(dueDate, 'PPp'); // "Jan 4, 2026, 11:30 AM"
```

---

## Research Topic 8: Notification Grouping Strategy

### Question

How do we handle multiple tasks due at the same time?

### Decision

**Use Notification.tag to group, show count in body**

### Rationale

1. **Browser Native**: Built-in grouping support
2. **Single Notification**: Doesn't spam user
3. **Clear Information**: Shows count of due tasks

### Implementation

```typescript
const checkTasksDue = (tasks: Task[]) => {
  const dueTasks = tasks.filter(isDueNow);

  if (dueTasks.length === 0) return;

  if (dueTasks.length === 1) {
    // Single task notification
    showTaskNotification(dueTasks[0]);
  } else {
    // Grouped notification
    new Notification('Tasks Due', {
      body: `You have ${dueTasks.length} tasks due now`,
      tag: 'tasks-due', // Groups multiple notifications
      data: { taskIds: dueTasks.map(t => t.id) }
    });
  }
};
```

---

## Research Topic 9: Reminder Offset Options

### Question

What reminder offset options should we offer?

### Decision

**Preset options: "At due time", "15 minutes before", "1 hour before", "1 day before"**

### Rationale

1. **Common Use Cases**: Covers most user needs
2. **Simple UI**: Radio buttons, no complex input
3. **Clear Labels**: Easy to understand
4. **Extendable**: Can add more options later

### Alternatives Considered

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Custom minutes input | Flexible | Complex, error-prone | Presets cover most cases |
| Multiple reminders | Powerful | UI complexity | Out of scope for MVP |

### Implementation

```typescript
const reminderOptions = [
  { label: 'At due time', value: 0 },
  { label: '15 minutes before', value: 15 },
  { label: '1 hour before', value: 60 },
  { label: '1 day before', value: 1440 },
];

// Calculate reminder time
const reminderTime = new Date(dueDate.getTime() - reminderOffset * 60000);
```

---

## Summary of Technology Choices

| Area | Technology | Status |
|------|-----------|--------|
| Date Picker | shadcn/ui Calendar + react-day-picker | ✅ Already installed |
| Time Input | Native `<input type="time">` | ✅ No dependency |
| Notifications | Web Notifications API | ✅ Browser native |
| Date Math | date-fns | ✅ Already installed |
| Recurrence Storage | PostgreSQL JSONB | ✅ SQLModel support |
| Polling | setInterval (1 minute) | ✅ No dependency |
| Timezone | UTC storage, local display | ✅ Existing pattern |

---

## Open Questions Resolved

**None** - all research topics have clear decisions with rationale.

---

## Next Steps

1. ✅ Phase 0: Research complete (this document)
2. ⏳ Phase 1: Create data-model.md
3. ⏳ Phase 1: Create contracts/ with API specs
4. ⏳ Phase 1: Create quickstart.md
5. ⏳ Phase 1: Update agent context
6. ⏳ Phase 2: Generate tasks.md

---

**Research Version**: 1.0.0
**Last Updated**: 2026-02-04
**Status**: Complete
