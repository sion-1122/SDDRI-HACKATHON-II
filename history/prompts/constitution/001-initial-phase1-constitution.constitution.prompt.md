---
id: 001
title: Initial Phase 1 CLI App Constitution
stage: constitution
date: 2026-01-02
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: todo-list-hackathon
command: /sp.constitution
labels: ["constitution","phase1","cli","tui","repl"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - history/prompts/constitution/001-initial-phase1-constitution.constitution.prompt.md
tests:
  - None (constitution update)
---

## Prompt

This project is a hackathon that is broke down into 5 phases

Here are the phase description

Phase I
In-Memory Python Console App
Python, Claude Code, Spec-Kit Plus

Phase II
Full-Stack Web Application
Next.js, FastAPI, SQLModel, Neon DB

Phase III
AI-Powered Todo Chatbot
OpenAI ChatKit, Agents SDK, Official MCP SDK

Phase IV
Local Kubernetes Deployment
Docker, Minikube, Helm, kubectl-ai, kagent

Phase V
Advanced Cloud Deployment
Kafka, Dapr, DigitalOcean DOKS


We'll increment phase based constitution rules as we go through them

right we'll right the first version of our constitution

Phase 1: CLI App
In our phase we need to create a cli based in memory REPL todo list app using python and respect TUI libraries.

We are not going to implement persistence, db, memory, everything will be saved in memory.

You're allowed to use base python libraries and libraries used to create beautiful TUI ( Terminal UI )

Key deliverable: Key deliverable is a python script that we can run using uv run main.py or similar command that spins up a REPL / Loop

Here are user stories:

When user starts the script the user get's greated and get's shown a list of action. The list is browsable using arrow keys and user can select them and press enter to submit the selected action

These are the required actions:
1. Add
2. List
3. delete
4. Edit
5. exit

in each of these action's other than add, user will be shown the list of their added tasks.
in the list format, user can browse through them using arrow keys and use space bar to toggle there completion status.

in the add action user is prompted to add task description that its get's saved to the user's task list.

We're not adding auth or multiple user's just simple implementation.

After completing every action user get's back to the initial menu with the same actions

## Response snapshot

Created initial constitution (v1.0.0) for Phase 1 of the Todo List Hackathon project.

**Five Core Principles Established:**
1. **In-Memory Execution** (Non-Negotiable): All state in memory, no persistence in Phase 1
2. **Terminal UI Excellence**: Beautiful TUI with keyboard-driven navigation (arrows, space, enter)
3. **REPL Architecture**: Continuous loop returning to main menu after every action
4. **Single User, Single Session**: No auth or multi-user complexity in Phase 1
5. **Incremental Phase Evolution**: Constitution will be amended for phases II-V

**Phase 1 Constraints Defined:**
- Technology: Python 3.13+, TUI libraries (textual/rich/curses), uv package management
- Required Features: Add, List, Delete, Edit, Exit tasks
- Interaction: Arrow key navigation, space bar toggling, enter for submission
- Out of Scope: Persistence, auth, task metadata, networking, web/GUI

**Development Workflow Standards:**
- PEP 8 compliance, type hints, docstrings
- Testing: Unit + integration tests, 70%+ coverage target
- Acceptance: `uv run main.py` execution, <100ms TUI response

**Governance Framework:**
- Amendment process with documentation and versioning
- Phase transition guidelines for adding persistence/web APIs in Phase 2

Constitution saved to `.specify/memory/constitution.md` with sync impact report.

## Outcome

- ✅ Impact: Established foundational governance document for Phase 1 CLI app development
- 🧪 Tests: None (constitution creation)
- 📁 Files: Constitution document created with 5 principles and comprehensive Phase 1 constraints
- 🔁 Next prompts: Consider running `/sp.specify` to create feature specification for CLI todo app
- 🧠 Reflection: Successfully captured all user requirements into testable principles; ready for spec phase

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create feature specification to elaborate user stories with acceptance criteria
