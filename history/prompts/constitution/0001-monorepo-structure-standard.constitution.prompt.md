---
id: 0001
title: monorepo-structure-standard
stage: constitution
date: 2026-01-06
surface: claude-code
model: claude-sonnet-4-5
feature: none
branch: 001-todo-cli-tui
user: groww
command: /sp.constitution
labels: [constitution, monorepo, structure]
links:
  spec: N/A
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - .specify/memory/constitution.md
  - .specify/templates/plan-template.md
  - .specify/templates/tasks-template.md
tests: []
---

## Prompt

User Input:
```
hackathon-todo/
├── .spec-kit/                    # Spec-Kit configuration
│   └── config.yaml
├── specs/                        # Spec-Kit managed specifications
│   ├── overview.md               # Project overview
│   ├── architecture.md           # System architecture
│   ├── features/                 # Feature specifications
│   │   ├── task-crud.md
│   │   ├── authentication.md
│   │   └── chatbot.md
│   ├── api/                      # API specifications
│   │   ├── rest-endpoints.md
│   │   └── mcp-tools.md
│   ├── database/                 # Database specifications
│   │   └── schema.md
│   └── ui/                       # UI specifications
│       ├── components.md
│       └── pages.md
├── CLAUDE.md                     # Root Claude Code instructions
├── frontend/
│   ├── CLAUDE.md
│   └── ... (Next.js app)
├── backend/
│   ├── CLAUDE.md
│   └── ... (FastAPI app)
├── docker-compose.yml
└── README.md
 enfore this type of monorepo folder structure.
```

[Full constitution skill prompt - see /sp.constitude command definition for complete workflow]

## Response snapshot

Successfully updated the project constitution from v1.0.0 to v1.1.0 by adding Principle VI: Monorepo Structure Standard.

**Key Changes**:
- Added new principle (VI) enforcing standardized monorepo folder structure across all phases
- Defined required structure with specs/ hierarchy (features/, api/, database/, ui/)
- Specified application directories (cli/, backend/, frontend/) with phase-appropriate usage
- Added structure enforcement rules covering specs hierarchy, CLAUDE.md inheritance, and phase compliance
- Updated plan-template.md to reference Principle VI and provide phase-appropriate structure options
- Updated tasks-template.md path conventions section to reference monorepo standard

**Version Rationale**: MINOR bump (1.0.0 → 1.1.0) - New principle added without breaking backward compatibility

**Updated Files**:
- .specify/memory/constitution.md (v1.1.0)
- .specify/templates/plan-template.md
- .specify/templates/tasks-template.md

**Follow-up TODOs**:
- Create .spec-kit/ directory structure if not exists
- Create specs/ subdirectories (features/, api/, database/, ui/) if not exists
- Consider creating frontend/ and backend/ directories for future phases

## Outcome

- ✅ Impact: Constitution now enforces monorepo structure standard as project-wide non-negotiable principle
- 🧪 Tests: N/A (constitution update)
- 📁 Files: 3 files updated (constitution.md, plan-template.md, tasks-template.md)
- 🔁 Next prompts: User should verify directory structure aligns with new principle; may need to create missing directories
- 🧠 Reflection: Successfully integrated monorepo governance into constitution without breaking existing Phase 1 principles. Template updates ensure future specs/plans/tasks reference the new standard.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor if plan/tasks generation correctly applies monorepo structure principle; may need to strengthen template language if violations occur
