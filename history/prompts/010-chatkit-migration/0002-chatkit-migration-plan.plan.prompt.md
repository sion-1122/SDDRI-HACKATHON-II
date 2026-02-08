---
id: 0002
title: chatkit-migration-plan
stage: plan
date: 2026-02-06T13:00:00Z
surface: claude
model: glm-4.7
feature: 010-chatkit-migration
branch: 010-chatkit-migration
user: groww
command: /sp.plan
labels: [plan, chatkit, migration, gemini, architecture]
links:
  spec: ../specs/010-chatkit-migration/spec.md
  ticket:
  adr:
  pr:
files:
  - path: specs/010-chatkit-migration/plan.md
    status: created
    description: Complete implementation plan with architecture diagrams and phases
  - path: specs/010-chatkit-migration/research.md
    status: created
    description: ChatKit + Gemini compatibility research with decision rationale
  - path: specs/010-chatkit-migration/data-model.md
    status: created
    description: Thread/Message data model and Store interface specification
  - path: specs/010-chatkit-migration/quickstart.md
    status: created
    description: Step-by-step migration quick start guide
  - path: specs/010-chatkit-migration/contracts/backend.md
    status: created
    description: Backend API contracts for ChatKit SSE endpoint
  - path: specs/010-chatkit-migration/contracts/frontend.md
    status: created
    description: Frontend ChatKit React integration contracts
  - path: CLAUDE.md
    status: modified
    description: Added Python 3.13+, TypeScript 5+, and Neon PostgreSQL to active technologies
tests:
  - type: architecture-validation
    coverage: All constitution principles validated with pass/fail status
  - type: feasibility-check
    coverage: ChatKit + Gemini compatibility confirmed via official documentation
---

## Prompt

/sp.plan with comprehensive requirements to plan the migration of a custom chat system to ChatKit while maintaining Gemini as the LLM provider.

**Critical Requirements:**
- Plan migration of custom React chat UI (~600 LOC) to ChatKit React
- Remove WebSocket streaming and replace with SSE
- Remove custom WebSocket manager (~350 LOC backend)
- Implement self-hosted ChatKit integration (NOT OpenAI-hosted)
- Configure Gemini via OpenAI-compatible endpoint
- Preserve all 7 MCP tools functionality
- Maintain existing JWT authentication (httpOnly cookies)

**Documentation Requirements:**
- Research ChatKit React, ChatKit Python, OpenAI Agents SDK official docs
- Validate Gemini OpenAI compatibility endpoint
- Confirm self-hosted ChatKit pattern supports custom base_url
- Design data model with Thread/Message entities
- Create API contracts for backend and frontend
- Generate quickstart migration guide

**Deliverables:**
- research.md: Technical feasibility analysis
- data-model.md: Thread/Message schema and Store interface
- contracts/: Backend and frontend API specifications
- quickstart.md: Step-by-step migration guide
- plan.md: Complete implementation plan with architecture diagrams

**Explicit Prohibitions:**
- NO OpenAI-hosted workflows
- NO GPT-specific model assumptions
- NO OpenAI Actions (keep MCP tools)
- NO OpenAI-managed session storage

## Response snapshot

Created a comprehensive implementation plan for ChatKit migration with the following outputs:

**1. Research Findings (research.md):**
- ✅ ChatKit CAN work with Gemini via self-hosted integration
- ✅ Custom base_url fully supported by OpenAI SDK and Agents SDK
- ✅ SSE streaming replaces WebSocket (simpler, HTTP-native)
- ✅ No OpenAI Sessions API required for self-hosted mode
- ✅ All 7 MCP tools can be wrapped as Agents SDK functions
- ⚠️ Gemini OpenAI compatibility is "still in beta"

**Decision**: Use self-hosted ChatKit integration with custom AsyncOpenAI client pointing to Gemini's OpenAI-compatible endpoint.

**2. Data Model (data-model.md):**
- New `Thread` entity for ChatKit's conversation model
- Extended `Message` entity with `thread_id` foreign key and `tool_calls` JSONB
- PostgreSQL `Store` interface implementation requirements
- Database migration script for threads table

**3. Backend Contracts (contracts/backend.md):**
- `/api/chatkit` SSE endpoint specification
- `ChatKitServer` implementation pattern
- `PostgresChatKitStore` interface requirements
- Tool wrapping with `@function_tool` decorator
- Authentication via JWT cookies (custom fetch)

**4. Frontend Contracts (contracts/frontend.md):**
- `TaskChat.tsx` wrapper component (~50 LOC vs 600 LOC)
- `useChatKit` hook configuration with custom fetch
- Component deletion list (6 files removed)
- Theme customization via CSS variables

**5. Architecture Diagrams:**
- Current architecture showing WebSocket + custom components
- Target architecture showing SSE + ChatKit UI
- Clear separation of ChatKit responsibilities vs backend responsibilities

**6. Implementation Phases:**
- Phase 0: Research ✅ COMPLETE
- Phase 1: Design ✅ COMPLETE
- Phase 2: Backend implementation (ChatKitServer, Store, SSE endpoint)
- Phase 3: Frontend implementation (TaskChat wrapper, component deletion)
- Phase 4: Cleanup and documentation

**7. Constitution Validation:**
- All 10 applicable principles PASSED
- One noted modification: SSE instead of pure REST (justified for streaming)

**8. Quickstart Guide (quickstart.md):**
- Step-by-step setup for backend and frontend
- Database migration scripts
- Testing procedures
- Troubleshooting section
- Rollback plan

## Outcome

- ✅ Impact: Comprehensive implementation plan created with validated architecture for ChatKit + Gemini integration using self-hosted pattern
- 🧪 Tests: Architecture validation passed all constitution principles; feasibility check confirmed ChatKit + Gemini compatibility via official documentation
- 📁 Files:
  - specs/010-chatkit-migration/plan.md (created)
  - specs/010-chatkit-migration/research.md (created)
  - specs/010-chatkit-migration/data-model.md (created)
  - specs/010-chatkit-migration/quickstart.md (created)
  - specs/010-chatkit-migration/contracts/backend.md (created)
  - specs/010-chatkit-migration/contracts/frontend.md (created)
  - CLAUDE.md (modified - added Python 3.13+, TypeScript 5+, Neon PostgreSQL)
- 🔁 Next prompts: /sp.tasks to generate actionable task list from this plan
- 🧠 Reflection: Research phase was critical - confirmed that ChatKit's self-hosted integration is the ONLY viable path for Gemini usage. OpenAI-hosted integration would force GPT models. The Agents SDK's support for custom OpenAI clients is the key enabler. Main risk is Gemini's OpenAI compatibility being in beta, but this is mitigated by thorough testing and rollback plan.

## Evaluation notes (flywheel)

- Failure modes observed: None - all research, design, and documentation phases completed successfully
- Graders run and results (PASS/FAIL):
  - Constitution compliance: PASS (all 10 applicable principles)
  - Technical feasibility: PASS (ChatKit + Gemini confirmed compatible)
  - Documentation completeness: PASS (all required artifacts created)
  - Architecture clarity: PASS (diagrams and contracts unambiguous)
- Prompt variant: N/A
- Next experiment: During implementation, validate that ChatKit's SSE streaming works reliably with Gemini's OpenAI-compatible endpoint under load (concurrent users, long-running conversations)
