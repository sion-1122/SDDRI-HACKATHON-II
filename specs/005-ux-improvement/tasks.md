# Tasks: UI/UX Improvements

**Input**: Design documents from `/specs/005-ux-improvement/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-contracts.md

**Tests**: This feature does NOT include test tasks. Testing is optional and not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story (P1 → P2 → P3) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

## Path Conventions

All paths are relative to `frontend/` directory. This is a frontend-only enhancement feature with no backend changes required.

---

## Phase 1: Setup (Dependencies & Configuration)

**Purpose**: Install new dependencies and configure shadcn/ui

- [ ] T001 Install nuqs package in frontend/package.json
- [ ] T002 Initialize shadcn/ui in frontend/ with `npx shadcn@latest init`
- [ ] T003 Add shadcn button component in frontend/src/components/ui/button.tsx
- [ ] T004 Add shadcn input component in frontend/src/components/ui/input.tsx
- [ ] T005 Add shadcn textarea component in frontend/src/components/ui/textarea.tsx
- [ ] T006 Add shadcn dialog component in frontend/src/components/ui/dialog.tsx
- [ ] T007 Add shadcn sheet component in frontend/src/components/ui/sheet.tsx
- [ ] T008 Add shadcn skeleton component in frontend/src/components/ui/skeleton.tsx
- [ ] T009 Add shadcn badge component in frontend/src/components/ui/badge.tsx

**Checkpoint**: All dependencies installed and shadcn/ui components ready

---

## Phase 2: Foundational (Type Definitions & Utilities)

**Purpose**: Enhanced TypeScript types and utility functions that all user stories depend on

- [ ] T010 Update Task type in frontend/src/types/task.ts to include due_date, priority, user_id fields
- [ ] T011 Add urgency type to frontend/src/types/task.ts (overdue, due-today, due-soon, due-later, none)
- [ ] T012 Update FilterState type in frontend/src/types/filters.ts to include priority and dueDate filters
- [ ] T013 Add TaskPriority type alias in frontend/src/types/filters.ts
- [ ] T014 Add DueDateFilter type alias in frontend/src/types/filters.ts
- [ ] T015 Add filterParsers export in frontend/src/types/filters.ts with nuqs parsers
- [ ] T016 Add formatRelativeDate utility in frontend/src/lib/utils.ts for date formatting
- [ ] T017 Add getTaskUrgency utility in frontend/src/lib/utils.ts for urgency calculation
- [ ] T018 Add Notion-themed CSS variables to frontend/src/app/globals.css

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Fast Dashboard Loading (Priority: P1) 🎯 MVP

**Goal**: Dashboard displays within 1 second using server-side data fetching and skeleton loading states

**Independent Test**: Navigate to /dashboard and measure initial page load time. Should be under 1 second for 100 tasks. Loading should show skeleton screens, not generic spinners.

### Implementation for US1

- [ ] T019 [P] [US1] Create TaskSkeleton component in frontend/src/components/tasks/TaskSkeleton.tsx
- [ ] T020 [P] [US1] Create DashboardSkeleton component in frontend/src/app/dashboard/loading.tsx
- [ ] T021 [US1] Convert dashboard/page.tsx to Server Component with server-side data fetching
- [ ] T022 [US1] Create TaskListClient wrapper component in frontend/src/components/tasks/TaskList.tsx for interactivity
- [ ] T023 [US1] Update dashboard to pass initialTasks from server to TaskListClient
- [ ] T024 [US1] Add Suspense boundary in dashboard/page.tsx with DashboardSkeleton as fallback
- [ ] T025 [US1] Test dashboard loads under 1 second with skeleton states

**Checkpoint**: Dashboard loads quickly with skeleton screens. US1 independently functional.

---

## Phase 4: User Story 2 - Complete Task Information Display (Priority: P1)

**Goal**: Display due dates and priority badges with urgency-based visual styling

**Independent Test**: View task list and verify due dates and priority badges are visible. Tasks should be color-coded by urgency (overdue=red, today=yellow, soon=green).

### Implementation for US2

- [ ] T026 [P] [US2] Create PriorityBadge component in frontend/src/components/tasks/PriorityBadge.tsx
- [ ] T027 [P] [US2] Create DueDateBadge component in frontend/src/components/tasks/DueDateBadge.tsx
- [ ] T028 [US2] Update TaskItem component in frontend/src/components/tasks/TaskItem.tsx to display due_date
- [ ] T029 [US2] Update TaskItem component in frontend/src/components/tasks/TaskItem.tsx to display priority badge
- [ ] T030 [US2] Add urgency-based styling to TaskItem in frontend/src/components/tasks/TaskItem.tsx
- [ ] T031 [US2] Handle tasks without due dates gracefully (no "missing" indicators)
- [ ] T032 [US2] Test task data display with various due dates and priorities

**Checkpoint**: Tasks show due dates, priority badges, and urgency styling. US2 independently functional.

---

## Phase 5: User Story 3 - Working Task Filtering (Priority: P1)

**Goal**: Fix broken filters using nuqs with type-safe, URL-based state management

**Independent Test**: Select different filter combinations. URL should update. Only tasks matching ALL criteria (AND logic) should display. Clear filters restores all tasks.

### Implementation for US3

- [ ] T033 [P] [US3] Create nuqs filter parsers in frontend/src/lib/filters.ts
- [ ] T034 [US3] Rewrite FilterBar component in frontend/src/components/tasks/FilterBar.tsx with nuqs
- [ ] T035 [US3] Add priority filter dropdown to FilterBar in frontend/src/components/tasks/FilterBar.tsx
- [ ] T036 [US3] Add due date range filter dropdown to FilterBar in frontend/src/components/tasks/FilterBar.tsx
- [ ] T037 [US3] Implement filter AND logic in TaskList or use backend API filter params
- [ ] T038 [US3] Add "no results" state in TaskList in frontend/src/components/tasks/TaskList.tsx
- [ ] T039 [US3] Test filter combinations work correctly with AND logic

**Checkpoint**: Filters work with URL sync, multiple filters, AND logic, and no-results state. US3 independently functional.

---

## Phase 6: User Story 4 - Task Search (Priority: P1)

**Goal**: Real-time search in title and description with debouncing

**Independent Test**: Type in search field. Results should update after 300ms debounce. Search matches title OR description. Clear search restores all tasks. No results shows message.

### Implementation for US4

- [ ] T040 [P] [US4] Add search input to FilterBar in frontend/src/components/tasks/FilterBar.tsx
- [ ] T041 [US4] Implement debounced search with nuqs in frontend/src/components/tasks/FilterBar.tsx
- [ ] T042 [US4] Connect search query to task API in frontend/src/lib/task-api.ts or TaskList
- [ ] T043 [US4] Implement search in title OR description (case-insensitive)
- [ ] T044 [US4] Show "no results found" message when search has no matches
- [ ] T045 [US4] Test search updates in real-time with proper debouncing

**Checkpoint**: Search works with debouncing, searches title+description, shows no-results state. US4 independently functional.

---

## Phase 7: User Story 5 - Optimistic UI Updates (Priority: P2)

**Goal**: Actions update UI immediately before server confirmation with rollback on error

**Independent Test**: Create/toggle/delete a task. UI should update instantly. If API fails, UI should revert with error toast. Perceived wait time should feel instant.

### Implementation for US5

- [ ] T046 [P] [US5] Create useOptimisticMutation hook in frontend/src/lib/hooks.ts
- [ ] T047 [US5] Update taskApi.createTask in frontend/src/lib/task-api.ts with optimistic wrapper
- [ ] T048 [US5] Update TaskForm in frontend/src/components/tasks/TaskForm.tsx with optimistic create
- [ ] T049 [US5] Update TaskItem toggle in frontend/src/components/tasks/TaskItem.tsx with optimistic update
- [ ] T050 [US5] Update TaskItem delete in frontend/src/components/tasks/TaskItem.tsx with optimistic delete
- [ ] T051 [US5] Implement rollback logic for failed optimistic updates
- [ ] T052 [US5] Add error toast when optimistic update fails
- [ ] T053 [US5] Test optimistic updates with rollback scenarios

**Checkpoint**: All CRUD operations update optimistically with error rollback. US5 independently functional.

---

## Phase 8: User Story 6 - Integrated Chatbot (Priority: P2)

**Goal**: Floating chatbot dialog in bottom-right corner that preserves state across navigation

**Independent Test**: Click chat button in bottom-right. Sheet opens from right. Navigate dashboard pages. Chat state preserved. Close and reopen - state maintained.

### Implementation for US6

- [ ] T054 [P] [US6] Create ChatProvider context in frontend/src/components/chatbot/ChatProvider.tsx
- [ ] T055 [P] [US6] Create FloatingChat component in frontend/src/components/chatbot/FloatingChat.tsx
- [ ] T056 [US6] Integrate shadcn Sheet for chat panel in frontend/src/components/chatbot/FloatingChat.tsx
- [ ] T057 [US6] Position floating button bottom-right in frontend/src/components/chatbot/FloatingChat.tsx
- [ ] T058 [US6] Wrap root layout with ChatProvider in frontend/src/app/layout.tsx
- [ ] T059 [US6] Reuse existing ChatInterface in FloatingChat sheet content
- [ ] T060 [US6] Test chat state preservation across navigation

**Checkpoint**: Chat accessible via floating button, state preserved, no page navigation needed. US6 independently functional.

---

## Phase 9: User Story 7 - Toast Notifications (Priority: P2)

**Goal**: Success/error toasts for all actions with appropriate colors and context

**Independent Test**: Perform create/update/delete actions. Success toasts appear green. Errors appear red with helpful message. Multiple toasts stack. Dismissible by clicking X.

### Implementation for US7

- [ ] T061 [P] [US7] Add success toast to TaskForm submit in frontend/src/components/tasks/TaskForm.tsx
- [ ] T062 [P] [US7] Add error toast to TaskForm submit in frontend/src/components/tasks/TaskForm.tsx
- [ ] T063 [P] [US7] Add success toast to TaskItem toggle in frontend/src/components/tasks/TaskItem.tsx
- [ ] T064 [P] [US7] Add success toast to TaskItem delete in frontend/src/components/tasks/TaskItem.tsx
- [ ] T065 [P] [US7] Add error toast to failed API calls across components
- [ ] T066 [US7] Add promise toasts for async operations in frontend/src/lib/task-api.ts
- [ ] T067 [US7] Verify toast color coding (success=green, error=red, warning=yellow)
- [ ] T068 [US7] Test toast stacking and dismissibility

**Checkpoint**: All actions show appropriate toasts with colors and context. US7 independently functional.

---

## Phase 10: User Story 8 - Notion-Inspired Minimalistic Theme (Priority: P3)

**Goal**: Clean, minimalistic design with neutral tones, generous whitespace, Inter typography

**Independent Test**: View dashboard. Design uses neutral grays, blue accents. Generous whitespace between elements. Clean typography. Consistent across pages.

### Implementation for US8

- [ ] T069 [P] [US8] Add Notion color CSS variables to frontend/src/app/globals.css
- [ ] T070 [P] [US8] Add Inter font import to frontend/src/app/layout.tsx
- [ ] T071 [US8] Update typography scale in frontend/tailwind.config.ts
- [ ] T072 [US8] Refactor dashboard layout with generous whitespace in frontend/src/app/dashboard/page.tsx
- [ ] T073 [US8] Update TaskItem styling for minimalistic look in frontend/src/components/tasks/TaskItem.tsx
- [ ] T074 [US8] Update FilterBar styling for minimalistic look in frontend/src/components/tasks/FilterBar.tsx
- [ ] T075 [US8] Ensure consistent design across all pages
- [ ] T076 [US8] Test Notion-inspired theme consistency

**Checkpoint**: Design is minimalistic with neutral tones, whitespace, clean typography. US8 independently functional.

---

## Phase 11: User Story 9 - Engaging Loading Animations (Priority: P3)

**Goal**: Replace generic spinners with skeleton screens and meaningful animations

**Independent Test**: Trigger loading states. See skeleton screens (not spinners). Chatbot shows typing indicator. Smooth transitions when content loads.

### Implementation for US9

- [ ] T077 [P] [US9] Replace generic LoadingSpinner with Skeleton in frontend/src/components/ui/LoadingSpinner.tsx
- [ ] T078 [P] [US9] Add skeleton loading to TaskList in frontend/src/components/tasks/TaskList.tsx
- [ ] T079 [P] [US9] Add skeleton loading to FilterBar in frontend/src/components/tasks/FilterBar.tsx
- [ ] T080 [US9] Create TypingIndicator component for chatbot in frontend/src/components/chatbot/TypingIndicator.tsx
- [ ] T081 [US9] Add smooth fade-in transitions to TaskList in frontend/src/components/tasks/TaskList.tsx
- [ ] T082 [US9] Test all loading states use engaging animations

**Checkpoint**: All loading states use skeletons or meaningful animations. US9 independently functional.

---

## Phase 12: User Story 10 - Enhanced Chatbot Experience (Priority: P3)

**Goal**: Better chatbot UX with progress indicators, streaming responses, friendly errors

**Independent Test**: Send chat message. See progress indicators. Response streams in real-time. Errors show friendly messages. Existing components from feature 004 enhanced.

### Implementation for US10

- [ ] T083 [P] [US10] Enhance ProgressBar component in frontend/src/components/chat/ProgressBar.tsx
- [ ] T084 [P] [US10] Enhance ToolStatus component in frontend/src/components/chat/ToolStatus.tsx
- [ ] T085 [US10] Enhance ConnectionStatus component in frontend/src/components/chat/ConnectionStatus.tsx
- [ ] T086 [US10] Add streaming response handling in frontend/src/components/chat/ChatInterface.tsx
- [ ] T087 [US10] Add friendly error messages for chatbot failures
- [ ] T088 [US10] Test enhanced chatbot experience

**Checkpoint**: Chatbot has progress indicators, streaming, friendly errors. US10 independently functional.

---

## Phase 13: User Story 11 - Value-Focused Landing Page (Priority: P3)

**Goal**: Marketing landing page with value proposition, features, and CTA. Logged-in users redirect to dashboard.

**Independent Test**: Visit root URL while logged out. See landing page with value prop and features. Visit while logged in. Redirect to dashboard automatically.

### Implementation for US11

- [ ] T089 [P] [US11] Create LandingPage component in frontend/src/components/landing/LandingPage.tsx
- [ ] T090 [US11] Add hero section with value proposition in LandingPage component
- [ ] T091 [US11] Add features section with 3-4 key features in LandingPage component
- [ ] T092 [US11] Add call-to-action buttons (Sign Up/Login) in LandingPage component
- [ ] T093 [US11] Add footer to LandingPage component
- [ ] T094 [US11] Update root page.tsx to check auth and redirect in frontend/src/app/page.tsx
- [ ] T095 [US11] Style landing page with Notion-inspired design
- [ ] T096 [US11] Test landing page and auth redirect logic

**Checkpoint**: Landing page displays value prop, features, CTA. Auth users bypass to dashboard. US11 independently functional.

---

## Phase 14: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, cleanup, and validation

- [ ] T097 [P] Add empty state component in frontend/src/components/tasks/EmptyState.tsx
- [ ] T098 [P] Add empty state to TaskList when no tasks exist
- [ ] T099 [P] Verify all Sonner toasts are dismissible and properly colored
- [ ] T100 [P] Test responsive design on mobile viewport
- [ ] T101 [P] Test keyboard navigation throughout app
- [ ] T102 Run accessibility audit (aria labels, focus management)
- [ ] T103 Test all user stories work together
- [ ] T104 Run quickstart.md validation checklist
- [ ] T105 Final performance audit (dashboard <1s, search <500ms)

**Checkpoint**: Feature complete, polished, and validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (shadcn components needed) - BLOCKS all user stories
- **User Stories (Phases 3-13)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 14)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1-US4 (P1 - Critical Path)**: Should be completed sequentially in order
  - US1 (Dashboard loading) → US2 (Data display) → US3 (Filters) → US4 (Search)
  - These build on each other for the core task management experience
- **US5-US7 (P2 - High Value)**: Can be done in parallel after P1 stories complete
  - US5 (Optimistic updates) enhances US1-US4
  - US6 (Chatbot) is independent
  - US7 (Toasts) enhances all stories
- **US8-US11 (P3 - Polish)**: Can be done in parallel after P1-P2 complete
  - US8 (Theme) is visual overlay
  - US9 (Loaders) replaces generic loading
  - US10 (Chatbot UX) enhances US6
  - US11 (Landing page) is independent

### Parallel Opportunities

**Within Setup (Phase 1)**:
- T003-T009 can run in parallel (all shadcn components)

**Within Foundational (Phase 2)**:
- T010-T018 can mostly run in parallel (different files)

**Within User Stories**:
- US2: T026-T027 can run in parallel
- US7: T061-T066 can run in parallel
- US8: T069-T073 can run in parallel
- US9: T077-T079 can run in parallel
- US10: T083-T084 can run in parallel
- US11: T089-T090 can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch both badge components together:
T026: "Create PriorityBadge component"
T027: "Create DueDateBadge component"
```

---

## Implementation Strategy

### MVP First (P1 User Stories Only)

1. Complete Phase 1: Setup (shadcn, nuqs)
2. Complete Phase 2: Foundational (types, utilities)
3. Complete Phase 3: US1 (Fast Dashboard Loading)
4. Complete Phase 4: US2 (Task Data Display)
5. Complete Phase 5: US3 (Working Filters)
6. Complete Phase 6: US4 (Task Search)
7. **STOP and VALIDATE**: Core task management works
8. Demo MVP (P1 stories deliver functional task manager)

### Incremental Delivery

1. **MVP (P1)**: Fast loading, complete data display, filters, search → Functional task manager
2. **+ P2**: Add optimistic updates, integrated chatbot, enhanced toasts → Enhanced UX
3. **+ P3**: Add Notion theme, engaging loaders, landing page, chatbot UX → Polish

### Parallel Team Strategy

With multiple developers after Foundational phase:

1. **Developer A**: P1 stories (US1-US4) - Core task management
2. **Developer B**: P2 stories (US5-US7) - Enhanced interactions
3. **Developer C**: P3 stories (US8-US11) - Visual polish

---

## Summary

- **Total Tasks**: 105
- **Setup**: 9 tasks
- **Foundational**: 9 tasks
- **P1 User Stories**: 29 tasks (US1-US4)
- **P2 User Stories**: 22 tasks (US5-US7)
- **P3 User Stories**: 27 tasks (US8-US11)
- **Polish**: 9 tasks

**Suggested MVP Scope**: Phases 1-6 (Setup, Foundational, US1-US4) = 51 tasks for functional task manager with fast loading, complete data display, filters, and search.
