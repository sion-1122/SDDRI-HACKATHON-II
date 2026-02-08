---
id: 0001
title: chatkit-migration-spec
stage: spec
date: 2026-02-06T12:50:00Z
surface: claude
model: glm-4.7
feature: 010-chatkit-migration
branch: 010-chatkit-migration
user: groww
command: /sp.specify
labels: [spec, chatkit, migration, gemini]
links:
  spec: ../specs/010-chatkit-migration/spec.md
  ticket:
  adr:
  pr:
files:
  - path: specs/010-chatkit-migration/spec.md
    status: created
    description: Feature specification for ChatKit migration with Gemini compatibility
  - path: specs/010-chatkit-migration/checklists/requirements.md
    status: created
    description: Quality validation checklist for specification
tests:
  - type: acceptance
    coverage: All user stories have acceptance scenarios defined
---

## Prompt

/sp.specify with detailed requirements to migrate custom chat system to ChatKit while maintaining Gemini as the LLM provider.

User provided comprehensive specification including:

**Non-Negotiable Constraints:**
- Gemini must remain the LLM (via OpenAI-compatible endpoint)
- OpenAI Agents SDK remains orchestrator
- ChatKit is UI and protocol only
- Single backend chat surface
- MCP tools remain unchanged

**Migration Goals:**
- Replace custom React chat UI with ChatKit React
- Remove WebSocket streaming and progress event plumbing
- Use ChatKit streaming and tool visualization
- Keep authentication, authorization, and rate limiting in FastAPI
- Preserve stateless backend execution model

**Target Architecture:**
- Frontend: ChatKit React component with useChatKit() hook
- Backend: /api/chatkit/session endpoint for session creation
- LLM: Gemini via OpenAI-compatible base_url

**Deletion Plan:**
- Custom chat UI components
- WebSocket connection manager
- Streaming event protocol
- Manual progress visualization
- LocalStorage conversation persistence

**Acceptance Criteria:**
- ChatKit UI renders and streams correctly
- Tools execute and visualize correctly
- Gemini confirmed as responding model
- No OpenAI model IDs in logs/config
- Conversation persistence functional
- No WebSocket code remains

## Response snapshot

Created feature specification for ChatKit migration with the following deliverables:

1. **Specification File** (specs/010-chatkit-migration/spec.md):
   - 3 prioritized user stories (P1: AI Chat with Task Management, P2: Cross-Tab Sync, P3: Error Resilience)
   - 15 functional requirements covering chat, tools, persistence, and migration requirements
   - 9 measurable success criteria with specific metrics (2s response time, 500ms tool visibility, 95% persistence, 600 LOC reduction)
   - 8 identified edge cases covering concurrency, session expiration, rate limits, and errors
   - Clear out-of-scope boundaries preventing scope creep

2. **Quality Checklist** (checklists/requirements.md):
   - All validation criteria PASSED
   - No [NEEDS CLARIFICATION] markers required
   - Requirements are testable and technology-agnostic
   - Ready for planning phase

3. **Branch Creation**:
   - Created branch: 010-chatkit-migration
   - Checked out to new branch
   - Spec file initialized at specs/010-chatkit-migration/spec.md

## Outcome

- ✅ Impact: Feature specification created for ChatKit migration, establishing clear requirements and success criteria while maintaining Gemini compatibility
- 🧪 Tests: All requirements are testable with defined acceptance scenarios and measurable success criteria
- 📁 Files:
  - specs/010-chatkit-migration/spec.md (created)
  - specs/010-chatkit-migration/checklists/requirements.md (created)
  - history/prompts/010-chatkit-migration/0001-chatkit-migration-spec.spec.prompt.md (created)
- 🔁 Next prompts: /sp.plan to create implementation architecture
- 🧠 Reflection: User provided very detailed requirements with clear constraints, making specification creation straightforward. No clarifications needed. Main risk documented is ChatKit's support for custom base URLs which needs validation in planning phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - script execution succeeded on second attempt (permission issue with first call)
- Graders run and results (PASS/FAIL): Quality checklist PASSED all criteria
- Prompt variant: N/A
- Next experiment: Validate in planning phase whether ChatKit actually supports custom OpenAI-compatible base URLs for Gemini integration
