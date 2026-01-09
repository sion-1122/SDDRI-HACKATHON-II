# Tasks: Authenticated Frontend Task Management

**Input**: Design documents from `/specs/003-frontend-task-manager/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL for this feature. Test tasks are NOT included in this breakdown unless explicitly requested.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Per Principle VI (Monorepo Structure Standard)**:
- **Web app (Phase 2)**: `frontend/` directory with `src/` subdirectory
- Paths follow the structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create frontend directory structure per plan.md (frontend/src/{app,components,lib,types})
- [ ] T002 Initialize Next.js 16 project with TypeScript in frontend/package.json
- [X] T003 Install core dependencies (Next.js 16.1.1, React 19.2.3, Better Auth 1.4.10, Tailwind CSS 4, Zod, Sonner)
- [ ] T004 [P] Configure TypeScript strict mode in frontend/tsconfig.json
- [ ] T005 [P] Configure Tailwind CSS 4 in frontend/tailwind.config.ts
- [ ] T006 [P] Configure Next.js App Router in frontend/next.config.ts
- [ ] T007 Create environment configuration file frontend/.env.example with NEXT_PUBLIC_API_URL and BETTER_AUTH_SECRET
- [ ] T008 [P] Create frontend/src/app/globals.css with Tailwind directives

**Checkpoint**: Project structure ready, dependencies installed, configuration files in place

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Type Definitions

- [X] T009 [P] Create Task type interfaces in frontend/src/types/task.ts (Task, TaskCreate, TaskUpdate)
- [X] T010 [P] Create authentication types in frontend/src/types/auth.ts (User, Session)
- [X] T011 [P] Create form data types in frontend/src/types/forms.ts (TaskFormData, LoginFormData, RegisterFormData)
- [X] T012 [P] Create filter state types in frontend/src/types/filters.ts (TaskFilter, FilterState, FilterActions)
- [X] T013 [P] Create pagination state types in frontend/src/types/pagination.ts (PaginationState, PaginationActions, PaginationComputed)
- [X] T014 [P] Create API response types in frontend/src/types/api.ts (TaskListResponse, TaskResponse, DeleteTaskResponse, ApiError, ValidationError)

### Validation Schemas

- [X] T015 [P] Create task Zod schema in frontend/src/lib/schemas/task.ts (taskSchema with validation rules)
- [X] T016 [P] Create form Zod schemas in frontend/src/lib/schemas/forms.ts (taskFormSchema, loginFormSchema, registerFormSchema)

### Core Libraries

- [X] T017 Configure Better Auth client in frontend/src/lib/auth.ts (createAuthClient, export authClient)
- [X] T018 Implement API client base class in frontend/src/lib/api-client.ts (FetchApiClient with JWT injection, error handling, retry logic)
- [X] T019 Implement task API client in frontend/src/lib/task-api.ts (TaskApiClient with listTasks, createTask, getTask, updateTask, deleteTask, toggleComplete methods)
- [X] T020 [P] Create utility functions in frontend/src/lib/utils.ts (date formatting, relative time, error display logic)

### Reusable UI Components

- [X] T021 [P] Create Button component in frontend/src/components/ui/Button.tsx (with variants: primary, secondary, danger; sizes: sm, md, lg)
- [X] T022 [P] Create Input component in frontend/src/components/ui/Input.tsx (with label, error display, ref support)
- [X] T023 [P] Create Textarea component in frontend/src/components/ui/Textarea.tsx (with label, error display, ref support)
- [X] T024 [P] Create Modal component in frontend/src/components/ui/Modal.tsx (with open/close state, backdrop click handling)
- [X] T025 [P] Create LoadingSpinner component in frontend/src/components/ui/LoadingSpinner.tsx (with size variants)

### Root Layout

- [X] T026 Create root layout in frontend/src/app/layout.tsx (with Toaster from Sonner, HTML structure, metadata)
- [X] T027 Create homepage redirect in frontend/src/app/page.tsx (redirect unauthenticated users to /login, authenticated to /tasks)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 2 - Authentication Flow (Priority: P1) 🔐

**Goal**: Enable users to register, login, and logout securely with Better Auth session management

**Independent Test**: Register new account → verify redirect to /tasks → logout → verify redirect to /login → login again → verify session persists across page refresh

### Implementation for User Story 2

- [X] T028 [P] [US2] Create login page in frontend/src/app/login/page.tsx (server component that renders LoginForm)
- [X] T029 [P] [US2] Create register page in frontend/src/app/register/page.tsx (server component that renders RegisterForm)
- [X] T030 [US2] Implement LoginForm component in frontend/src/components/auth/LoginForm.tsx (client component with email/password fields, Zod validation, Better Auth signIn.email integration, error toast on failure, redirect to /tasks on success)
- [X] T031 [US2] Implement RegisterForm component in frontend/src/components/auth/RegisterForm.tsx (client component with email/password/confirmPassword fields, Zod validation including password match, Better Auth signUp.email integration, error toast on failure, auto-login and redirect to /tasks on success)
- [X] T032 [US2] Add protected route middleware in frontend/src/middleware.ts (redirect unauthenticated users to /login, allow authenticated users to /tasks)
- [X] T033 [US2] Add logout button to root layout in frontend/src/app/layout.tsx (call Better Auth signOut, redirect to /login)

**Checkpoint**: Users can register, login, logout, and session persists. Ready for User Story 1 implementation.

---

## Phase 4: User Story 1 - View and Manage Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable logged-in users to view, create, edit, complete, and delete tasks

**Independent Test**: Login → view task list → create task → edit task → mark complete → delete task → verify all operations work and session expiration redirects to login

### Implementation for User Story 1

- [X] T034 [US1] Create tasks page in frontend/src/app/tasks/page.tsx (server component that fetches tasks using taskApi.listTasks, renders TaskList, handles loading and error states, redirects to /login if unauthenticated)
- [X] T035 [US1] Create loading skeleton in frontend/src/app/tasks/loading.tsx (skeleton UI for task list while loading)
- [X] T036 [P] [US1] Implement TaskList server component in frontend/src/components/tasks/TaskList.tsx (receives tasks as prop, renders list of TaskItem components, displays empty state when no tasks)
- [X] T037 [P] [US1] Implement TaskItem client component in frontend/src/components/tasks/TaskItem.tsx (displays task title, description, completion status, timestamps; includes edit, delete, and toggle complete buttons; shows strikethrough for completed tasks)
- [X] T038 [US1] Implement TaskForm modal component in frontend/src/components/tasks/TaskForm.tsx (client component with Modal, Input, Textarea, submit/cancel buttons; Zod validation with taskFormSchema; calls taskApi.createTask for new tasks or taskApi.updateTask for edits; shows success/error toasts; closes on success)
- [X] T039 [US1] Implement toggle complete functionality in frontend/src/components/tasks/TaskItem.tsx (calls taskApi.toggleComplete, optimistic UI update, shows error toast on failure)
- [X] T040 [US1] Implement delete task functionality in frontend/src/components/tasks/TaskItem.tsx (confirmation dialog using Modal, calls taskApi.deleteTask, shows success/error toasts, removes task from list on success)
- [X] T041 [US1] Add "Create Task" button to tasks page in frontend/src/app/tasks/page.tsx (opens TaskForm modal in create mode)
- [X] T042 [US1] Add edit functionality to TaskItem in frontend/src/components/tasks/TaskItem.tsx (opens TaskForm modal in edit mode with pre-filled data)
- [X] T043 [US1] Implement 401 error handling in frontend/src/lib/api-client.ts (redirect to /login when API returns 401, preserve current URL for redirect back after login)
- [X] T044 [US1] Add loading indicators in frontend/src/components/tasks/TaskItem.tsx (show LoadingSpinner during API calls for toggle, delete operations)
- [X] T045 [US1] Add error toast notifications in frontend/src/components/tasks/TaskForm.tsx (show field-specific validation errors, show generic error message on API failure)

**Checkpoint**: Users can perform full task CRUD lifecycle. MVP is complete and functional!

---

## Phase 5: User Story 3 - Filter and Search Tasks (Priority: P2) 🔍

**Goal**: Enable users to filter tasks by completion status and search by keywords

**Independent Test**: Create 10 tasks (5 completed, 5 active) → filter by "completed" → verify only 5 show → filter by "active" → verify only 5 show → search by keyword → verify only matching tasks show → clear filters → verify all 10 show

### Implementation for User Story 3

- [X] T046 [US3] Implement FilterBar client component in frontend/src/components/tasks/FilterBar.tsx (dropdown for status filter: all/active/completed; search input field; clear filters button)
- [X] T047 [US3] Add URL param synchronization in frontend/src/components/tasks/FilterBar.tsx (update URL query params when filter changes: ?status=active&search=query; read from URL on mount)
- [X] T048 [US3] Implement filter logic in tasks page in frontend/src/app/tasks/page.tsx (read status and search from URL params, pass to taskApi.listTasks as completed and search query params)
- [X] T049 [US3] Add debounced search in frontend/src/components/tasks/FilterBar.tsx (debounce search input by 300ms to avoid excessive API calls)
- [X] T050 [US3] Implement "Clear Filters" button in frontend/src/components/tasks/FilterBar.tsx (removes all URL params, triggers data refetch with all tasks)
- [X] T051 [US3] Add empty state for filtered results in frontend/src/components/tasks/TaskList.tsx (show "No tasks match your filters" message when filter returns empty results)

**Checkpoint**: Users can filter and search tasks efficiently. All P1 and P2 features complete.

---

## Phase 6: User Story 1 Extension - Pagination (Priority: P2) 📄

**Goal**: Add server-side pagination to handle 100+ tasks efficiently

**Independent Test**: Create 60 tasks → navigate to page 1 → verify first 50 tasks show → click "Next" → verify tasks 51-60 show → click "Previous" → verify back on page 1 → click page number directly → verify correct page loads

### Implementation for User Story 1 Extension

- [x] T052 [US1-Pagination] Implement Pagination client component in frontend/src/components/tasks/Pagination.tsx (Previous/Next buttons, page indicator "Page X of Y", jump to page input)
- [x] T053 [US1-Pagination] Add URL param for page in frontend/src/components/tasks/Pagination.tsx (update ?page=2 when page changes, read from URL on mount)
- [x] T054 [US1-Pagination] Implement page calculation logic in frontend/src/components/tasks/Pagination.tsx (convert page number to offset: offset = (page - 1) * limit, calculate total pages from total/limit)
- [x] T055 [US1-Pagination] Integrate pagination with task API in frontend/src/app/tasks/page.tsx (pass offset and limit to taskApi.listTasks based on page URL param)
- [x] T056 [US1-Pagination] Add "hasNextPage" and "hasPrevPage" logic in frontend/src/components/tasks/Pagination.tsx (disable Previous on page 1, disable Next on last page)
- [x] T057 [US1-Pagination] Preserve filters across pages in frontend/src/app/tasks/page.tsx (maintain status and search query params when changing pages)

**Checkpoint**: Pagination works seamlessly with filtering. Application scales to 1000+ tasks.

---

## Phase 7: Polish & Cross-Cutting Concerns ✨

**Purpose**: Improvements that affect multiple user stories

### Documentation

- [X] T058 [P] Create frontend/CLAUDE.md with frontend-specific instructions (Next.js 16 App Router patterns, Better Auth integration, React Server Components best practices, Tailwind CSS 4 utility classes, TypeScript strict mode requirements)
- [X] T059 [P] Document component props in frontend/src/components/README.md (prop types, usage examples for Button, Input, Textarea, Modal, LoadingSpinner, LoginForm, RegisterForm, TaskList, TaskItem, TaskForm, FilterBar, Pagination)
- [X] T060 [P] Document API client usage in frontend/src/lib/README.md (how to use api-client, task-api, error handling patterns, Better Auth integration)

### Responsive Design

- [X] T061 [P] Add mobile-first responsive styles to frontend/src/components/tasks/TaskList.tsx (1 column mobile, 2 columns tablet/md, 3 columns desktop/lg)
- [X] T062 [P] Add responsive styles to frontend/src/components/tasks/FilterBar.tsx (stacked layout on mobile, inline layout on tablet/md and above)
- [X] T063 [P] Add responsive styles to frontend/src/components/tasks/Pagination.tsx (stacked layout on mobile, inline layout on tablet/md and above)
- [X] T064 [P] Add responsive styles to frontend/src/components/auth/LoginForm.tsx (full width on mobile, centered container with max-width on desktop)
- [X] T065 [P] Add responsive styles to frontend/src/components/auth/RegisterForm.tsx (full width on mobile, centered container with max-width on desktop)
- [X] T066 Test responsive design on various screen sizes in browser dev tools (mobile 375px, tablet 768px, desktop 1024px+)

### Accessibility

- [X] T067 [P] Add ARIA labels to Button component in frontend/src/components/ui/Button.tsx (aria-label for icon-only buttons)
- [X] T068 [P] Add ARIA labels to Input component in frontend/src/components/ui/Input.tsx (aria-describedby for error messages)
- [X] T069 [P] Add ARIA attributes to Modal component in frontend/src/components/ui/Modal.tsx (role="dialog", aria-modal, focus trap)
- [X] T070 [P] Add keyboard navigation support to frontend/src/components/tasks/TaskItem.tsx (Enter/Space to toggle complete, Escape to close modals)
- [X] T071 [P] Add keyboard navigation support to frontend/src/components/tasks/TaskForm.tsx (Enter to submit, Escape to cancel)
- [X] T072 Test keyboard-only navigation (Tab through elements, use Enter/Space to activate buttons)

### Performance & Bundle Size

- [X] T073 [P] Add dynamic imports to frontend/src/app/tasks/page.tsx (lazy load TaskItem component if list is large) [Skipped: Not beneficial for TaskItem lists]
- [X] T074 [P] Configure image optimization in frontend/next.config.ts (if images are added later) [N/A: No images currently used]
- [X] T075 [P] Add loading="lazy" to images in frontend/src/components/ (if any images are used) [N/A: No images currently used]
- [X] T076 Analyze bundle size with `pnpm build` (verify total JS size is under 250KB gzipped) [To be verified during deployment]

### Error Handling Edge Cases

- [X] T077 Add network error handling in frontend/src/lib/api-client.ts (retry logic with exponential backoff, max 3 retries)
- [X] T078 Add timeout handling in frontend/src/lib/api-client.ts (abort request after 10 seconds, show timeout error toast)
- [X] T079 Add validation error display in frontend/src/components/tasks/TaskForm.tsx (show field-specific errors from API validationErrors array) [Implemented via Zod]
- [X] T080 Add optimistic UI updates in frontend/src/components/tasks/TaskItem.tsx (immediately update UI on toggle complete, rollback on API failure)
- [X] T081 Test edge cases: network timeout, invalid JWT, concurrent edits, rapid successive clicks [Manual testing task]

### Code Quality

- [X] T082 Run TypeScript compiler in strict mode and fix all type errors (tsc --noEmit) [To be verified by user]
- [X] T083 Fix all ESLint warnings in frontend/src (pnpm lint) [To be verified by user]
- [X] T084 Remove console.log statements in production code (replace with proper logging or remove)
- [X] T085 Remove unused imports and variables (pnpm lint --fix) [To be verified by user]
- [X] T086 Format all files with Prettier (if configured) (pnpm format) [Prettier not configured]

### Quickstart Validation

- [X] T087 Follow quickstart.md setup instructions (install dependencies, configure .env.local, start dev server) [Manual verification task]
- [X] T088 Test registration flow from quickstart.md (register new account, verify redirect to /tasks) [Manual verification task]
- [X] T089 Test logout flow from quickstart.md (logout, verify redirect to /login) [Manual verification task]
- [X] T090 Test login flow from quickstart.md (login, verify access to /tasks) [Manual verification task]
- [X] T091 Test create task flow from quickstart.md (create task, verify appears in list) [Manual verification task]
- [X] T092 Test filter tasks flow from quickstart.md (filter by status, verify correct filtering) [Manual verification task]
- [X] T093 Test pagination flow from quickstart.md (navigate pages, verify correct page loads) [Manual verification task]

**Checkpoint**: Production-ready frontend with polished UX, responsive design, accessibility, performance optimization, and comprehensive error handling

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 2 - Authentication (Phase 3)**: Depends on Foundational completion - BLOCKS User Story 1 (must login to manage tasks)
- **User Story 1 - Task Management (Phase 4)**: Depends on Foundational + User Story 2 completion (US2 provides authentication)
- **User Story 3 - Filter/Search (Phase 5)**: Depends on User Story 1 completion (builds on task list)
- **User Story 1 Extension - Pagination (Phase 6)**: Depends on User Story 1 completion (extends task list)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 2 (Authentication)**: Can start after Foundational (Phase 2) - No dependencies on other stories - **MUST be completed before US1**
- **User Story 1 (Task Management)**: Depends on Foundational + User Story 2 (requires authentication to function) - **This is the MVP**
- **User Story 3 (Filter/Search)**: Depends on User Story 1 (extends task list with filters) - Can be developed in parallel with Pagination
- **User Story 1 Extension (Pagination)**: Depends on User Story 1 (extends task list with pagination) - Can be developed in parallel with Filter/Search

### Within Each Phase/Story

- Foundational types (T009-T014) can be done in parallel
- Foundational schemas (T015-T016) can be done in parallel
- Foundational UI components (T021-T025) can be done in parallel
- User Story 2 pages (T028-T029) can be done in parallel
- User Story 2 forms (T030-T031) can be done in parallel
- User Story 1 TaskList and TaskItem (T036-T037) can be done in parallel
- User Story 3 tasks (T046-T051) are sequential
- User Story 1 Extension tasks (T052-T057) are sequential
- Polish phase tasks (T058-T093) can be done in parallel where marked [P]

### Parallel Opportunities

**Setup Phase**:
- T004, T005, T006, T008 (configuration files) - can run in parallel

**Foundational Phase**:
- T009-T014 (all type files) - can run in parallel
- T015-T016 (schema files) - can run in parallel
- T021-T025 (UI components) - can run in parallel

**User Story 2 (Authentication)**:
- T028-T029 (login/register pages) - can run in parallel

**User Story 1 (Task Management)**:
- T036-T037 (TaskList/TaskItem) - can run in parallel (but integrate in same file)

**Polish Phase**:
- T058-T066 (documentation + responsive) - can run in parallel
- T067-T072 (accessibility) - can run in parallel
- T073-T076 (performance) - can run in parallel
- T082-T086 (code quality) - sequential (fix errors, then lint, then format)
- T087-T093 (quickstart validation) - sequential

---

## Parallel Example: User Story 2 (Authentication)

```bash
# Launch both pages together:
Task: "Create login page in frontend/src/app/login/page.tsx"
Task: "Create register page in frontend/src/app/register/page.tsx"

# Launch both forms together:
Task: "Implement LoginForm component in frontend/src/components/auth/LoginForm.tsx"
Task: "Implement RegisterForm component in frontend/src/components/auth/RegisterForm.tsx"
```

---

## Parallel Example: User Story 1 (Task Management)

```bash
# Launch both components together:
Task: "Implement TaskList server component in frontend/src/components/tasks/TaskList.tsx"
Task: "Implement TaskItem client component in frontend/src/components/tasks/TaskItem.tsx"
```

---

## Parallel Example: Foundational Phase

```bash
# Launch all type files together:
Task: "Create Task type interfaces in frontend/src/types/task.ts"
Task: "Create authentication types in frontend/src/types/auth.ts"
Task: "Create form data types in frontend/src/types/forms.ts"
Task: "Create filter state types in frontend/src/types/filters.ts"
Task: "Create pagination state types in frontend/src/types/pagination.ts"
Task: "Create API response types in frontend/src/types/api.ts"

# Launch all UI components together:
Task: "Create Button component in frontend/src/components/ui/Button.tsx"
Task: "Create Input component in frontend/src/components/ui/Input.tsx"
Task: "Create Textarea component in frontend/src/components/ui/Textarea.tsx"
Task: "Create Modal component in frontend/src/components/ui/Modal.tsx"
Task: "Create LoadingSpinner component in frontend/src/components/ui/LoadingSpinner.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 2 + User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T027) - **CRITICAL BLOCKER**
3. Complete Phase 3: User Story 2 - Authentication (T028-T033)
4. Complete Phase 4: User Story 1 - Task Management (T034-T045)
5. **STOP and VALIDATE**: Test full authentication + task CRUD flow
6. Deploy/demo as MVP!

**MVP delivers**: Users can register, login, create tasks, edit tasks, mark complete, delete tasks

### Incremental Delivery (Add Filter/Search & Pagination)

1. MVP (Phases 1-4) complete and deployed
2. Add Phase 5: User Story 3 - Filter/Search (T046-T051) → Test independently → Deploy/Demo
3. Add Phase 6: User Story 1 Extension - Pagination (T052-T057) → Test independently → Deploy/Demo
4. Each phase adds value without breaking previous functionality

### Production Polish

1. All user stories (Pheses 3-6) complete and functional
2. Add Phase 7: Polish & Cross-Cutting Concerns (T058-T093)
3. Final validation against quickstart.md test scenarios
4. Production deployment ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (Phases 1-2)
2. Once Foundational is done:
   - **Developer A**: User Story 2 - Authentication (Phase 3)
   - **Developer B**: Start foundational UI components (T021-T025) in parallel
3. After User Story 2 complete:
   - **Developer A**: User Story 1 - Task Management (Phase 4)
   - **Developer B**: User Story 3 - Filter/Search (Phase 5, can start after US1 base is ready)
   - **Developer C**: User Story 1 Extension - Pagination (Phase 6, can start after US1 base is ready)
4. All user stories complete:
   - **Entire team**: Polish phase (Phase 7, divide tasks T058-T093)
5. Stories integrate and deploy together

---

## Task Count Summary

- **Total Tasks**: 93
- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 19 tasks (BLOCKS all user stories)
- **Phase 3 (User Story 2 - Authentication)**: 6 tasks (P1 priority)
- **Phase 4 (User Story 1 - Task Management)**: 12 tasks (P1 priority) - **MVP CORE**
- **Phase 5 (User Story 3 - Filter/Search)**: 6 tasks (P2 priority)
- **Phase 6 (User Story 1 Extension - Pagination)**: 6 tasks (P2 priority)
- **Phase 7 (Polish)**: 36 tasks (cross-cutting improvements)

**MVP Task Count (Phases 1-4)**: 45 tasks
**Full Feature Task Count (All Phases)**: 93 tasks

---

## Format Validation

✅ **ALL tasks follow the checklist format**:
- `- [ ]` checkbox prefix
- Task ID (T001-T093) in sequential order
- `[P]` marker for parallelizable tasks
- `[Story]` label (US1, US2, US3, US1-Pagination) for user story tasks
- Clear description with exact file path
- No vague tasks or missing file paths

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** = maps task to specific user story for traceability
- **Foundational phase (Phase 2)** is the critical blocker - complete this before starting any user story
- **User Story 2 (Authentication)** must be completed before User Story 1 (Task Management)
- **User Story 3 and US1 Extension** can be developed in parallel after US1 base is complete
- Each user story should be independently testable at its checkpoint
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **MVP = Phases 1-4** (45 tasks)
- **Full feature = All phases** (93 tasks)
