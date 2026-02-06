# Quick Start: Advanced Todo Features

**Feature**: 008-advanced-features | **Date**: 2026-02-04 | **Status**: Complete

## Overview

This guide provides step-by-step instructions for integrating and testing the advanced time-based task management features: due dates, reminders, and recurring tasks.

---

## Prerequisites

1. **Phase 007 Complete**: Ensure intermediate todo features (priority, tags, filters, sort, search) are implemented
2. **Database Access**: Neon PostgreSQL connection available
3. **Dependencies Installed**: Both backend and frontend dependencies installed

---

## Installation Steps

### 1. Database Migration

Run the migration to add new columns to the tasks table:

```bash
cd backend
uv run python -c "
from database import engine
from sqlmodel import SQLModel, text

# Create migration SQL
migration_sql = '''
ALTER TABLE tasks
  ADD COLUMN IF NOT EXISTS reminder_offset INTEGER,
  ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS recurrence JSONB,
  ADD COLUMN IF NOT EXISTS parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_tasks_parent_task_id ON tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_reminder_sent ON tasks(reminder_sent) WHERE reminder_sent = FALSE;
'''

with engine.begin() as conn:
    conn.execute(text(migration_sql))
    print('Migration completed successfully!')
"
```

### 2. Backend Model Extensions

The backend Task model is extended in `backend/models/task.py`:

```python
# Add to existing Task class
class Task(SQLModel, table=True):
    # ... existing fields ...

    # NEW: Reminder fields
    reminder_offset: Optional[int] = Field(default=None)
    reminder_sent: bool = Field(default=False)

    # NEW: Recurrence fields
    recurrence: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    parent_task_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tasks.id")
```

### 3. Frontend Type Extensions

Add to `frontend/src/types/task.ts`:

```typescript
export interface Task {
  // ... existing fields ...
  due_date: string | null;
  reminder_offset: number | null;
  reminder_sent: boolean;
  recurrence: RecurrenceRule | null;
  parent_task_id: string | null;
}

export interface RecurrenceRule {
  frequency: 'daily' | 'weekly' | 'monthly';
  interval?: number;
  count?: number;
  end_date?: string;
}
```

---

## Development Quick Start

### Backend Development

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

Backend runs on http://localhost:8000

### Frontend Development

```bash
cd frontend
pnpm install
pnpm dev
```

Frontend runs on http://localhost:3000

---

## Feature Testing Guide

### Test 1: Create Task with Due Date

1. Navigate to http://localhost:3000
2. Click "Add Task" button
3. Enter task title: "Submit weekly report"
4. Click "Due Date" field
5. Select tomorrow's date from calendar
6. Select time: 5:00 PM
7. Click "Create Task"
8. **Expected**: Task appears in list with due date displayed

### Test 2: Set Reminder Offset

1. Edit an existing task
2. Under "Reminder", select "15 minutes before"
3. Save the task
4. **Expected**: Task shows reminder icon/badge

### Test 3: Browser Notification

1. Create a task due within 2 minutes
2. Set reminder to "At due time"
3. Grant notification permission when prompted
4. Wait for the due time
5. **Expected**: Browser notification appears with task title

### Test 4: Create Daily Recurring Task

1. Create new task
2. Set title: "Take medication"
3. Set due date: today at 9:00 AM
4. Enable "Recurring" toggle
5. Select frequency: "Daily"
6. Click "Create Task"
7. **Expected**: Task shows recurring icon

### Test 5: Complete Recurring Task

1. Find the recurring task created above
2. Click the checkbox to mark complete
3. **Expected**:
   - Task is marked complete
   - New task appears with tomorrow's date
   - New task has same title and settings

### Test 6: Overdue Task Display

1. Create a task with yesterday's due date
2. **Expected**: Task appears with red "Overdue" badge

### Test 7: Filter by Due Date

1. In the filter bar, select "Due this week"
2. **Expected**: Only tasks due within 7 days shown

---

## API Testing Examples

### Using curl

**Create task with due date and reminder**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team standup",
    "due_date": "2026-02-05T09:00:00Z",
    "reminder_offset": 15,
    "recurrence": {
      "frequency": "weekly",
      "interval": 1
    }
  }'
```

**Get tasks due this week**:
```bash
curl -X GET "http://localhost:8000/api/tasks?due_after=2026-02-03T00:00:00Z&due_before=2026-02-09T23:59:59Z" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Complete recurring task**:
```bash
curl -X POST http://localhost:8000/api/tasks/TASK_ID/complete \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Using Python

```python
import httpx
import json

API_URL = "http://localhost:8000"
JWT_TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

# Create recurring task
task_data = {
    "title": "Daily standup",
    "due_date": "2026-02-05T09:00:00Z",
    "reminder_offset": 15,
    "recurrence": {
        "frequency": "daily",
        "interval": 1
    }
}

response = httpx.post(
    f"{API_URL}/api/tasks",
    headers=headers,
    json=task_data
)

task = response.json()
print(f"Created task: {task['id']}")

# Complete task (creates next instance)
response = httpx.post(
    f"{API_URL}/api/tasks/{task['id']}/complete",
    headers=headers,
    json={"completed": True}
}

result = response.json()
if result.get("next_instance"):
    print(f"Next instance created: {result['next_instance']['id']}")
```

---

## Component Integration

### Adding Due Date Picker to TaskForm

```typescript
// frontend/src/components/tasks/TaskForm.tsx
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { format } from 'date-fns';

export function TaskForm() {
  const [dueDate, setDueDate] = useState<Date | undefined>();

  return (
    <div className="space-y-4">
      {/* Due Date Picker */}
      <div>
        <label>Due Date</label>
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline">
              {dueDate ? format(dueDate, 'PPP') : 'Pick a date'}
            </Button>
          </PopoverTrigger>
          <PopoverContent>
            <Calendar
              mode="single"
              selected={dueDate}
              onSelect={setDueDate}
            />
          </PopoverContent>
        </Popover>
      </div>

      {/* Time Input */}
      <div>
        <label>Time</label>
        <input type="time" />
      </div>
    </div>
  );
}
```

### Adding NotificationManager

```typescript
// frontend/src/components/tasks/NotificationManager.tsx
'use client';

import { useEffect } from 'react';
import { toast } from 'sonner';

export function NotificationManager({ tasks }: { tasks: Task[] }) {
  useEffect(() => {
    // Request permission on mount
    if ('Notification' in window) {
      Notification.requestPermission();
    }

    // Check every minute
    const interval = setInterval(() => {
      checkNotifications(tasks);
    }, 60000);

    return () => clearInterval(interval);
  }, [tasks]);

  const checkNotifications = (tasks: Task[]) => {
    const now = new Date();

    tasks.forEach(task => {
      if (!task.due_date || task.reminder_sent) return;

      const dueDate = new Date(task.due_date);
      const reminderTime = new Date(dueDate.getTime() - (task.reminder_offset || 0) * 60000);

      if (now >= reminderTime) {
        showNotification(task);
        updateReminderSent(task.id);
      }
    });
  };

  const showNotification = (task: Task) => {
    new Notification('Task Due', {
      body: task.title,
      icon: '/icon.png',
      tag: task.id,
    });
  };

  return null; // Invisible component
}
```

---

## Troubleshooting

### Issue: Notifications Not Appearing

**Symptoms**: Task due time passes, no notification shown

**Solutions**:
1. Check browser permissions: Settings → Site Settings → Notifications
2. Verify `Notification.permission === 'granted'`
3. Check browser console for errors
4. Ensure NotificationManager component is mounted

### Issue: Recurring Task Not Creating Next Instance

**Symptoms**: Complete recurring task, no new task appears

**Solutions**:
1. Check if recurrence limit reached (100 instances max)
2. Verify `end_date` or `count` in recurrence rule
3. Check API response for `next_instance` field
4. Review backend logs for recurrence calculation errors

### Issue: Due Date Shows Wrong Time

**Symptoms**: Due date displays different time than selected

**Solutions**:
1. Verify due date is stored in UTC on backend
2. Check frontend date conversion uses local timezone
3. Ensure consistent timezone handling (date-fns `format` with `tz` option)

### Issue: Overdue Badge Not Showing

**Symptoms**: Past-due task doesn't show overdue indicator

**Solutions**:
1. Check `isOverdue()` function logic
2. Ensure comparison uses same timezone
3. Verify `completed: false` condition

---

## Performance Considerations

1. **Database Indexing**: Ensure `due_date`, `parent_task_id`, and `reminder_sent` are indexed
2. **Notification Polling**: Only poll tasks with due dates in next 24 hours
3. **Recurrence Calculation**: Cache calculated dates for display
4. **Date Formatting**: Memoize formatted dates in list components

---

## Security Notes

1. **User Data Isolation**: All queries scoped to `user_id`
2. **Validation**: Backend validates all recurrence rules
3. **Rate Limiting**: Consider rate limiting notification API calls
4. **Permission Handling**: Handle denied notification permissions gracefully

---

## Next Steps

1. ✅ Run database migration
2. ✅ Extend backend models
3. ✅ Extend frontend types
4. ⏳ Implement UI components (TaskForm extensions, NotificationManager, RecurrencePicker)
5. ⏳ Implement backend services (RecurrenceService)
6. ⏳ Test all user stories
7. ⏳ Update documentation

---

**Quick Start Version**: 1.0.0
**Last Updated**: 2026-02-04
**Status**: Complete
