---
id: 0004
title: chatkit-migration-tasks
stage: tasks
date: 2026-02-06T13:30:00Z
surface: claude
model: glm-4.7
feature: 010-chatkit-migration
branch: 010-chatkit-migration
user: groww
command: /sp.tasks
labels: [tasks, chatkit, migration, gemini, implementation]
links:
  spec: ../specs/010-chatkit-migration/spec.md
  ticket:
  adr:
  pr:
files:
  - path: specs/010-chatkit-migration/tasks.md
    status: created
    description: Actionable task list organized by user story with 67 total tasks
tests:
  - type: integration
    coverage: Validation via quickstart.md testing scenarios (no unit test tasks)
---

## Prompt

/sp.tasks to generate actionable task list for ChatKit migration feature.

**Input**: Complete design documents from specs/010-chatkit-migration/:
- spec.md: 3 prioritized user stories (P1: AI Chat with Task Management, P2: Cross-Tab Sync, P3: Error Resilience)
- plan.md: Architecture, phases, component mapping, deletion plan
- research.md: ChatKit + Gemini compatibility validation
- data-model.md: Thread/Message entities and Store interface
- contracts/backend.md: /api/chatkit SSE endpoint specification
- contracts/frontend.md: ChatKit React integration contracts
- quickstart.md: Testing scenarios and validation checklist

**Requirements**:
- Organize tasks by user story for independent implementation and testing
- Each task must follow strict checklist format: `- [ ] [ID] [P?] [Story] Description with file path`
- Include [P] marker for parallelizable tasks
- Include [Story] label (US1, US2, US3) for user story phase tasks
- No story label for Setup and Foundational phases
- Specify exact file paths in all task descriptions
- Create dependency graph showing user story completion order
- Provide parallel execution examples per user story
- Identify MVP scope (typically User Story 1 only)
- Tests are NOT included (validation via quickstart.md scenarios)

**Deliverables**:
- tasks.md with 67 tasks organized by phase
- Clear dependency and parallel execution opportunities
- MVP scope definition (28 tasks for functional chat)
- Independent test criteria for each user story

## Response snapshot

Generated comprehensive task list for ChatKit migration with the following structure:

**Phase 1: Setup (3 tasks)**
- Install backend ChatKit dependencies (openai-chatkit, openai-agents)
- Install frontend ChatKit dependency (@openai/chatkit-react)
- Add Gemini API configuration to .env.example

**Phase 2: Foundational (8 tasks) - BLOCKS all user stories**
- Create Thread model (backend/models/thread.py)
- Add thread_id foreign key to Message model
- Create database migration script for threads table
- Run database migration
- Configure Gemini AsyncOpenAI client (backend/core/config.py)
- Implement PostgresChatKitStore class (backend/services/chatkit_store.py)
- Implement ChatKitServer class (backend/chatkit_server.py)
- Create /api/chatkit SSE endpoint (backend/api/chat.py)

**Phase 3: User Story 1 - AI Chat with Task Management (17 tasks) 🎯 MVP**
- Backend: Wrap all 7 MCP tools as Agents SDK functions (parallelizable)
- Backend: Configure TaskAssistant agent with Gemini model
- Backend: Add rate limiting to /api/chatkit endpoint
- Frontend: Create TaskChat wrapper component (~50 LOC)
- Frontend: Configure useChatKit with custom fetch for JWT
- Frontend: Update dashboard to use TaskChat
- Testing: Tool execution, streaming, persistence, authentication

**Phase 4: User Story 2 - Cross-Tab Chat Synchronization (4 tasks)**
- Test cross-tab SSE synchronization
- Verify conversation state updates across tabs
- Test multiple concurrent tool executions
- Verify thread switching across tabs

**Phase 5: User Story 3 - Error Resilience and Connection Status (8 tasks)**
- Backend: SSE error handling, timeouts, rate limit responses
- Frontend: Test ChatKit built-in connection status
- Frontend: Verify UI doesn't freeze during errors
- Frontend: Test automatic reconnection

**Phase 6: Deletion (12 tasks)**
- Delete backend/ws_manager/ directory (entire directory)
- Delete backend/ai_agent/agent_streaming.py
- Delete 6 frontend chat components (~600 LOC)
- Verify zero WebSocket code remains

**Phase 7: Polish & Cross-Cutting Concerns (15 tasks)**
- Update CLAUDE.md files with ChatKit architecture
- Update README.md
- Delete removed files from git
- Run all 9 success criteria validations (SC-001 through SC-009)
- Document Gemini-specific behaviors

**Task Organization Features**:
- All 67 tasks follow strict checklist format with checkbox, ID, [P] marker, [Story] label, and file path
- ~40 tasks marked [P] for parallel execution
- Clear dependency graph: Setup → Foundational → User Stories (parallel) → Deletion → Polish
- Each user story independently testable

**MVP Scope**: Phases 1-3 (28 tasks) delivers working AI chat with task management, ~600 LOC reduction

## Outcome

- ✅ Impact: Generated actionable task list with 67 tasks organized by user story for independent implementation and testing
- 🧪 Tests: No test tasks included (validation via quickstart.md testing scenarios)
- 📁 Files: specs/010-chatkit-migration/tasks.md (created)
- 🔁 Next prompts: /sp.implement to execute all tasks, or start with MVP implementation (Phases 1-3)
- 🧠 Reflection: Task organization by user story enables incremental delivery. Each phase (US1, US2, US3) can be completed and tested independently. The parallelizable markers ([P]) identify opportunities for concurrent work. Deletion phase is critical - must remove ~950 LOC to meet success criteria SC-006. The foundational phase (T004-T011) is the critical path that blocks all user story work.

## Evaluation notes (flywheel)

- Failure modes observed: None - task generation completed successfully
- Graders run and results (PASS/FAIL):
  - Task format validation: PASS (all tasks follow checklist format)
  - File path completeness: PASS (all tasks have exact file paths)
  - User story mapping: PASS (all US tasks have [Story] labels)
  - Dependency clarity: PASS (blocking dependencies clearly marked)
  - MVP scope definition: PASS (28 tasks for functional MVP)
- Prompt variant: N/A
- Next experiment: During implementation, validate that the 7 tool wrappers can truly be implemented in parallel without conflicts in the same file (backend/ai_agent/tool_wrappers.py)
