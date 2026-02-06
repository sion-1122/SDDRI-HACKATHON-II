# Tasks: Advanced Todo Features

**Feature**: 008-advanced-features | **Branch**: `008-advanced-features` | **Date**: 2026-02-04
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Data Model**: [data-model.md](./data-model.md)
**Status**: Draft | **Total Tasks**: 67

---

## Executive Summary

This implementation adds time-based task management features to the Todo List application. Tasks are organized by user story to enable independent implementation and testing. Each user story phase is self-contained with its own models, services, API endpoints, and UI components.

**User Stories (Priority Order)**:
1. **US1 - Due Dates with DateTime Picker** (P1, MVP): Set and display due dates, overdue detection
2. **US2 - Browser Notifications for Reminders** (P1): Permission requests, notification scheduling
3. **US3 - Recurring Tasks** (P2): Daily/weekly/monthly recurrence, automatic next instance creation
4. **US4 - Cron-Based Scheduling** (P3): Custom cron expressions, advanced recurrence patterns

**Implementation Strategy**: Incremental delivery - each US1 and US2 form the MVP, US3 adds recurrence, US4 adds power-user features.

---

## Phase 1: Setup & Database Migration

**Goal**: Prepare database schema and project structure for all advanced features.

**Independent Test Criteria**:
- Database migration runs successfully
- New columns are added to tasks table
- Indexes are created for performance
- Validation function is created

**Tasks**:

- [ ] T001 Run database migration to add advanced features columns in backend/migrations/008_add_advanced_features.sql
- [ ] T002 [P] Create RecurrenceRule Pydantic model in backend/models/recurrence.py
- [ ] T003 Extend Task SQLModel with reminder_offset field in backend/models/task.py
- [ ] T004 [P] Extend Task SQLModel with reminder_sent field in backend/models/task.py
- [ ] T005 [P] Extend Task SQLModel with recurrence JSONB field in backend/models/task.py
- [ ] T006 [P] Extend Task SQLModel with parent_task_id field in backend/models/task.py
- [ ] T007 Extend TaskCreate Pydantic model with new fields in backend/models/task.py
- [ ] T008 Extend TaskUpdate Pydantic model with new fields in backend/models/task.py
- [ ] T009 Extend TaskRead Pydantic model with new fields in backend/models/task.py
- [ ] T010 [P] Add RecurrenceRule interface to frontend in frontend/src/types/recurrence.ts
- [ ] T011 Extend Task interface with advanced fields in frontend/src/types/task.ts
- [ ] T012 Extend TaskCreate interface with advanced fields in frontend/src/types/task.ts
- [ ] T013 [P] Extend TaskUpdate interface with advanced fields in frontend/src/types/task.ts
- [ ] T014 [P] Extend TaskListFilters interface with due date fields in frontend/src/types/task.ts

**Dependencies**: None (setup phase)

**Parallel Opportunities**: T002-T006 can run in parallel (different model files), T010-T014 can run in parallel (different type files)

---

## Phase 2: Foundational Services

**Goal**: Create shared services for date formatting and recurrence calculation used by all user stories.

**Independent Test Criteria**:
- RecurrenceService correctly calculates next occurrence for daily/weekly/monthly
- Date formatters display relative time correctly
- Overdue detection works across timezones

**Tasks**:

- [ ] T015 Create RecurrenceService class in backend/services/recurrence_service.py
- [ ] T016 [P] Implement calculate_next_occurrence for daily frequency in backend/services/recurrence_service.py
- [ ] T017 [P] Implement calculate_next_occurrence for weekly frequency in backend/services/recurrence_service.py
- [ ] T018 [P] Implement calculate_next_occurrence for monthly frequency in backend/services/recurrence_service.py
- [ ] T019 Implement validate_recurrence_rule method in backend/services/recurrence_service.py
- [ ] T020 Implement check_recurrence_limit method (100 instance max) in backend/services/recurrence_service.py
- [ ] T021 Create dateFormatters utility in frontend/src/lib/utils/dateFormatters.ts
- [ ] T022 [P] Implement formatRelativeTime function in frontend/src/lib/utils/dateFormatters.ts
- [ ] T023 [P] Implement formatDueDate function (with overdue check) in frontend/src/lib/utils/dateFormatters.ts
- [ ] T024 Create recurrenceCalculator utility in frontend/src/lib/utils/recurrenceCalculator.ts
- [ ] T025 [P] Implement calculateNext function in frontend/src/lib/utils/recurrenceCalculator.ts
- [ ] T026 [P] Implement isValidRecurrenceRule function in frontend/src/lib/utils/recurrenceCalculator.ts

**Dependencies**: Phase 1 must be complete

**Parallel Opportunities**: T016-T018 (different frequencies), T022-T023 (different formatters), T025-T026 (different calculator functions)

---

## Phase 3: User Story 1 - Due Dates with DateTime Picker (P1, MVP)

**User Story**: As a user, I want to set a specific due date and time for my tasks so that I can track time-sensitive deadlines.

**Acceptance Scenarios**:
1. Given I am creating or editing a task, When I click the due date field, Then a datetime picker appears
2. Given I select a date and time, When I save the task, Then the due date is stored and displayed
3. Given a task has a due date, When I view the task list, Then I see the due date formatted clearly
4. Given a task is overdue, When I view the task list, Then the task is visually highlighted

**Independent Test Criteria**:
- User can select date and time via picker
- Due date is stored in UTC and displayed in local timezone
- Overdue tasks show red badge with "Overdue" text
- Tasks can be filtered by due date range

**Tasks**:

- [ ] T027 [US1] Extend POST /api/tasks to accept due_date in backend/api/tasks.py
- [ ] T028 [US1] Extend GET /api/tasks to support due_before/due_after filters in backend/api/tasks.py
- [ ] T029 [US1] Extend PUT /api/tasks/{id} to update due_date in backend/api/tasks.py
- [ ] T030 [US1] Create DatePicker component using Calendar in frontend/src/components/tasks/DatePicker.tsx
- [ ] T031 [US1] Create TimePicker component using native input in frontend/src/components/tasks/TimePicker.tsx
- [ ] T032 [US1] Create DueDateField component combining DatePicker and TimePicker in frontend/src/components/tasks/DueDateField.tsx
- [ ] T033 [US1] Extend TaskForm to include DueDateField component in frontend/src/components/tasks/TaskForm.tsx
- [ ] T034 [US1] Extend TaskForm to handle due_date state in frontend/src/components/tasks/TaskForm.tsx
- [ ] T035 [US1] Extend TaskForm to submit due_date to API in frontend/src/components/tasks/TaskForm.tsx
- [ ] T036 [US1] Extend TaskForm to edit existing due_date in frontend/src/components/tasks/TaskForm.tsx
- [ ] T037 [US1] Extend TaskListItem to display formatted due date in frontend/src/components/tasks/TaskListItem.tsx
- [ ] T038 [US1] Extend TaskListItem to show relative time in frontend/src/components/tasks/TaskListItem.tsx
- [ ] T039 [US1] Extend TaskListItem to display overdue badge in frontend/src/components/tasks/TaskListItem.tsx
- [ ] T040 [US1] Create isOverdue utility function in frontend/src/lib/utils/taskHelpers.ts
- [ ] T041 [US1] Extend task API client to send due_date in frontend/src/lib/api/client.ts
- [ ] T042 [US1] Extend task API client to parse due_date from response in frontend/src/lib/api/client.ts

**Dependencies**: Phase 1, Phase 2 must be complete

**Parallel Opportunities**: T027-T029 (different endpoints), T030-T031 (different pickers), T037-T039 (different display aspects)

---

## Phase 4: User Story 2 - Browser Notifications for Reminders (P1)

**User Story**: As a user, I want to receive browser notifications when a task is due or overdue so that I don't miss important deadlines.

**Acceptance Scenarios**:
1. Given I have granted notification permission, When a task becomes due, Then I receive a browser notification
2. Given I haven't granted permission, When the app loads, Then I'm prompted to enable notifications
3. Given I receive a notification, When I click it, Then the app opens to that task
4. Given multiple tasks are due, When reminders fire, Then I receive grouped notifications

**Independent Test Criteria**:
- Notification permission is requested on first load
- Notifications appear for tasks due within reminder offset
- Multiple due tasks are grouped into single notification
- Clicking notification opens the relevant task

**Tasks**:

- [ ] T043 [US2] Extend POST /api/tasks to accept reminder_offset in backend/api/tasks.py
- [ ] T044 [US2] Extend PUT /api/tasks/{id} to update reminder_offset in backend/api/tasks.py
- [ ] T045 [US2] Create PATCH /api/tasks/{id}/reminder endpoint in backend/api/tasks.py
- [ ] T046 [US2] Create ReminderOffsetSelector component in frontend/src/components/tasks/ReminderOffsetSelector.tsx
- [ ] T047 [US2] Create NotificationPermissionPrompt component in frontend/src/components/tasks/NotificationPermissionPrompt.tsx
- [ ] T048 [US2] Extend TaskForm to include ReminderOffsetSelector in frontend/src/components/tasks/TaskForm.tsx
- [ ] T049 [US2] Create NotificationManager component in frontend/src/components/tasks/NotificationManager.tsx
- [ ] T050 [US2] Implement NotificationManager permission request in frontend/src/components/tasks/NotificationManager.tsx
- [ ] T051 [US2] Implement NotificationManager polling interval (1 minute) in frontend/src/components/tasks/NotificationManager.tsx
- [ ] T052 [US2] Implement NotificationManager checkAndSendNotifications function in frontend/src/components/tasks/NotificationManager.tsx
- [ ] T053 [US2] Implement NotificationManager showNotification function in frontend/src/components/tasks/NotificationManager.tsx
- [ ] T054 [US2] Implement NotificationManager groupNotifications function in frontend/src/components/tasks/NotificationManager.tsx
- [ ] T055 [US2] Implement NotificationManager handleNotificationClick function in frontend/src/components/tasks/NotificationManager.tsx
- [ ] T056 [US2] Add NotificationManager to dashboard layout in frontend/src/app/dashboard/layout.tsx
- [ ] T057 [US2] Extend task API client to send reminder_offset in frontend/src/lib/api/client.ts
- [ ] T058 [US2] Extend task API client to update reminder_sent status in frontend/src/lib/api/client.ts
- [ ] T059 [US2] Create useNotifications hook in frontend/src/lib/hooks/useNotifications.ts

**Dependencies**: Phase 1, Phase 2, Phase 3 must be complete

**Parallel Opportunities**: T043-T045 (different endpoints), T050-T055 (different NotificationManager functions)

---

## Phase 5: User Story 3 - Recurring Tasks (P2)

**User Story**: As a user, I want to create tasks that repeat automatically so that I don't have to manually recreate recurring tasks.

**Acceptance Scenarios**:
1. Given I am creating a task, When I enable recurring, Then I can select daily/weekly/monthly
2. Given I complete a recurring task, When it's marked done, Then a new task is automatically created
3. Given a recurring task is created, When I view the new task, Then the due date is advanced to the next period
4. Given I edit a recurring task, When I save, Then future tasks follow the new pattern

**Independent Test Criteria**:
- User can set recurrence frequency (daily/weekly/monthly)
- Completing recurring task creates next instance automatically
- Next instance has advanced due date based on recurrence pattern
- Recurrence stops when count or end_date limit reached

**Tasks**:

- [ ] T060 [US3] Extend POST /api/tasks to accept recurrence in backend/api/tasks.py
- [ ] T061 [US3] Extend PUT /api/tasks/{id} to update recurrence in backend/api/tasks.py
- [ ] T062 [US3] Extend POST /api/tasks/{id}/complete to create next instance in backend/api/tasks.py
- [ ] T063 [US3] Add recurrence limit checking in complete endpoint in backend/api/tasks.py
- [ ] T064 [US3] Handle count limit in recurrence creation in backend/api/tasks.py
- [ ] T065 [US3] Handle end_date limit in recurrence creation in backend/api/tasks.py
- [ ] T066 [US3] Create RecurrencePicker component in frontend/src/components/tasks/RecurrencePicker.tsx
- [ ] T067 [US3] Implement RecurrencePicker frequency selector in frontend/src/components/tasks/RecurrencePicker.tsx
- [ ] T068 [US3] Implement RecurrencePicker interval input in frontend/src/components/tasks/RecurrencePicker.tsx
- [ ] T069 [US3] Implement RecurrencePicker end condition (count/end_date) in frontend/src/components/tasks/RecurrencePicker.tsx
- [ ] T070 [US3] Extend TaskForm to include RecurrencePicker in frontend/src/components/tasks/TaskForm.tsx
- [ ] T071 [US3] Extend TaskForm to handle recurrence state in frontend/src/components/tasks/TaskForm.tsx
- [ ] T072 [US3] Extend TaskForm to submit recurrence to API in frontend/src/components/tasks/TaskForm.tsx
- [ ] T073 [US3] Extend TaskListItem to show recurring indicator in frontend/src/components/tasks/TaskListItem.tsx
- [ ] T074 [US3] Extend complete task handler to process next_instance in frontend/src/lib/api/client.ts
- [ ] T075 [US3] Extend complete task handler to refresh task list after recurrence in frontend/src/lib/api/client.ts

**Dependencies**: Phase 1, Phase 2, Phase 3, Phase 4 must be complete

**Parallel Opportunities**: T060-T061 (different endpoints), T067-T069 (different RecurrencePicker parts)

---

## Phase 6: User Story 4 - Cron-Based Scheduling (P3)

**User Story**: As a user, I want advanced recurring patterns (cron expressions) for complex scheduling needs.

**Acceptance Scenarios**:
1. Given I select custom recurring, When I enter a cron expression, Then it validates the format
2. Given a cron task exists, When the schedule triggers, Then a new task is created

**Independent Test Criteria**:
- Cron expressions are validated for format (5 fields: minute hour day month weekday)
- Cron validation provides clear error messages
- RecurrenceService can calculate next occurrence from cron expression

**Tasks**:

- [ ] T076 [US4] Implement cron expression validator in backend/services/recurrence_service.py
- [ ] T077 [US4] Implement calculate_next_occurrence for cron in backend/services/recurrence_service.py
- [ ] T078 [US4] Add cron_frequency to RecurrenceRule model in backend/models/recurrence.py
- [ ] T079 [US4] Extend RecurrencePicker with cron input mode in frontend/src/components/tasks/RecurrencePicker.tsx
- [ ] T080 [US4] Create CronExpressionInput component in frontend/src/components/tasks/CronExpressionInput.tsx
- [ ] T081 [US4] Create CronExpressionBuilder component with presets in frontend/src/components/tasks/CronExpressionBuilder.tsx
- [ ] T082 [US4] Implement cron validator in frontend/src/lib/utils/recurrenceCalculator.ts
- [ ] T083 [US4] Implement cron next occurrence calculator in frontend/src/lib/utils/recurrenceCalculator.ts

**Dependencies**: Phase 1, Phase 2, Phase 3, Phase 4, Phase 5 must be complete

**Parallel Opportunities**: T076-T077 (different functions), T079-T081 (different UI components)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Finalize implementation with edge cases, error handling, and UX improvements.

**Independent Test Criteria**:
- All edge cases handled (max recursion limit, timezone changes, permission denial)
- Error messages are clear and actionable
- Performance meets targets (notification <10s, recurrence <5s)
- Accessibility requirements met

**Tasks**:

- [ ] T084 Add error handling for recurrence limit exceeded in backend/api/tasks.py
- [ ] T085 Add error handling for invalid cron expressions in backend/api/tasks.py
- [ ] T086 Add error handling for denied notification permission in frontend/src/components/tasks/NotificationManager.tsx
- [ ] T087 Add loading states for recurrence calculation in frontend/src/components/tasks/RecurrencePicker.tsx
- [ ] T088 Add ARIA labels to DatePicker component in frontend/src/components/tasks/DatePicker.tsx
- [ ] T089 Add ARIA labels to TimePicker component in frontend/src/components/tasks/TimePicker.tsx
- [ ] T090 Add keyboard navigation to RecurrencePicker in frontend/src/components/tasks/RecurrencePicker.tsx
- [ ] T091 Add screen reader support for overdue badge in frontend/src/components/tasks/TaskListItem.tsx
- [ ] T092 Optimize date formatting with memoization in frontend/src/components/tasks/TaskListItem.tsx
- [ ] T093 Optimize notification polling (only check tasks due in 24h) in frontend/src/components/tasks/NotificationManager.tsx
- [ ] T094 Add toast notifications for recurrence errors in frontend/src/components/tasks/TaskForm.tsx
- [ ] T095 Add toast notifications for permission denied in frontend/src/components/tasks/NotificationPermissionPrompt.tsx
- [ ] T096 Test timezone handling for due dates in backend/tests/test_task_api.py
- [ ] T097 Test recurrence calculation edge cases in backend/tests/test_recurrence_service.py
- [ ] T098 Test notification permission flow in frontend/tests/notifications/notificationManager.test.ts
- [ ] T099 Test overdue detection across timezone changes in frontend/tests/tasks/taskHelpers.test.ts

**Dependencies**: All previous phases must be complete

**Parallel Opportunities**: T084-T086 (different error handling), T088-T091 (different accessibility), T096-T099 (different test files)

---

## Dependencies & Execution Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational Services)
    ↓
    ├─→ Phase 3 (US1: Due Dates) ──────┐
    │                                 │
    ├─→ Phase 4 (US2: Notifications)─┤
    │                                 ├─→ Phase 7 (Polish)
    │                                 │
    └─→ Phase 5 (US3: Recurrence) ────┘
            │
            └─→ Phase 6 (US4: Cron)
```

**Dependency Rules**:
- Phase 1 must complete before any other phase
- Phase 2 must complete before US1-US4 phases
- US1 and US2 can be developed in parallel (both P1 MVP)
- US3 requires US1 (due dates needed for recurrence)
- US4 requires US3 (extends recurrence)
- Phase 7 requires all user stories complete

---

## Parallel Execution Examples

### Phase 1 Parallel Execution
```bash
# Terminal 1
- T002: Create RecurrenceRule Pydantic model

# Terminal 2 (parallel)
- T003: Extend Task with reminder_offset
- T004: Extend Task with reminder_sent
- T005: Extend Task with recurrence

# Terminal 3 (parallel)
- T006: Extend Task with parent_task_id

# Terminal 4 (parallel)
- T010: Add RecurrenceRule interface (frontend)
- T011: Extend Task interface
```

### Phase 3 (US1) Parallel Execution
```bash
# Terminal 1
- T027: Extend POST /api/tasks for due_date

# Terminal 2 (parallel)
- T028: Extend GET /api/tasks filters
- T029: Extend PUT /api/tasks/{id}

# Terminal 3 (parallel)
- T030: Create DatePicker component
- T031: Create TimePicker component

# Terminal 4 (parallel)
- T040: Create isOverdue utility
- T041: Extend API client for due_date
```

### Phase 4 (US2) Parallel Execution
```bash
# Terminal 1
- T043: Extend POST for reminder_offset

# Terminal 2 (parallel)
- T044: Extend PUT for reminder_offset
- T045: Create PATCH reminder endpoint

# Terminal 3 (parallel)
- T046: Create ReminderOffsetSelector
- T047: Create PermissionPrompt

# Terminal 4 (parallel)
- T050: Implement permission request
- T051: Implement polling interval
- T052: Implement checkAndSendNotifications
- T053: Implement showNotification
- T054: Implement groupNotifications
- T055: Implement handleNotificationClick
```

---

## MVP Scope

**Minimum Viable Product** (US1 + US2):
- Due dates with datetime picker
- Overdue detection and display
- Browser notifications for reminders
- Due date range filtering

**Post-MVP** (US3):
- Recurring tasks (daily/weekly/monthly)
- Automatic next instance creation

**Advanced** (US4):
- Cron expression scheduling
- Custom recurrence patterns

---

## Success Criteria Validation

| Criterion | Test | Task(s) |
|-----------|------|---------|
| SC-001: Due date in 3 clicks | Manual | T030-T036 |
| SC-002: Notification in 10 seconds | Manual | T049-T055 |
| SC-003: Recurring task in 5 seconds | Manual | T062-T075 |
| SC-004: Timezone handling | Manual | T003-T004, T021-T023 |
| SC-005: Overdue visually distinct | Visual | T037-T040 |

---

## Format Validation

**All tasks follow checklist format**:
- ✅ Checkbox: `- [ ]` prefix
- ✅ Task ID: Sequential T001-T099
- ✅ [P] marker: Included for parallelizable tasks
- ✅ [Story] label: Included for user story phases (US1, US2, US3, US4)
- ✅ Description: Clear action with exact file path

**Total Tasks**: 99
- Phase 1 (Setup): 14 tasks
- Phase 2 (Foundational): 12 tasks
- Phase 3 (US1): 16 tasks
- Phase 4 (US2): 17 tasks
- Phase 5 (US3): 16 tasks
- Phase 6 (US4): 8 tasks
- Phase 7 (Polish): 16 tasks

**Parallel Opportunities**: 45 tasks marked with [P]

---

## Implementation Notes

1. **No New Dependencies**: All required packages already installed (date-fns, react-day-picker, shadcn/ui)
2. **Database Migration**: Run T001 first before any model changes
3. **Backend Services**: RecurrenceService is shared across US3 and US4
4. **Frontend Utilities**: dateFormatters and recurrenceCalculator are shared across all user stories
5. **Notification Polling**: 1-minute interval acceptable for MVP (spec allows 10-second target)
6. **Recursion Limit**: 100 instances max enforced at backend and frontend
7. **Timezone Handling**: All dates stored in UTC, displayed in user's local timezone
8. **Accessibility**: ARIA labels and keyboard navigation added in Polish phase

---

**Tasks Version**: 1.0.0
**Last Updated**: 2026-02-04
**Status**: Ready for Implementation
