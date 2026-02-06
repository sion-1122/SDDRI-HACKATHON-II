# Implementation Plan: Advanced Todo Features

**Branch**: `008-advanced-features` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-advanced-features/spec.md`

## Summary

Add time-based task management features including due dates with datetime picker UI, browser notifications for reminders, and recurring task support with automatic rescheduling. This feature extends the existing Task model with reminder and recurrence fields, integrates Web Notifications API, and implements client-side notification scheduling.

## Technical Context

**Language/Version**: TypeScript 5+ (frontend), Python 3.13+ (backend)
**Primary Dependencies**:
- Frontend: Next.js 16.1.1, React 19.2.3, shadcn/ui, date-fns, react-day-picker, Sonner
- Backend: FastAPI, SQLModel, Pydantic
**Storage**: Neon Serverless PostgreSQL (existing)
**Testing**: Documented but optional for this feature
**Target Platform**: Web (browser with Notifications API support)
**Project Type**: Full-stack web application (backend + frontend)
**Performance Goals**:
- Notification appears within 10 seconds of task becoming due
- Recurring task creates new instance within 5 seconds of completion
- Due date selection within 3 clicks
**Constraints**:
- Browser Notifications API requires user permission
- Notifications only work when browser is open (background via service worker not in scope)
- Client-side scheduling (no backend cron jobs)
- Maximum 100 recurring instances per task to prevent infinite loops
**Scale/Scope**: 10k users, 50k tasks with due dates, 10k recurring tasks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Persistent Storage | ✅ PASS | All new fields (reminder_offset, recurrence, parent_task_id) stored in PostgreSQL |
| II. RESTful API Excellence | ✅ PASS | New endpoints follow existing patterns, require JWT auth |
| III. Responsive Web UI | ✅ PASS | shadcn/ui components, mobile-first design |
| IV. Multi-User Architecture | ✅ PASS | All data scoped to authenticated user_id |
| V. Incremental Phase Evolution | ✅ PASS | Extends Phase II features, compatible with Phase III (AI chatbot) |
| VI. Monorepo Structure Standard | ✅ PASS | Uses existing backend/ and frontend/ directories |
| VII. Authentication & JWT Security | ✅ PASS | All endpoints require valid JWT |
| VIII. Frontend Architecture (Next.js) | ✅ PASS | Server Components by default, Client Components for interactivity |
| IX. Data Ownership & Isolation | ✅ PASS | All queries filter by user_id |
| X. API Response Consistency | ✅ PASS | Follows existing JSON response structure |
| XI. Containerization with Docker | ✅ PASS | Existing Dockerfiles support new code |
| XII. Kubernetes Orchestration | ✅ PASS | Existing K8s manifests support new code |
| XIII. Helm Chart Packaging | ✅ PASS | Existing Helm chart supports new code |
| XIV. AI-Assisted DevOps | ✅ PASS | N/A for this feature (no infrastructure changes) |
| XV. Cloud-Native Deployment Patterns | ✅ PASS | Stateless design, health checks unchanged |
| XVI. AIOps and Blueprints | ✅ PASS | N/A for this feature (no infrastructure changes) |

**Overall Status**: ✅ **PASS** - No constitution violations. All principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/008-advanced-features/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── api-endpoints.md # API contracts
│   └── openapi.yaml     # OpenAPI spec
└── tasks.md             # Phase 2 output (NOT created by this command)
```

### Source Code (repository root)

This feature uses the **existing monorepo structure** (Option 3: Full monorepo):

```text
backend/
├── models/
│   ├── task.py          # EXTEND: Add recurrence, reminder fields
│   └── recurrence.py    # NEW: RecurrenceRule model
├── services/
│   ├── recurrence_service.py  # NEW: Calculate next occurrence
│   └── notification_service.py # NEW: Notification scheduling logic
├── api/
│   └── tasks.py         # EXTEND: Add reminder/recurrence endpoints
└── tests/
    ├── test_recurrence_service.py
    └── test_task_api.py

frontend/
├── src/
│   ├── components/
│   │   ├── tasks/
│   │   │   ├── TaskForm.tsx           # EXTEND: Add date picker, recurrence
│   │   │   ├── TaskListItem.tsx       # EXTEND: Show due date, overdue badge
│   │   │   ├── RecurrencePicker.tsx   # NEW: Recurrence UI
│   │   │   └── NotificationManager.tsx # NEW: Permission & scheduling
│   │   └── ui/
│   │       └── calendar.tsx           # EXISTS: shadcn/ui calendar
│   ├── lib/
│   │   ├── hooks/
│   │   │   └── useNotifications.ts    # NEW: Notification hook
│   │   └── utils/
│   │       ├── dateFormatters.ts      # NEW: Date formatting utilities
│   │       └── recurrenceCalculator.ts # NEW: Next occurrence calculation
│   └── types/
│       └── task.ts                    # EXTEND: Add recurrence types
└── tests/
    └── notifications/
        └── notificationManager.test.ts
```

**Structure Decision**: Uses existing `backend/` and `frontend/` directories per Principle VI. Extends existing Task model and components rather than creating new modules. Follows monorepo standard with shared types across backend (Pydantic) and frontend (TypeScript).

## Complexity Tracking

> No constitution violations - this section is not applicable.

## Component Architecture

### Backend Components

#### 1. Task Model Extensions (`backend/models/task.py`)

**New Fields**:
```python
class Task(SQLModel, table=True):
    # ... existing fields
    reminder_offset: Optional[int] = Field(default=None)  # Minutes before due_date
    reminder_sent: bool = Field(default=False)
    recurrence: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    parent_task_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tasks.id")
```

**Rationale**:
- `reminder_offset`: Stores offset in minutes (e.g., 15 = 15 min before due)
- `reminder_sent`: Prevents duplicate notifications
- `recurrence`: JSON column stores recurrence rule (flexible for future patterns)
- `parent_task_id`: Links recurring instances to original task

#### 2. Recurrence Service (`backend/services/recurrence_service.py`)

**Responsibilities**:
- Calculate next occurrence from recurrence rule
- Support daily, weekly, monthly frequencies
- Support custom intervals (every N days/weeks/months)
- Handle count limits and end dates
- Validate cron expressions (for P3 custom recurrence)

**Interface**:
```python
class RecurrenceService:
    def calculate_next_occurrence(
        self,
        base_date: datetime,
        recurrence_rule: dict
    ) -> Optional[datetime]:
        """Calculate next due date based on recurrence pattern."""

    def validate_recurrence_rule(
        self,
        rule: dict
    ) -> bool:
        """Validate recurrence rule structure."""
```

#### 3. Task API Extensions (`backend/api/tasks.py`)

**New Endpoints**:
```
POST   /api/tasks                    # EXTEND: Accept recurrence, reminder_offset
GET    /api/tasks?due_before=...     # NEW: Filter by due date range
PUT    /api/tasks/{id}               # EXTEND: Update recurrence, reminder_offset
POST   /api/tasks/{id}/complete      # EXTEND: Create next recurring instance
```

### Frontend Components

#### 1. Task Form Extensions (`frontend/src/components/tasks/TaskForm.tsx`)

**New UI Elements**:
- Due date picker (shadcn/ui Calendar + Popover)
- Reminder offset selector (Select: "At due time", "15 min before", "1 hr before", "1 day before")
- Recurrence toggle (Switch)
- Recurrence pattern picker (Select: Daily, Weekly, Monthly)

**User Flow**:
1. User clicks "Due Date" field
2. Calendar popover appears
3. User selects date and time
4. User optionally sets reminder offset
5. User optionally enables recurrence
6. Form submits with extended data

#### 2. Task List Item Extensions (`frontend/src/components/tasks/TaskListItem.tsx`)

**New UI Elements**:
- Due date display (formatted relative time: "Due in 2 days", "Overdue by 3 days")
- Overdue badge (red background for past-due tasks)
- Recurring indicator (icon showing repeat pattern)

**Overdue Detection**:
```typescript
const isOverdue = task.due_date && new Date(task.due_date) < new Date();
```

#### 3. Notification Manager (`frontend/src/components/tasks/NotificationManager.tsx`)

**Responsibilities**:
- Request notification permission on mount
- Schedule notifications for tasks with due dates
- Check every minute for tasks due soon
- Group multiple notifications
- Handle notification clicks (navigate to task)

**Implementation**:
```typescript
export function NotificationManager({ tasks }: { tasks: Task[] }) {
  useEffect(() => {
    // Request permission
    Notification.requestPermission();

    // Check every minute
    const interval = setInterval(() => {
      checkAndSendNotifications(tasks);
    }, 60000);

    return () => clearInterval(interval);
  }, [tasks]);
}
```

#### 4. Recurrence Picker (`frontend/src/components/tasks/RecurrencePicker.tsx`)

**UI Components**:
- Frequency selector (Select: Daily, Weekly, Monthly)
- Interval input (number input: "Every X days/weeks/months")
- End condition selector (Radio: "Never", "After X times", "On date")

**State**:
```typescript
interface RecurrenceRule {
  frequency: 'daily' | 'weekly' | 'monthly';
  interval?: number;
  count?: number;
  end_date?: string;
}
```

## Data Flow

### Due Date Flow

```
User → TaskForm → Select Date/Time → API Create Task → Store UTC → Display Local Time
```

### Reminder Flow

```
1. User sets due_date + reminder_offset in TaskForm
2. Task saved to DB with due_date (UTC) and reminder_offset (minutes)
3. NotificationManager checks every minute
4. Calculate reminder_time = due_date - reminder_offset
5. If now >= reminder_time and !reminder_sent:
   - Show browser notification
   - Update task.reminder_sent = true
   - Call API to update reminder_sent
```

### Recurring Task Flow

```
1. User completes recurring task
2. API call: POST /api/tasks/{id}/complete
3. Backend checks if task has recurrence rule
4. Calculate next_due_date = calculate_next_occurrence(due_date, recurrence)
5. Create new task with:
   - same title, description, priority, tags
   - new due_date = next_due_date
   - parent_task_id = original task.id
   - recurrence = same rule
6. Return new task in response
7. Frontend updates UI with new task
```

## Technology Decisions (Phase 0 Research)

### 1. Date/Time Picker: shadcn/ui Calendar + react-day-picker

**Decision**: Use existing `calendar.tsx` component with `react-day-picker` library

**Rationale**:
- Already installed (`react-day-picker: ^9.13.0`)
- Consistent with existing UI library
- Customizable with Tailwind CSS
- Supports date range selection
- Time input via native `<input type="time">`

**Alternatives Considered**:
- `@mui/x-date-pickers`: Too heavy, additional dependency
- `react-datepicker`: Outdated styling, not consistent with shadcn/ui
- Native `<input type="datetime-local">`: Poor UX on mobile

### 2. Browser Notifications: Web Notifications API

**Decision**: Use native browser `Notification` API

**Rationale**:
- No additional dependencies
- Works on all modern browsers
- Supports actions, vibration, sound
- Can be triggered from client-side JavaScript

**Alternatives Considered**:
- `react-push-notification`: Wrapper, not needed
- Service Workers with Push API: Overkill for this use case
- OneSignal: Third-party dependency, privacy concerns

### 3. Recurrence Calculation: date-fns

**Decision**: Use `date-fns` for date arithmetic

**Rationale**:
- Already installed (`date-fns: ^4.1.0`)
- Tree-shakeable (small bundle size)
- Immutable operations
- Good timezone support (via `date-fns-tz`)

**Alternatives Considered**:
- `luxon`: Heavier, fewer features
- `dayjs`: Less type-safe
- `moment.js`: Deprecated, large bundle

### 4. Notification Scheduling: Client-Side Polling

**Decision**: Poll every minute on client-side

**Rationale**:
- Simple implementation
- Works without backend changes
- Stops when browser closes (acceptable for MVP)
- 1-minute interval is acceptable per spec (10 second target)

**Alternatives Considered**:
- `setTimeout` for each task: Doesn't handle time changes, timezone shifts
- Backend cron jobs: Requires persistent worker process
- Web Workers: Overkill for simple polling

### 5. Recurrence Rule Storage: JSON Column

**Decision**: Store recurrence rule as JSON in PostgreSQL

**Rationale**:
- Flexible schema (can add fields without migration)
- SQLModel supports JSON columns
- Easy to serialize/deserialize
- Queryable with PostgreSQL JSON operators

**Alternatives Considered**:
- Separate `recurrence_rules` table: Over-engineered for MVP
- String field (cron expression): Too rigid for simple patterns

## API Contracts

### Request Models

```typescript
// Create Task with Advanced Features
interface TaskCreateAdvanced {
  title: string;
  description?: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  tags: string[];
  due_date?: string;  // ISO 8601 datetime (UTC)
  reminder_offset?: number;  // Minutes before due_date (null = at due time)
  recurrence?: {
    frequency: 'daily' | 'weekly' | 'monthly';
    interval?: number;  // Default: 1
    count?: number;  // Max occurrences
    end_date?: string;  // ISO 8601 date
  };
}
```

### Response Models

```typescript
// Task Read with Advanced Features
interface TaskReadAdvanced {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  priority: string;
  tags: string[];
  due_date?: string;  // ISO 8601 datetime (UTC)
  reminder_offset?: number;
  reminder_sent: boolean;
  completed: boolean;
  recurrence?: RecurrenceRule;
  parent_task_id?: string;
  created_at: string;
  updated_at: string;
}
```

## Testing Strategy

### Unit Tests (Optional)

**Backend**:
- `RecurrenceService.calculate_next_occurrence()`: Test all frequencies
- `RecurrenceService.validate_recurrence_rule()`: Test validation logic
- `TaskCreate.validate_due_date()`: Test date validation

**Frontend**:
- `dateFormatters.formatRelativeTime()`: Test time formatting
- `recurrenceCalculator.calculateNext()`: Match backend logic

### Integration Tests (Optional)

**Backend**:
- Test POST /api/tasks with recurrence creates parent task
- Test POST /api/tasks/{id}/complete creates new instance
- Test GET /api/tasks?due_before filters correctly

**Frontend**:
- Test NotificationManager requests permission
- Test TaskForm submits with due date
- Test recurring task completion flow

### E2E Tests (Optional)

1. Create task with due date → verify displayed in list
2. Create task with due date in past → verify overdue badge
3. Create recurring task → complete → verify new task created
4. Grant notification permission → wait for notification

## Dependencies

### Prerequisites

1. **007-intermediate-todo-features**: Must be complete (provides priority, tags, filters, sort, search)
2. **shadcn/ui components**: `calendar.tsx` already exists
3. **Browser Notifications API**: Web Notifications API supported (Chrome 22+, Firefox 22+, Safari 7+)

### Installation

**No new packages required** - all dependencies already installed:
- `date-fns: ^4.1.0` ✅
- `react-day-picker: ^9.13.0` ✅
- Sonner for toasts ✅

## Security Considerations

1. **Notification Permission**: Must be user-initiated (not on page load)
2. **Due Date Validation**: Prevent dates >10 years in past (already implemented)
3. **Recursion Limit**: Maximum 100 instances per recurring task
4. **User Data Isolation**: All queries scoped to user_id
5. **XSS Prevention**: React auto-escapes, validate inputs with Pydantic/Zod

## Performance Optimization

1. **Database Indexing**: `due_date` already indexed
2. **Notification Polling**: Check only tasks with due dates in next 24 hours
3. **Recurring Task Creation**: Async, non-blocking
4. **Date Formatting**: Memoize formatted dates in list components

## Accessibility

1. **Due Date Input**: ARIA labels, keyboard navigation
2. **Notification Permission**: Clear explanation of why requested
3. **Overdue Indication**: Color + text (not just color)
4. **Recurrence Picker**: Screen reader friendly

## Migration Plan

### Database Migration

```sql
-- Add new columns to tasks table
ALTER TABLE tasks
  ADD COLUMN reminder_offset INTEGER,
  ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE,
  ADD COLUMN recurrence JSONB,
  ADD COLUMN parent_task_id UUID REFERENCES tasks(id);

-- Create index on parent_task_id for faster queries
CREATE INDEX idx_tasks_parent_task_id ON tasks(parent_task_id);

-- Create index on reminder_sent for notification queries
CREATE INDEX idx_tasks_reminder_sent ON tasks(reminder_sent) WHERE reminder_sent = FALSE;
```

### Data Migration

No data migration needed - new fields are optional.

## Rollback Plan

If issues arise:
1. Remove notification polling (delete NotificationManager)
2. Hide recurrence UI (disable RecurrencePicker)
3. Keep due date functionality (stable)

## Open Questions

**None** - all clarifications resolved in research phase.

## Next Steps

1. ✅ Create this plan (plan.md)
2. ⏳ Generate research.md with detailed technology analysis
3. ⏳ Generate data-model.md with entity definitions
4. ⏳ Generate contracts/ with API specifications
5. ⏳ Generate quickstart.md with integration guide
6. ⏳ Run `/sp.tasks` to generate task breakdown
7. ⏳ Implement following tasks.md

---

**Plan Version**: 1.0.0
**Last Updated**: 2026-02-04
**Status**: Ready for Phase 0 Research
