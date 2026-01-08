---
id: 0002
title: phase-ii-constitution-update
stage: constitution
date: 2026-01-08
surface: claude
model: claude-sonnet-4-5-20250929
feature: none
branch: 002-mcp-server-prompts
user: developer
command: /sp.constitution
labels: [constitution, phase-ii, full-stack]
links:
  spec: N/A
  ticket: N/A
  adr: N/A
  pr: N/A
files:
- path: .specify/memory/constitution.md
  action: updated
  reason: "Amended constitution from version 1.1.0 to 2.0.0 for Phase II full-stack web application"
tests: []
---

## Prompt

We are starting Phase II: Todo Full-Stack Web Application.

Follow Spec-Driven Development strictly:
Specify → Plan → Tasks → Implement.
No code may be written until Tasks are approved.

Context:
- This project is a monorepo using Spec-Kit Plus and Claude Code.
- Specs live under /specs and must follow Spec-Kit conventions.
- Claude must read and respect:
  - Root CLAUDE.md
  - frontend/CLAUDE.md
  - backend/CLAUDE.md

Objective:
Create a multi-user todo app  web application with authentication and persistent storage.

Phase II Requirements:
- Implement all 5 basic todo features as a web app:
  - Add Task
  - View Tasks
  - Update Task
  - Delete Task
  - Toggle Completion
- Create RESTful API endpoints using FastAPI
- Build responsive frontend using Next.js App Router
- Store data in Neon Serverless PostgreSQL using SQLModel
- Implement authentication using Better Auth on frontend
- Secure backend using JWT verification

Auth Architecture:
- Better Auth runs on the Next.js frontend
- JWT tokens are issued on login
- Frontend sends JWT via Authorization: Bearer <token>
- FastAPI backend verifies JWT using shared secret
- Backend extracts user_id from JWT and enforces ownership
- All task queries must be filtered by authenticated user

Shared Secret:
- Use environment variable BETTER_AUTH_SECRET
- Same value must be used by frontend and backend

API Requirements:
- All routes under /api
- All routes require valid JWT
- Requests without JWT return 401
- User can only access their own tasks

Suggested Specs to structure:
1. /specs/overview.md
2. /specs/features/task-crud.md
3. /specs/features/authentication.md
4. /specs/api/rest-endpoints.md
5. /specs/database/schema.md
6. /specs/ui/pages.md
7. /specs/ui/components.md

Output for this step:
- constitution updated for Phase II
- constitution describing full-stack architecture
- NO code generation yet

If anything is missing or ambiguous, stop and request clarification instead of guessing.

## Response snapshot

Successfully updated the constitution from version 1.1.0 to 2.0.0 (MAJOR version bump) to govern Phase II of the Todo Full-Stack Web Application.

**Key Changes:**

**Modified Principles:**
- Principle I: "In-Memory Execution (Phase 1)" → "Persistent Storage (Phase II)" - All state must be persisted in Neon Serverless PostgreSQL using SQLModel
- Principle IV: "Single User, Single Session" → "Multi-User Architecture with Authentication" - Multi-user semantics with JWT authentication

**New Principles Added:**
- Principle VII: Authentication & JWT Security - JWT-based auth with shared BETTER_AUTH_SECRET
- Principle VIII: Frontend Architecture (Next.js) - Next.js App Router with React Server Components
- Principle IX: Data Ownership & Isolation - All queries scoped to authenticated user_id
- Principle X: API Response Consistency - Standardized JSON responses with error handling

**Technology Stack Defined:**
- Backend: Python 3.13+ with FastAPI, SQLModel, Pydantic
- Frontend: Next.js 15+ with App Router, React 19+, TypeScript
- Authentication: Better Auth with JWT
- Database: Neon Serverless PostgreSQL

**Security Requirements:**
- All /api endpoints require valid JWT
- User passwords hashed by Better Auth
- SQL injection prevention via SQLModel
- XSS prevention via React escaping
- CSRF protection via SameSite cookies

**Legacy Preservation:**
Phase I principles preserved in "Phase I Legacy" section for historical reference.

**Infrastructure Created:**
- Created spec subdirectories: /specs/features, /specs/api, /specs/database, /specs/ui

**Version Information:**
- Version: 2.0.0
- Ratified: 2026-01-02
- Last Amended: 2026-01-08

## Outcome

- ✅ Impact: Constitution amended to version 2.0.0 establishing Phase II governance with 10 core principles covering persistent storage, RESTful API, responsive UI, multi-user auth, JWT security, data ownership, and monorepo structure
- 🧪 Tests: N/A (constitution update, no code changes)
- 📁 Files: Updated .specify/memory/constitution.md; created /specs subdirectories (features/, api/, database/, ui/)
- 🔁 Next prompts: Run /sp.specify to create feature specifications for Phase II (task-crud, authentication)
- 🧠 Reflection: MAJOR version bump appropriate due to backward-incompatible architectural changes (in-memory → persistent storage, single-user → multi-user, CLI → full-stack web). Phase I principles preserved as legacy for reference. Constitution now provides comprehensive governance for full-stack development with clear security requirements and data isolation rules.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
