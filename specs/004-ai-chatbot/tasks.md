# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/004-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.yaml

**Tests**: Test tasks included for validation and quality assurance

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Per Principle VI (Monorepo Structure Standard)**:
- **Web app (Phases 2-3)**: `backend/`, `frontend/` with their own structure
- Paths reflect the monorepo structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install backend Python dependencies (OpenAI SDK, AsyncOpenAI, Gemini SDK, MCP SDK, FastAPI) in backend/
- [X] T002 [P] Install frontend dependencies (@openai/chatkit-react) in frontend/
- [X] T003 [P] Configure Gemini API authentication with environment variables in backend/core/config.py
- [X] T004 [P] Setup database connection pooling for conversation/message tables in backend/core/database.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create Conversation model in backend/models/conversation.py
- [X] T006 [P] Create Message model in backend/models/message.py
- [X] T007 Create database migration for conversation and message tables in backend/migrations/
- [X] T008 [P] Implement message length validation (10,000 char limit) in backend/core/validators.py
- [X] T009 [P] Setup MCP server structure in backend/mcp_server/server.py
- [X] T010 Create base MCP tool schema and registration in backend/mcp_server/tools/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks through natural language input

**Independent Test**: Send "Add a task to buy groceries" and verify task is created with correct title, AI confirms action

### Tests for User Story 1

- [X] T011 [P] [US1] Integration test for task creation via natural language in backend/tests/integration/test_chat_task_creation.py
- [X] T012 [P] [US1] Contract test for chat API endpoint in backend/tests/contract/test_chat_api.py

### Implementation for User Story 1

- [X] T013 [P] [US1] Implement add_task MCP tool in backend/mcp_server/tools/add_task.py
- [X] T014 [P] [US1] Initialize OpenAI Agents SDK with Gemini model via AsyncOpenAI in backend/ai_agent/agent.py
- [X] T015 [US1] Implement chat API endpoint POST /api/{user_id}/chat in backend/api/chat.py
- [X] T016 [US1] Implement conversation history loading in backend/services/conversation.py
- [X] T017 [US1] Add user message persistence before AI processing in backend/api/chat.py
- [X] T018 [US1] Add AI response persistence after processing in backend/api/chat.py
- [X] T019 [US1] Create ChatInterface React component in frontend/components/chat/ChatInterface.tsx
- [X] T020 [US1] Create chat page route in frontend/app/chat/page.tsx
- [X] T021 [US1] Implement daily message limit enforcement (100/day) in backend/services/rate_limiter.py
- [X] T022 [US1] Add error handling for Gemini API unavailability via AsyncOpenAI in backend/ai_agent/agent.py

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language

---

## Phase 4: User Story 2 - Conversational Task Listing (Priority: P1)

**Goal**: Users can ask for their tasks in natural language and receive a readable list

**Independent Test**: Create 5 tasks, then ask "What are my tasks?" and verify AI returns formatted list with completion status

### Tests for User Story 2

- [X] T023 [P] [US2] Integration test for task listing via natural language in backend/tests/integration/test_chat_task_listing.py

### Implementation for User Story 2

- [X] T024 [P] [US2] Implement list_tasks MCP tool in backend/mcp_server/tools/list_tasks.py
- [X] T025 [US2] Add conversation context retrieval for existing conversations in backend/services/conversation.py (already implemented)
- [X] T026 [US2] Handle empty task list responses in backend/ai_agent/agent.py
- [X] T027 [US2] Add task status filtering (pending/completed) to list_tasks tool in backend/mcp_server/tools/list_tasks.py

**Checkpoint**: At this point, Users 1 AND 2 should both work independently

---

## Phase 5: User Story 6 - Persistent Conversations (Priority: P1)

**Goal**: Chat history persists across sessions and server restarts

**Independent Test**: Send messages, refresh page or restart server, verify conversation loads and AI maintains context

### Tests for User Story 6

- [ ] T028 [P] [US6] Integration test for conversation persistence in backend/tests/integration/test_conversation_persistence.py
- [ ] T029 [P] [US6] Test for 90-day auto-deletion policy in backend/tests/integration/test_conversation_retention.py

### Implementation for User Story 6

- [ ] T030 [P] [US6] Implement conversation loading by conversation_id in backend/services/chat_service.py
- [ ] T031 [P] [US6] Add conversation creation flow when no conversation_id provided in backend/services/chat_service.py
- [ ] T032 [US6] Store conversation_id in frontend chat state in frontend/components/chat/ChatInterface.tsx
- [ ] T033 [US6] Implement 90-day conversation auto-deletion job in backend/services/conversation_cleanup.py
- [ ] T034 [US6] Add conversation.updated_at trigger on message creation in backend/models/message.py
- [ ] T035 [US6] Handle auto-deleted conversations gracefully in backend/api/chat.py

**Checkpoint**: At this point, User Stories 1, 2, AND 6 should all work independently

---

## Phase 6: User Story 3 - Natural Language Task Updates (Priority: P2)

**Goal**: Users can modify existing tasks using conversational commands

**Independent Test**: Create task "buy groceries", send "Change task 1 to buy groceries and milk", verify title updated correctly

### Tests for User Story 3

- [ ] T036 [P] [US3] Integration test for task updates via natural language in backend/tests/integration/test_chat_task_updates.py

### Implementation for User Story 3

- [X] T037 [P] [US3] Implement update_task MCP tool in backend/mcp_server/tools/update_task.py
- [X] T038 [US3] Handle ambiguous task references in backend/ai_agent/agent.py
- [X] T039 [US3] Add validation for non-existent task updates in backend/mcp_server/tools/update_task.py
- [X] T040 [US3] Format task update confirmations in backend/ai_agent/agent.py

**Checkpoint**: User Stories 1, 2, 3, AND 6 should all work independently

---

## Phase 7: User Story 4 - Conversational Task Completion (Priority: P2)

**Goal**: Users can mark tasks as complete through natural language

**Independent Test**: Create task, send "Mark task 1 as complete", verify completion status changes to true

### Tests for User Story 4

- [ ] T041 [P] [US4] Integration test for task completion via natural language in backend/tests/integration/test_chat_task_completion.py

### Implementation for User Story 4

- [X] T042 [P] [US4] Implement complete_task MCP tool in backend/mcp_server/tools/complete_task.py
- [X] T043 [US4] Support task completion and uncompletion in backend/mcp_server/tools/complete_task.py
- [X] T044 [US4] Handle "mark all tasks as complete" command in backend/mcp_server/tools/complete_all_tasks.py
- [X] T045 [US4] Add completion confirmations with task count in backend/mcp_server/tools/complete_all_tasks.py

**Checkpoint**: User Stories 1, 2, 3, 4, AND 6 should all work independently

---

## Phase 8: User Story 5 - Conversational Task Deletion (Priority: P2)

**Goal**: Users can delete tasks using natural language

**Independent Test**: Create task, send "Delete task 1", verify task removed from database

### Tests for User Story 5

- [ ] T046 [P] [US5] Integration test for task deletion via natural language in backend/tests/integration/test_chat_task_deletion.py

### Implementation for User Story 5

- [X] T047 [P] [US5] Implement delete_task MCP tool in backend/mcp_server/tools/delete_task.py
- [X] T048 [US5] Add confirmation prompt for "delete all tasks" in backend/mcp_server/tools/delete_all_tasks.py
- [X] T049 [US5] Handle non-existent task deletion attempts in backend/mcp_server/tools/delete_task.py
- [X] T050 [US5] Format deletion confirmations in backend/mcp_server/tools/delete_all_tasks.py

**Checkpoint**: User Stories 1, 2, 3, 4, 5, AND 6 should all work independently

---

## Phase 9: User Story 7 - Multi-Action Conversational Requests (Priority: P3)

**Goal**: Users can request multiple actions in a single message

**Independent Test**: Send "Add a task to buy milk and mark task 1 as complete", verify both actions occur

### Tests for User Story 7

- [ ] T051 [P] [US7] Integration test for multi-action requests in backend/tests/integration/test_chat_multi_actions.py

### Implementation for User Story 7

- [ ] T052 [US7] Enable MCP tool chaining in backend/ai_agent/agent.py
- [ ] T053 [US7] Handle tool execution errors in multi-action flows in backend/ai_agent/agent.py
- [ ] T054 [US7] Aggregate multiple tool results into single response in backend/ai_agent/agent.py
- [ ] T055 [US7] Request clarification for vague multi-action commands in backend/ai_agent/agent.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T056 [P] Add request queue with exponential backoff for Gemini rate limits in backend/services/rate_limiter.py
- [ ] T057 [P] Implement prompt injection sanitization in backend/services/security.py
- [ ] T058 [P] Add audit logging for all MCP tool invocations in backend/mcp_server/server.py
- [ ] T059 [P] Create database indexes for conversation/message queries in backend/migrations/
- [ ] T060 [P] Add comprehensive error messages for edge cases in backend/api/chat.py
- [ ] T061 Add MessageList React component in frontend/components/chat/MessageList.tsx
- [ ] T062 Add MessageInput React component in frontend/components/chat/MessageInput.tsx
- [ ] T063 Update quickstart.md with actual environment setup steps
- [ ] T064 [P] Run backend test suite and ensure 70%+ coverage in backend/tests/
- [ ] T065 [P] Run frontend component tests in frontend/tests/chat/
- [ ] T066 Validate quickstart.md instructions by running through setup process

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-9)**: All depend on Foundational phase completion
  - US1, US2, US6 (P1 stories) should be completed first for MVP
  - US3, US4, US5 (P2 stories) build on P1 stories
  - US7 (P3 story) enhances all previous stories
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - Independent of US1
- **User Story 6 (P1)**: Can start after Foundational - Independent of US1 and US2
- **User Story 3 (P2)**: Should follow US1 (builds on task creation but independently testable)
- **User Story 4 (P2)**: Should follow US1 (builds on task creation but independently testable)
- **User Story 5 (P2)**: Should follow US1 (builds on task creation but independently testable)
- **User Story 7 (P3)**: Should follow US1-US5 (enhances existing functionality)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Models before services
- MCP tools before AI agent
- AI agent before chat API
- Backend before frontend
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T004)
- All Foundational tasks marked [P] can run in parallel (T006, T008-T010)
- Once Foundational phase completes, US1, US2, US6 can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members (after P1 stories complete)

---

## Parallel Example: MVP (User Stories 1, 2, 6)

After Foundational phase completes, these stories can be worked on in parallel:

```bash
# Developer A: User Story 1 (Task Creation)
Task: "T013 [P] [US1] Implement add_task MCP tool"
Task: "T019 [P] [US1] Create ChatInterface React component"

# Developer B: User Story 2 (Task Listing)
Task: "T024 [P] [US2] Implement list_tasks MCP tool"
Task: "T026 [P] [US2] Handle empty task list responses"

# Developer C: User Story 6 (Conversation Persistence)
Task: "T030 [P] [US6] Implement conversation loading"
Task: "T032 [P] [US6] Store conversation_id in frontend"
```

Each developer's work is independent and can be tested separately.

---

## Implementation Notes

### Gemini + OpenAI Agents SDK Integration Pattern

**Critical Implementation Detail** (from plan.md):

The AI agent MUST use the OpenAI Agents SDK with Gemini models via the AsyncOpenAI adapter:

```python
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from backend.core.config import SETTINGS

# Create AsyncOpenAI client configured for Gemini API
gemini_client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=SETTINGS.gemini_api_key
)

# Initialize task management agent
task_agent = Agent(
    name="task_manager",
    instructions="""You are a helpful task management assistant.
    Users can create, list, update, complete, and delete tasks through natural language.
    Always confirm actions clearly and ask for clarification when requests are ambiguous.""",
    model=OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=gemini_client,
    ),
)

# Execute agent with conversation history
result = await Runner.run(
    task_agent,
    input=conversation_history + [current_message],
    context={"user_id": user_id}
)
```

**Why this pattern?**
- **Cost**: Gemini models are free tier vs. paid OpenAI models
- **Compatibility**: AsyncOpenAI adapter provides OpenAI-compatible interface to Gemini API
- **Orchestration**: OpenAI Agents SDK provides superior tool calling and agent management

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 6 - All P1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Task Creation)
4. Complete Phase 4: User Story 2 (Task Listing) - can parallelize with US1
5. Complete Phase 5: User Story 6 (Persistence) - can parallelize with US1 and US2
6. **STOP and VALIDATE**: Test all three P1 stories working together
7. Deploy/demo MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Task Creation) → Test independently → Feature complete
3. Add US2 (Task Listing) → Test independently → Feature complete
4. Add US6 (Persistence) → Test independently → MVP COMPLETE!
5. Add US3 (Task Updates) → Test independently → Enhancement
6. Add US4 (Task Completion) → Test independently → Enhancement
7. Add US5 (Task Deletion) → Test independently → Enhancement
8. Add US7 (Multi-Action) → Test independently → Polish
9. Polish phase → Production ready

Each P1 story adds independent value without breaking previous stories.

### Parallel Team Strategy

With 3 developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Task Creation)
   - Developer B: User Story 2 (Task Listing)
   - Developer C: User Story 6 (Persistence)
3. After P1 stories complete:
   - Developer A: User Story 3 (Task Updates)
   - Developer B: User Story 4 (Task Completion)
   - Developer C: User Story 5 (Task Deletion)
4. All: Polish phase together

---

## Format Validation

✅ ALL tasks follow the checklist format:
- Checkbox prefix: `- [ ]`
- Sequential Task IDs: T001 through T066
- [P] marker for parallelizable tasks
- [Story] label for user story tasks (US1-US7)
- Exact file paths in every description
- Setup phase: No story labels ✅
- Foundational phase: No story labels ✅
- User Story phases: Story labels included ✅
- Polish phase: No story labels ✅

---

## Notes

- 66 total tasks across all phases
- 21 tasks are parallelizable (marked [P])
- 7 user stories organized by priority (P1→P2→P3)
- MVP = Phases 1-5 (Setup, Foundational, US1, US2, US6) = 35 tasks
- Each user story is independently completable and testable
- P1 stories (US1, US2, US6) have no interdependencies
- P2 stories (US3, US4, US5) build on P1 but remain independently testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
