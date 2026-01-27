# Data Model: UI/UX Improvements

**Feature**: 005-ux-improvement
**Date**: 2026-01-24
**Status**: Complete

## Overview

This feature is primarily a frontend UX improvement. No new database entities are required. The existing Task model from the backend already contains all necessary fields (`due_date`, `priority`) that are currently not displayed in the UI.

## Existing Entities (From Backend)

### Task

**Source**: `backend/models/task.py`

```python
class Task(SQLModel, table=True):
    """Database table model for Task entity."""
    __tablename__ = "tasks"

    id: uuid.UUID              # Primary key
    user_id: uuid.UUID          # Foreign key to users
    title: str                  # Required, max 255 chars
    description: Optional[str]  # Optional, max 2000 chars
    due_date: Optional[datetime] # Currently NOT displayed in UI
    priority: str               # "medium" by default, NOT displayed in UI
    completed: bool             # False by default
    created_at: datetime        # Creation timestamp
    updated_at: datetime        # Last update timestamp
```

### User

**Source**: `backend/models/user.py`

```python
class User(SQLModel, table=True):
    """Database table model for User entity."""
    __tablename__ = "users"

    id: uuid.UUID              # Primary key
    email: str                  # Unique email address
    hashed_password: str        # Bcrypt hashed password
    created_at: datetime        # Account creation timestamp
```

### ChatSession / Message

**Source**: `backend/models/conversation.py`, `backend/models/message.py`

```python
class Conversation(SQLModel, table=True):
    """Chat conversation session."""
    __tablename__ = "conversations"

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

class Message(SQLModel, table=True):
    """Chat message in conversation."""
    __tablename__ = "messages"

    id: uuid.UUID
    conversation_id: uuid.UUID  # Foreign key
    role: str                   # "user" or "assistant"
    content: str                # Message content
    created_at: datetime
```

---

## Frontend Type Definitions

### Task Type (Enhanced)

**Current** (`frontend/src/types/task.ts`):
```typescript
interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}
```

**Enhanced** (to display missing data):
```typescript
interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  due_date: string | null;        // ADD: Display formatted due date
  priority: 'low' | 'medium' | 'high';  // ADD: Display priority badge
  completed: boolean;
  created_at: string;
  updated_at: string;

  // Computed UI properties (not from backend)
  urgency?: 'overdue' | 'due-today' | 'due-soon' | 'due-later' | 'none';
}
```

### Filter State Type (Enhanced)

**Current** (`frontend/src/types/filters.ts`):
```typescript
type TaskFilter = 'all' | 'active' | 'completed';
```

**Enhanced** (with nuqs serialization):
```typescript
type TaskFilter = 'all' | 'active' | 'completed';

type TaskPriority = 'low' | 'medium' | 'high';

type DueDateFilter = 'all' | 'overdue' | 'today' | 'week' | 'month';

interface FilterState {
  status: TaskFilter;
  search: string;
  priority?: TaskPriority;
  dueDate?: DueDateFilter;
  page: number;
}
```

---

## Component State Models

### Chatbot Dialog State

```typescript
interface ChatbotState {
  isOpen: boolean;
  isMinimized: boolean;
  messages: ChatMessage[];
  isConnected: boolean;
  isProcessing: boolean;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  toolCalls?: ToolCall[];
}

interface ToolCall {
  name: string;
  status: 'starting' | 'complete' | 'error';
  message: string;
}
```

### Toast Notification State

```typescript
type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastOptions {
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}
```

### Loading State Types

```typescript
type LoadingState =
  | 'idle'          // No loading
  | 'initial'       // Initial page load
  | 'refreshing'    // Background refresh
  | 'optimistic';   // Optimistic update pending
```

---

## Validation Rules

### Task Form Validation (Zod)

```typescript
import { z } from 'zod';

export const taskFormSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(255, 'Title must be less than 255 characters'),
  description: z.string()
    .max(2000, 'Description must be less than 2000 characters')
    .optional()
    .nullable(),
  due_date: z.coerce.date()
    .optional()
    .nullable(),
  priority: z.enum(['low', 'medium', 'high'])
    .default('medium'),
});

export type TaskFormSchema = z.infer<typeof taskFormSchema>;
```

### Filter State Validation (nuqs)

```typescript
import { parseAsStringLiteral, parseAsInteger, parseAsString } from 'nuqs';

export const filterParsers = {
  status: parseAsStringLiteral(['all', 'active', 'completed'])
    .withDefault('all'),
  search: parseAsString.withDefault(''),
  priority: parseAsStringLiteral(['low', 'medium', 'high'])
    .withDefault('medium'),
  dueDate: parseAsStringLiteral(['all', 'overdue', 'today', 'week', 'month'])
    .withDefault('all'),
  page: parseAsInteger.withDefault(1),
};
```

---

## UI State Transitions

### Task Item States

```
[Created] --> [Editing] --> [Saved]
    |            |
    v            v
[Completed] <-- [Toggling]
    |
    v
[Deleted]
```

### Chatbot Dialog States

```
[CLOSED] <---> [OPEN]
                  |
                  v
            [MINIMIZED] -- [EXPANDED]
                  |
                  v
            [PROCESSING] -- [IDLE]
```

---

## Data Flow

### Server-Side Data Fetching

```
DashboardPage (Server Component)
    |
    v
fetchTasks() from API
    |
    v
TaskList (Client Component) receives initialTasks
    |
    v
[User Interaction] --> Optimistic Update --> API Call --> Refresh/Revert
```

### Chatbot Message Flow

```
User Input
    |
    v
WebSocket.send()
    |
    v
Backend processes with AI
    |
    v
WebSocket streams response
    |
    v
UI updates in real-time
```

---

## Summary

**No new database entities required.** This feature focuses on:

1. **Displaying existing data**: `due_date`, `priority` fields already exist in Task model
2. **Frontend type enhancements**: Adding TypeScript types for UI state
3. **State management**: Using nuqs for URL-based filter/search state
4. **Component state**: Managing dialog, toast, and loading states

All backend entities remain unchanged. The frontend will be enhanced to display and interact with existing data more effectively.
