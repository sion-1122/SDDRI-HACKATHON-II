# Data Model: Intermediate Todo Features

**Feature**: 007-intermediate-todo-features
**Date**: 2026-01-28
**Phase**: Phase 1 (Design)

## Entity Definitions

### Task (Extended)

The existing Task entity is extended with three new fields: `priority`, `tags`, and `due_date`.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | UUID | Primary Key | auto-generated | Unique task identifier |
| `user_id` | UUID | Foreign Key, Not Null | - | Owner of the task |
| `title` | String | Not Null, Max 500 | - | Task title |
| `description` | String | Nullable, Max 5000 | null | Task description |
| `completed` | Boolean | Not Null | false | Task completion status |
| `priority` | Enum | Not Null | `medium` | Task priority level |
| `tags` | String[] | Not Empty Array | `[]` | Task category tags |
| `due_date` | TIMESTAMPTZ | Nullable, Indexed | null | Task due date (UTC) |
| `created_at` | TIMESTAMPTZ | Not Null | now | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | Not Null | now | Last update timestamp |

#### Priority Enum

```python
from enum import Enum

class PriorityLevel(str, Enum):
    """Task priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

#### Tag Array

Tags are stored as a PostgreSQL text array:

```sql
tags TEXT[] NOT NULL DEFAULT '{}'
```

#### Database Migration

```sql
-- Migration: Add priority, tags, and due_date to tasks table
ALTER TABLE tasks
  ADD COLUMN priority VARCHAR(10) NOT NULL DEFAULT 'medium',
  ADD COLUMN tags TEXT[] NOT NULL DEFAULT '{}',
  ADD COLUMN due_date TIMESTAMPTZ;

-- Add index for due_date queries
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Add check constraint for priority values
ALTER TABLE tasks
  ADD CONSTRAINT check_priority
  CHECK (priority IN ('high', 'medium', 'low'));

-- Backward compatibility: Existing records get Medium priority, empty tags, null due_date
```

### Tag (Virtual)

Tags are simple text labels stored as an array on the Task entity. No separate Tag table is required.

#### Tag Color Mapping

Tag colors are derived deterministically from the tag name using a hash function (see research.md).

---

## State Transitions

### Task Priority

```
[high]    <-> [medium] <-> [low]
    ^            ^            ^
    |            |            |
  User can change priority at any time via:
  - Natural language: "mark this as urgent"
  - Filter UI: Priority dropdown
  - Direct API: PUT /api/tasks/{id}
```

### Task Completion

```
[pending] -> [completed]
    ^            |
    |            v
  Can be toggled back via:
  - Natural language: "mark task as complete"
  - Task UI: Checkbox/button
  - Direct API: PATCH /api/tasks/{id}/complete
```

### Tag Association

```
[no tags] -> [tags added]
    ^            |
    |            v
  Tags can be added/removed via:
  - Natural language: "add tag 'work' to this task"
  - Task UI: Tag input field
  - Direct API: PATCH /api/tasks/{id}/tags
```

---

## Validation Rules

### Task Creation

| Field | Validation | Error Message |
|-------|-----------|---------------|
| `title` | Required, 1-500 chars | "Title is required" |
| `description` | Optional, max 5000 chars | "Description too long" |
| `priority` | One of: high, medium, low | "Invalid priority level" |
| `tags` | Array of strings, each max 50 chars | "Tag name too long" |
| `due_date` | ISO 8601 datetime or null | "Invalid date format" |

### Task Update

| Field | Validation | Error Message |
|-------|-----------|---------------|
| `title` | Optional, 1-500 chars if provided | "Title too long" |
| `description` | Optional, max 5000 chars | "Description too long" |
| `priority` | Optional, one of: high, medium, low | "Invalid priority level" |
| `tags` | Optional, array of strings | "Invalid tags format" |
| `due_date` | Optional, ISO 8601 datetime or null | "Invalid date format" |

### Filter/Sort Parameters

| Parameter | Type | Valid Values |
|-----------|------|--------------|
| `status` | string | `all`, `pending`, `completed` |
| `priority` | string[] | `high`, `medium`, `low` (any combination) |
| `tags` | string[] | Tag names (multi-select with AND logic) |
| `due_date` | string | `today`, `this_week`, `overdue`, `all` |
| `sort_by` | string | `due_date`, `priority`, `created_at`, `title` |
| `sort_order` | string | `asc`, `desc` |
| `search` | string | Free text search query |

---

## Relationships

### User -> Task (One-to-Many)

```
User (1) ----< (N) Task
  |
  +-- user_id (FK) --> Task.user_id
```

**Rules**:
- All tasks must have a valid `user_id`
- Users can only access their own tasks
- Deleting a user should cascade delete their tasks

### Task -> Tags (Many-to-Many, denormalized)

```
Task (1) ----< (N) Tag (stored as array)
  |
  +-- tags (TEXT[]) --> Tag names
```

**Rules**:
- Tags are stored as a text array on the Task entity
- No separate Tag table (denormalized for simplicity)
- Tag colors are derived deterministically in the frontend

---

## Indexes

```sql
-- Existing indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- New indexes for this feature
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_completed ON tasks(completed);

-- Composite index for common filter combinations
CREATE INDEX idx_tasks_user_priority_status
  ON tasks(user_id, priority, completed);

-- GIN index for tag array searching
CREATE INDEX idx_tasks_tags ON tasks USING GIN (tags);
```

---

## Database Schema Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                            tasks                                 │
├─────────────────────────────────────────────────────────────────┤
│ PK  id                   UUID                                    │
│ FK  user_id              UUID                                    │
│     title                VARCHAR(500) NOT NULL                   │
│     description          VARCHAR(5000)                           │
│     completed            BOOLEAN NOT NULL DEFAULT false          │
│     priority             VARCHAR(10) NOT NULL DEFAULT 'medium'   │
│     tags                 TEXT[] NOT NULL DEFAULT '{}'            │
│     due_date             TIMESTAMPTZ                             │
│     created_at           TIMESTAMPTZ NOT NULL DEFAULT now()      │
│     updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()      │
├─────────────────────────────────────────────────────────────────┤
│ Indexes:                                                           │
│   - idx_tasks_user_id                                             │
│   - idx_tasks_due_date                                            │
│   - idx_tasks_priority                                            │
│   - idx_tasks_completed                                           │
│   - idx_tasks_user_priority_status                                │
│   - idx_tasks_tags (GIN)                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Backward Compatibility

### Existing Data Migration

```sql
-- All existing tasks will have:
-- priority = 'medium' (default)
-- tags = '{}' (empty array)
-- due_date = NULL (no due date)

-- Example migration query
UPDATE tasks
SET
  priority = 'medium',
  tags = '{}'
WHERE priority IS NULL;
```

### API Backward Compatibility

- Existing API endpoints continue to work
- New fields are optional in requests
- New fields are included in responses (with defaults for old records)
- No breaking changes to existing endpoints

---

## Performance Considerations

### Query Optimization

1. **Client-side search** for < 100 tasks: Fetch all, filter in React
2. **Server-side search** for ≥ 100 tasks: Use PostgreSQL full-text search
3. **Tag filtering**: Use GIN index for array operations
4. **Due date queries**: Use indexed `due_date` column

### Caching Strategy

- Search results: Cache up to 10 recent queries
- Filter combinations: No caching (user-specific)
- Tag colors: Derived deterministically, no storage needed

---

## Security Considerations

### Data Isolation

- All queries filter by `user_id` from JWT token
- Users cannot access other users' tasks
- Tag names are user-scoped (no global tag namespace)

### Input Validation

- Tag names: Sanitize to prevent XSS, max 50 chars
- Search queries: Escape special characters, max 200 chars
- Date inputs: Validate ISO 8601 format, reject invalid dates
