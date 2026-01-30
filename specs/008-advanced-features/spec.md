# Feature Specification: Advanced Todo Features

**Feature Branch**: `008-advanced-features`
**Created**: 2026-01-30
**Status**: Draft
**Input**: Add time-based task management features including due dates with datetime picker, browser notifications for reminders, and recurring task support with automatic rescheduling.

## User Scenarios & Testing

### User Story 1 - Due Dates with DateTime Picker (Priority: P1) MVP

As a user, I want to set a specific due date and time for my tasks so that I can track time-sensitive deadlines.

**Why this priority**: Due dates are the foundation of time-based task management. Users need to specify when tasks are due.

**Acceptance Scenarios**:
1. Given I am creating or editing a task, When I click the due date field, Then a datetime picker appears
2. Given I select a date and time, When I save the task, Then the due date is stored and displayed
3. Given a task has a due date, When I view the task list, Then I see the due date formatted clearly
4. Given a task is overdue, When I view the task list, Then the task is visually highlighted

### User Story 2 - Browser Notifications for Reminders (Priority: P1)

As a user, I want to receive browser notifications when a task is due or overdue so that I don't miss important deadlines.

**Why this priority**: Reminders actively alert users, making the app more useful than passive task lists.

**Acceptance Scenarios**:
1. Given I have granted notification permission, When a task becomes due, Then I receive a browser notification
2. Given I haven't granted permission, When the app loads, Then I'm prompted to enable notifications
3. Given I receive a notification, When I click it, Then the app opens to that task
4. Given multiple tasks are due, When reminders fire, Then I receive grouped notifications

### User Story 3 - Recurring Tasks (Priority: P2)

As a user, I want to create tasks that repeat automatically so that I don't have to manually recreate recurring tasks.

**Why this priority**: Recurring tasks reduce friction for repeated activities.

**Acceptance Scenarios**:
1. Given I am creating a task, When I enable recurring, Then I can select daily/weekly/monthly
2. Given I complete a recurring task, When it's marked done, Then a new task is automatically created
3. Given a recurring task is created, When I view the new task, Then the due date is advanced to the next period
4. Given I edit a recurring task, When I save, Then future tasks follow the new pattern

### User Story 4 - Cron-Based Scheduling (Priority: P3)

As a user, I want advanced recurring patterns (cron expressions) for complex scheduling needs.

**Why this priority**: Power users need flexible scheduling beyond simple daily/weekly.

**Acceptance Scenarios**:
1. Given I select custom recurring, When I enter a cron expression, Then it validates the format
2. Given a cron task exists, When the schedule triggers, Then a new task is created

## Requirements

### Functional Requirements

**Due Dates (FR-001 to FR-005)**:
- FR-001: System MUST provide a datetime picker component for task creation/editing
- FR-002: System MUST store due dates in UTC timezone
- FR-003: System MUST display due dates in user's local timezone
- FR-004: System MUST visually highlight overdue tasks in the UI
- FR-005: System MUST support filtering tasks by due date range

**Reminders (FR-006 to FR-012)**:
- FR-006: System MUST request browser notification permission on first load
- FR-007: System MUST schedule notifications for tasks at their due time
- FR-008: System MUST support reminder offset (15min, 1hr, 1day before due)
- FR-009: System MUST handle notification permission denial gracefully
- FR-010: System MUST group multiple notifications when many tasks are due
- FR-011: System MUST open the relevant task when notification is clicked
- FR-012: System MUST provide notification preferences (enable/disable, sound)

**Recurring Tasks (FR-013 to FR-020)**:
- FR-013: System MUST support daily, weekly, and monthly recurrence
- FR-014: System MUST support custom recurrence with count (repeat N times)
- FR-015: System MUST support recurrence with end date
- FR-016: System MUST automatically create new task when recurring task is completed
- FR-017: System MUST advance due dates based on recurrence pattern
- FR-018: System MUST link recurring tasks to their parent task
- FR-019: System MUST allow editing recurrence pattern
- FR-020: System MUST support stopping recurrence

**Cron Scheduling (FR-021 to FR-025)**:
- FR-021: System MUST validate cron expressions
- FR-022: System MUST calculate next occurrence from cron
- FR-023: System MUST support standard cron syntax (minute hour day month weekday)
- FR-024: System MUST provide cron expression builder UI
- FR-025: System MUST support common presets (weekday mornings, month-end, etc)

### Data Model Extensions

**Task Model Additions**:
```typescript
interface Task {
  // ... existing fields
  due_date?: DateTime          // UTC timestamp
  reminder_offset?: number     // Minutes before due_date (0 = at due time)
  reminder_sent?: boolean      // Track if notification was sent
  recurrence?: RecurrenceRule
  parent_task_id?: string      // For recurring task instances
}

interface RecurrenceRule {
  frequency: 'daily' | 'weekly' | 'monthly' | 'custom'
  interval?: number            // Every N days/weeks/months
  cron_expression?: string     // For custom recurrence
  count?: number               // Maximum occurrences
  end_date?: DateTime          // Recurrence end date
}
```

## Success Criteria

- SC-001: User can set due date on task creation within 3 clicks
- SC-002: Notification appears within 10 seconds of task becoming due
- SC-003: Recurring task creates new instance within 5 seconds of completion
- SC-004: Due dates display correctly across timezone changes
- SC-005: All overdue tasks are visually distinct in the list

## Dependencies

1. **007-intermediate-todo-features** - Must be complete
2. **shadcn/ui components** - DatePicker, Select components available
3. **Browser Notification API** - Web Notifications API supported

## Out of Scope

1. Calendar view - List view only
2. Task dependencies - Tasks blocking other tasks
3. Time tracking - Time spent on tasks
4. Subtasks - Hierarchical task breakdown
5. Task templates - Pre-defined task patterns
