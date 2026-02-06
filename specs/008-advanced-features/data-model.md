# Data Model: Advanced Todo Features

**Feature**: 008-advanced-features | **Date**: 2026-02-04 | **Status**: Complete

## Overview

This document defines the data model extensions for advanced time-based task management features. The existing Task model is extended with reminder and recurrence fields while maintaining backward compatibility.

---

## Entity Definitions

### Task (Extended)

**Description**: Core task entity, extended with reminder and recurrence capabilities.

**Existing Fields** (unchanged):
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid | PK, indexed | Unique identifier |
| user_id | uuid | FK → users.id, indexed | Owner |
| title | string | max 255 chars | Task name |
| description | string | optional, max 2000 chars | Details |
| priority | enum | HIGH/MEDIUM/LOW, default MEDIUM | Importance |
| tags | array | string[], max 50 chars each | Labels |
| due_date | datetime | optional, indexed, UTC | Deadline |
| completed | boolean | default false | Status |
| created_at | datetime | UTC | Creation time |
| updated_at | datetime | UTC | Last update |

**New Fields**:
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| reminder_offset | integer | optional, minutes | Offset before due_date to notify |
| reminder_sent | boolean | default false, indexed | Notification status |
| recurrence | jsonb | optional | Recurrence rule (see below) |
| parent_task_id | uuid | optional, FK → tasks.id, indexed | Links recurring instances |

**Indexes**:
```sql
-- Existing (unchanged)
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- New
CREATE INDEX idx_tasks_parent_task_id ON tasks(parent_task_id);
CREATE INDEX idx_tasks_reminder_sent ON tasks(reminder_sent) WHERE reminder_sent = FALSE;
```

**Relationships**:
```
Task (parent) 1──N Task (instances via parent_task_id)
Task ────→ User (via user_id)
```

**State Transitions**:
```
Task Creation → Due Date Set → Reminder Scheduled → Reminder Sent → Task Completed
                                                            ↓
                                                     (if recurring)
                                                            ↓
                                                Next Instance Created
```

---

### RecurrenceRule (Embedded JSON)

**Description**: Defines how a task repeats. Stored as JSONB within Task table.

**Structure** (TypeScript):
```typescript
interface RecurrenceRule {
  // Required: How often the task repeats
  frequency: 'daily' | 'weekly' | 'monthly';

  // Optional: Repeat interval (default: 1)
  // Examples: 2 = every 2 days, 3 = every 3 weeks
  interval?: number;

  // Optional: Maximum number of occurrences
  // Example: 10 = create 10 instances then stop
  count?: number;

  // Optional: End date for recurrence
  // Example: "2026-12-31" = stop creating after this date
  end_date?: string;  // ISO 8601 date
}
```

**Structure** (Python/Pydantic):
```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class RecurrenceRule(BaseModel):
    """Defines how a task repeats."""

    frequency: Literal['daily', 'weekly', 'monthly'] = Field(
        ...,
        description="How often the task repeats"
    )

    interval: Optional[int] = Field(
        default=1,
        ge=1,
        le=365,
        description="Repeat every N periods (max 365)"
    )

    count: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Maximum number of occurrences (max 100)"
    )

    end_date: Optional[datetime] = Field(
        default=None,
        description="Stop recurring after this date"
    )
```

**Validation Rules**:
1. `interval`: Must be >= 1 and <= 365 (at most once per year)
2. `count`: Must be >= 1 and <= 100 (max instances limit)
3. `end_date`: Must be in the future
4. At least one of `count` or `end_date` should be set (prevents infinite loops)
5. Cannot set both `count` and `end_date` to empty/undefined

**Examples**:

| Description | Rule JSON |
|-------------|-----------|
| Daily forever | `{"frequency": "daily"}` |
| Weekly | `{"frequency": "weekly"}` |
| Every 2 weeks | `{"frequency": "weekly", "interval": 2}` |
| Monthly, 10 times | `{"frequency": "monthly", "count": 10}` |
| Daily until Dec 31 | `{"frequency": "daily", "end_date": "2026-12-31"}` |
| Every 3 days, 50 times | `{"frequency": "daily", "interval": 3, "count": 50}` |

---

## Database Schema (SQL)

### Migration Script

```sql
-- Migration: Add advanced features to tasks table
-- Version: 008_advanced_features
-- Date: 2026-02-04

-- Step 1: Add new columns
ALTER TABLE tasks
  ADD COLUMN reminder_offset INTEGER,
  ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE,
  ADD COLUMN recurrence JSONB,
  ADD COLUMN parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL;

-- Step 2: Create indexes for performance
CREATE INDEX idx_tasks_parent_task_id ON tasks(parent_task_id);
CREATE INDEX idx_tasks_reminder_sent ON tasks(reminder_sent) WHERE reminder_sent = FALSE;

-- Step 3: Add constraints
ALTER TABLE tasks
  ADD CONSTRAINT chk_reminder_offset_positive
    CHECK (reminder_offset IS NULL OR reminder_offset >= 0);

ALTER TABLE tasks
  ADD CONSTRAINT chk_recurrence_no_self_reference
    CHECK (parent_task_id IS NULL OR id != parent_task_id);

-- Step 4: Add comments for documentation
COMMENT ON COLUMN tasks.reminder_offset IS 'Minutes before due_date to send notification (0 = at due time)';
COMMENT ON COLUMN tasks.reminder_sent IS 'Whether notification has been sent for this task';
COMMENT ON COLUMN tasks.recurrence IS 'Recurrence rule as JSONB (frequency, interval, count, end_date)';
COMMENT ON COLUMN tasks.parent_task_id IS 'For recurring task instances, links to the original task';

-- Step 5: Create validation function for recurrence JSONB
CREATE OR REPLACE FUNCTION validate_recurrence(rule jsonb)
RETURNS boolean AS $$
BEGIN
  -- Check frequency is present and valid
  IF rule->>'frequency' NOT IN ('daily', 'weekly', 'monthly') THEN
    RETURN false;
  END IF;

  -- Check interval is valid if present
  IF (rule->>'interval') IS NOT NULL THEN
    IF (rule->>'interval')::integer < 1 OR (rule->>'interval')::integer > 365 THEN
      RETURN false;
    END IF;
  END IF;

  -- Check count is valid if present
  IF (rule->>'count') IS NOT NULL THEN
    IF (rule->>'count')::integer < 1 OR (rule->>'count')::integer > 100 THEN
      RETURN false;
    END IF;
  END IF;

  RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Add check constraint using validation function
ALTER TABLE tasks
  ADD CONSTRAINT chk_recurrence_valid
    CHECK (recurrence IS NULL OR validate_recurrence(recurrence));
```

### Rollback Script

```sql
-- Rollback: Remove advanced features columns
-- WARNING: This will delete all reminder and recurrence data

DROP INDEX IF EXISTS idx_tasks_parent_task_id;
DROP INDEX IF EXISTS idx_tasks_reminder_sent;

ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_recurrence_valid;
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_recurrence_no_self_reference;
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_reminder_offset_positive;

ALTER TABLE tasks DROP COLUMN IF EXISTS parent_task_id;
ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence;
ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_sent;
ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_offset;

DROP FUNCTION IF EXISTS validate_recurrence(jsonb);
```

---

## API Data Transfer Objects

### TypeScript Types (Frontend)

```typescript
// src/types/task.ts

import type { RecurrenceRule } from './recurrence';

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  tags: string[];
  due_date: string | null;        // ISO 8601 datetime (UTC)
  reminder_offset: number | null; // Minutes before due_date
  reminder_sent: boolean;
  completed: boolean;
  recurrence: RecurrenceRule | null;
  parent_task_id: string | null;
  created_at: string;             // ISO 8601 datetime (UTC)
  updated_at: string;             // ISO 8601 datetime (UTC)
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: 'HIGH' | 'MEDIUM' | 'LOW';
  tags?: string[];
  due_date?: string;              // ISO 8601 datetime (UTC)
  reminder_offset?: number;       // Minutes before due_date
  recurrence?: RecurrenceRule;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: 'HIGH' | 'MEDIUM' | 'LOW';
  tags?: string[];
  due_date?: string;
  reminder_offset?: number;
  completed?: boolean;
  recurrence?: RecurrenceRule | null; // null = remove recurrence
}

export interface TaskListFilters {
  status?: 'all' | 'active' | 'completed';
  priority?: 'HIGH' | 'MEDIUM' | 'LOW';
  tags?: string[];
  search?: string;
  due_before?: string;            // ISO 8601 date (for filtering)
  due_after?: string;             // ISO 8601 date (for filtering)
  sort_by?: 'created_at' | 'due_date' | 'priority' | 'title';
  sort_order?: 'asc' | 'desc';
}
```

### Python Models (Backend)

```python
# backend/models/task.py (extended)

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, String, JSON

class PriorityLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RecurrenceRule(BaseModel):
    """Recurrence rule for repeating tasks."""
    frequency: Literal['daily', 'weekly', 'monthly']
    interval: int = Field(default=1, ge=1, le=365)
    count: Optional[int] = Field(default=None, ge=1, le=100)
    end_date: Optional[datetime] = None

class Task(SQLModel, table=True):
    """Database table model for Task entity."""
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    tags: list[str] = Field(default=[], sa_column=Column(ARRAY(String), nullable=False))

    # Due date fields
    due_date: Optional[datetime] = Field(default=None, index=True)

    # Reminder fields (NEW)
    reminder_offset: Optional[int] = Field(default=None)  # Minutes before due
    reminder_sent: bool = Field(default=False)

    # Recurrence fields (NEW)
    recurrence: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True)
    )
    parent_task_id: Optional[UUID] = Field(default=None, foreign_key="tasks.id")

    # Status fields
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(SQLModel):
    """Request model for creating a task."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    tags: list[str] = Field(default=[])
    due_date: Optional[datetime] = None
    reminder_offset: Optional[int] = Field(default=None, ge=0)
    recurrence: Optional[RecurrenceRule] = None
    completed: bool = False

class TaskUpdate(SQLModel):
    """Request model for updating a task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[PriorityLevel] = None
    tags: Optional[list[str]] = None
    due_date: Optional[datetime] = None
    reminder_offset: Optional[int] = Field(default=None, ge=0)
    completed: Optional[bool] = None
    recurrence: Optional[RecurrenceRule] = None

class TaskRead(SQLModel):
    """Response model for task data."""
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    priority: PriorityLevel
    tags: list[str]
    due_date: Optional[datetime]
    reminder_offset: Optional[int]
    reminder_sent: bool
    completed: bool
    recurrence: Optional[dict]
    parent_task_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
```

---

## State Machine

### Task Lifecycle with Recurrence

```
┌─────────────┐
│   Created   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Scheduled  │  (has due_date, !completed)
└──────┬──────┘
       │
       ├──────────────────────┐
       ▼                      ▼
┌─────────────┐      ┌─────────────┐
│   Overdue   │      │  Reminder   │  (reminder sent)
│ (past due)  │      │   Sent      │
└──────┬──────┘      └─────────────┘
       │
       ▼
┌─────────────┐
│  Completed  │
└──────┬──────┘
       │
       ▼ (if recurring)
┌─────────────┐
│  Next       │  (new instance created)
│  Instance   │
└─────────────┘
```

### Recurrence Termination Conditions

A recurring task stops creating new instances when:

1. **Count Limit Reached**: `instance_count >= recurrence.count`
2. **End Date Passed**: `next_due_date > recurrence.end_date`
3. **Max Limit Reached**: `total_instances >= 100` (safety limit)
4. **Recurrence Removed**: User sets `recurrence = null`

---

## Validation Rules Summary

| Field | Validation | Error Message |
|-------|-----------|---------------|
| due_date | Not >10 years in past | "Due date cannot be more than 10 years in the past" |
| reminder_offset | >= 0 | "Reminder offset must be positive" |
| recurrence.frequency | daily/weekly/monthly | "Invalid recurrence frequency" |
| recurrence.interval | 1-365 | "Interval must be between 1 and 365" |
| recurrence.count | 1-100 | "Count must be between 1 and 100" |
| recurrence.end_date | Must be future | "End date must be in the future" |
| parent_task_id | Cannot reference self | "Task cannot be its own parent" |

---

## Query Patterns

### Find Tasks Due Soon

```sql
-- Tasks due in next 24 hours that need reminders
SELECT * FROM tasks
WHERE user_id = $1
  AND due_date BETWEEN NOW() AND NOW() + INTERVAL '24 hours'
  AND reminder_sent = FALSE
  AND completed = FALSE;
```

### Find Overdue Tasks

```sql
-- Tasks past their due date
SELECT * FROM tasks
WHERE user_id = $1
  AND due_date < NOW()
  AND completed = FALSE
ORDER BY due_date ASC;
```

### Find Recurring Task Instances

```sql
-- All instances of a recurring task
SELECT * FROM tasks
WHERE parent_task_id = $1
ORDER BY due_date ASC;
```

### Count Recurring Instances

```sql
-- Check if recurrence limit reached
SELECT COUNT(*) as instance_count
FROM tasks
WHERE parent_task_id = $1;
```

---

## Data Integrity

### Constraints Enforced

1. **Foreign Keys**: `user_id` → users, `parent_task_id` → tasks
2. **Check Constraints**: All validation rules enforced at DB level
3. **Cascade Rules**: `ON DELETE SET NULL` for `parent_task_id`
4. **Indexes**: All foreign keys and frequently queried columns

### Transaction Safety

When completing a recurring task:
```python
@transaction
def complete_recurring_task(task_id: UUID) -> Task:
    # 1. Mark original task as complete
    task = session.get(Task, task_id)
    task.completed = True

    # 2. Check if should create next instance
    if should_create_next(task):
        # 3. Create next instance
        next_task = Task(
            title=task.title,
            due_date=calculate_next(task),
            parent_task_id=task.parent_task_id or task.id,
            recurrence=task.recurrence,
            user_id=task.user_id
        )
        session.add(next_task)

    # 4. Commit both changes atomically
    session.commit()
    return next_task
```

---

**Data Model Version**: 1.0.0
**Last Updated**: 2026-02-04
**Status**: Complete
