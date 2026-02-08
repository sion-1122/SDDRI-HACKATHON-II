# Tasks: ChatKit Migration with Gemini Compatibility

**Input**: Design documents from `/specs/010-chatkit-migration/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are NOT included in this migration task list. The specification focuses on functional implementation with validation via quickstart.md testing scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Per Principle VI (Monorepo Structure Standard)**:
- **Web app (Phases 2-3)**: `backend/`, `frontend/` with their own structures
- Paths shown below follow the existing monorepo structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure ChatKit packages

- [x] T001 [P] Install backend ChatKit dependencies in backend/pyproject.toml
- [x] T002 [P] Install frontend ChatKit dependency in frontend/package.json (already installed)
- [x] T003 [P] Add Gemini API configuration to backend/.env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Thread model in backend/models/thread.py
- [x] T005 [P] Add thread_id foreign key to Message model in backend/models/message.py
- [x] T006 [P] Create database migration script for threads table in backend/migrations/migrate_threads.sql
- [ ] T007 Run database migration to create threads table (MANUAL: psql $DATABASE_URL < backend/migrations/migrate_threads.sql)
- [x] T008 [P] Configure Gemini AsyncOpenAI client in backend/core/config.py
- [x] T009 [P] Implement PostgresChatKitStore class in backend/services/chatkit_store.py
- [x] T010 Implement ChatKitServer class in backend/chatkit_server.py
- [x] T011 Create /api/chatkit SSE endpoint in backend/api/chat.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - AI Chat with Task Management (Priority: P1) 🎯 MVP

**Goal**: Users can interact with AI chatbot to manage tasks with real-time tool execution visualization and conversation persistence

**Independent Test**: Open chat interface, send "create a task called buy groceries", verify (1) response streams correctly, (2) tool execution visualizes, (3) task appears in task list

### Backend Implementation for US1

- [x] T012 [P] [US1] Wrap create_task MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py
- [x] T013 [P] [US1] Wrap list_tasks MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py
- [x] T014 [P] [US1] Wrap update_task MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py
- [x] T015 [P] [US1] Wrap delete_task MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py
- [x] T016 [P] [US1] Wrap complete_task MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py
- [x] T017 [P] [US1] Wrap bulk_complete_tasks MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py
- [x] T018 [P] [US1] Wrap bulk_delete_tasks MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py
- [x] T019 [US1] Configure TaskAssistant agent with Gemini model and wrapped tools in backend/chatkit_server.py
- [x] T020 [US1] Add rate limiting to /api/chatkit endpoint in backend/api/chat.py
- [ ] T021 [US1] Test tool execution through ChatKit SSE streaming (manual testing)

### Frontend Implementation for US1

- [x] T022 [P] [US1] Create TaskChat wrapper component in frontend/src/components/chat/TaskChat.tsx
- [x] T023 [US1] Configure useChatKit with custom fetch for JWT cookies in frontend/src/components/chat/TaskChat.tsx
- [x] T024 [US1] Update chat page to use TaskChat instead of ChatInterface in frontend/src/app/chat/page.tsx
- [ ] T025 [US1] Test chat interface with streaming responses (manual: run app and test)
- [ ] T026 [US1] Test tool execution visualization in ChatKit UI (manual: run app and test)
- [ ] T027 [US1] Test conversation persistence across page refreshes (manual: run app and test)
- [ ] T028 [US1] Verify authentication works with custom fetch and JWT cookies (manual: run app and test)

**Checkpoint**: At this point, User Story 1 backend and frontend code is complete! Manual testing tasks (T025-T028) require running the application.

---

## Phase 4: User Story 2 - Cross-Tab Chat Synchronization (Priority: P2)

**Goal**: Chat state synchronizes across multiple browser tabs automatically

**Independent Test**: Open app in two tabs, send message in tab A, verify tab B shows new message in conversation history

### Implementation for US2

- [ ] T029 [P] [US2] Test cross-tab synchronization with SSE (ChatKit handles this automatically)
- [ ] T030 [US2] Verify conversation state updates when tab is closed and reopened
- [ ] T031 [US2] Test multiple concurrent tool executions across tabs
- [ ] T032 [US2] Verify thread switching works correctly across tabs

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Error Resilience and Connection Status (Priority: P3)

**Goal**: Chat interface gracefully handles network errors and displays connection status

**Independent Test**: Simulate network failure (Chrome DevTools offline mode), verify interface shows disconnected indicator and recovers when network returns

### Backend Implementation for US3

- [x] T033 [P] [US3] Add SSE error handling for connection drops in backend/api/chat.py
- [x] T034 [US3] Add timeout handling for long-running tool executions in backend/chatkit_server.py
- [ ] T035 [P] [US3] Test 429 rate limit response format in backend/api/chat.py
- [ ] T036 [P] [US3] Test 503/504 AI service error responses in backend/api/chat.py

### Frontend Implementation for US3

- [ ] T037 [P] [US3] Test ChatKit built-in connection status indicators
- [ ] T038 [US3] Test error message display for network failures
- [ ] T039 [US3] Verify UI doesn't freeze during backend errors
- [ ] T040 [US3] Test automatic reconnection when network returns

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Deletion (Remove Legacy Code)

**Purpose**: Delete all custom chat components and WebSocket code that have been replaced

- [x] T041 [P] Delete backend/ws_manager/manager.py
- [x] T042 [P] Delete backend/ws_manager/events.py
- [x] T043 [P] Delete backend/ws_manager/__init__.py
- [x] T044 [P] Delete backend/ws_manager/ directory
- [x] T045 [P] Delete backend/ai_agent/agent_streaming.py
- [x] T046 [P] Delete frontend/src/components/chat/ChatInterface.tsx
- [x] T047 [P] Delete frontend/src/components/chat/MessageList.tsx
- [x] T048 [P] Delete frontend/src/components/chat/MessageInput.tsx
- [x] T049 [P] Delete frontend/src/components/chat/ProgressBar.tsx
- [x] T050 [P] Delete frontend/src/components/chat/ConnectionStatus.tsx
- [x] T051 [P] Delete frontend/src/components/chat/useWebSocket.ts
- [x] T052 Verify zero WebSocket code remains in codebase

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, documentation updates, and validation

- [x] T053 [P] Update backend/CLAUDE.md with ChatKit architecture details
- [x] T054 [P] Update frontend/CLAUDE.md with ChatKit integration details
- [x] T055 [P] Update README.md with new chat architecture description
- [x] T056 [P] Delete removed files from git repository
- [ ] T057 Run quickstart.md validation checklist
- [ ] T058 Verify < 2s first token response time (SC-001)
- [ ] T059 Verify < 500ms tool execution visibility (SC-002)
- [ ] T060 Verify 100% Gemini LLM usage, no OpenAI models (SC-003)
- [ ] T061 Verify zero WebSocket code remains (SC-004)
- [ ] T062 Verify 95% conversation persistence rate (SC-005)
- [ ] T063 Count LOC reduction to verify ≥ 600 lines removed (SC-006)
- [ ] T064 Verify all 7 tools execute successfully (SC-007)
- [ ] T065 Verify graceful error handling without UI freezes (SC-008)
- [ ] T066 Verify < 1s thread creation time (SC-009)
- [ ] T067 Document any Gemini-specific behaviors in specs/010-chatkit-migration/research.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Depends on US1 for chat functionality
  - User Story 3 (P3): Can start after Foundational - Depends on US1 for chat functionality
- **Deletion (Phase 6)**: Depends on US1, US2, US3 being complete and validated
- **Polish (Phase 7)**: Depends on all previous phases being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Core MVP, no other story dependencies
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 with cross-tab sync
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US1 with error handling

### Within Each User Story

- Tool wrapping (T012-T018) can run in parallel
- Agent configuration (T019) depends on tool wrapping
- Endpoint rate limiting (T020) can run in parallel with testing
- Frontend TaskChat creation (T022-T023) can run in parallel with backend work
- Dashboard update (T024) depends on TaskChat creation

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- All tasks marked [P] can run in parallel

**Foundational Phase (Phase 2)**:
- T005, T006, T008, T009 can run in parallel (different files)
- T004 must complete before T005 (Thread model before Message model modification)

**User Story 1 (Phase 3)**:
- T012-T018 (all 7 tool wrappers) can run in parallel
- T022 (TaskChat creation) can run in parallel with backend tool wrapping

**User Story 2 (Phase 4)**:
- All tasks can run in parallel once US1 is complete

**User Story 3 (Phase 3)**:
- Backend error handling (T033-T036) can run in parallel
- Frontend error testing (T037-T040) can run in parallel

**Deletion Phase (Phase 6)**:
- All tasks marked [P] can run in parallel

**Polish Phase (Phase 7)**:
- Documentation updates (T053-T056) can run in parallel
- Success criteria verification (T058-T066) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all 7 tool wrapper tasks together (they're independent files):
Task: "Wrap create_task MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py"
Task: "Wrap list_tasks MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py"
Task: "Wrap update_task MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py"
Task: "Wrap delete_task MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py"
Task: "Wrap complete_task MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py"
Task: "Wrap bulk_complete_tasks MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py"
Task: "Wrap bulk_delete_tasks MCP tool as Agents SDK function in backend/ai_agent/tool_wrappers.py"

# These can all run in parallel because they modify the same file but with independent functions
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently using quickstart.md
5. Deploy/demo MVP if ready

**MVP Deliverables**:
- Working AI chat with task management
- Real-time streaming responses
- Tool execution visualization
- Conversation persistence
- ~600 LOC reduction (frontend components deleted)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Complete Deletion → Verify code reduction → Deploy/Demo
6. Complete Polish → Final validation → Production deployment

Each phase adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (backend tool wrapping + agent config)
   - Developer B: User Story 1 (frontend TaskChat + dashboard update)
   - Developer C: User Story 2 (cross-tab testing, mostly validation)
3. Stories complete and integrate independently

---

## Notes

- **[P] tasks** = different files or no dependencies, can run in parallel
- **[Story] label** = maps task to specific user story for traceability (US1, US2, US3)
- Each user story should be independently completable and testable
- **No test tasks included** - validation via quickstart.md testing scenarios
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Deletion is critical**: Must remove ~950 LOC of custom code to meet success criteria
- **Gemini validation**: Ensure no OpenAI model IDs appear anywhere in logs or config

---

## Task Count Summary

- **Total Tasks**: 67
- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 8 tasks
- **Phase 3 (US1 - MVP)**: 17 tasks
- **Phase 4 (US2)**: 4 tasks
- **Phase 5 (US3)**: 8 tasks
- **Phase 6 (Deletion)**: 12 tasks
- **Phase 7 (Polish)**: 15 tasks

**Parallel Opportunities**: ~40 tasks marked [P] can run in parallel with proper coordination

**Independent Test Criteria**:
- US1: Chat interface + task creation with streaming + tool visualization
- US2: Cross-tab message synchronization
- US3: Error recovery and connection status

**Suggested MVP Scope**: Phases 1-3 (Setup + Foundational + User Story 1) = 28 tasks for working MVP

---

## Format Validation

✅ **All tasks follow checklist format**: `- [ ] [ID] [P?] [Story?] Description with file path`
✅ **All Story labels present**: US1, US2, US3 used consistently
✅ **All file paths specified**: Every task includes exact file location
✅ **No vague tasks**: Each task has specific, actionable description
