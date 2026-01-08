---
id: "0002"
title: "mcp server plan"
stage: "plan"
date: "2026-01-06T17:30:00Z"
surface: "claude"
model: "claude-sonnet-4-5-20250929"
feature: "002-mcp-server-prompts"
branch: "002-mcp-server-prompts"
user: "groww"
command: "/sp.plan"
labels: ["mcp", "fastmcp", "specifyplus", "prompts", "python"]
links:
  spec: "../specs/002-mcp-server-prompts/spec.md"
  ticket: ""
  adr: ""
  pr: ""
files:
  - path: "specs/002-mcp-server-prompts/plan.md"
    status: "created"
    description: "Implementation plan with technical context, constitution check, and architecture"
  - path: "specs/002-mcp-server-prompts/research.md"
    status: "created"
    description: "Phase 0 research findings on FastMCP, MCP protocol, and technical decisions"
  - path: "specs/002-mcp-server-prompts/data-model.md"
    status: "created"
    description: "Phase 1 data model with Pydantic schemas for Prompt, PromptMetadata, etc."
  - path: "specs/002-mcp-server-prompts/contracts/mcp-prompts-schema.yaml"
    status: "created"
    description: "Phase 1 MCP protocol schemas for prompts/list, prompts/get, notifications"
  - path: "specs/002-mcp-server-prompts/quickstart.md"
    status: "created"
    description: "Phase 1 quickstart guide with installation, testing, and troubleshooting"
  - path: "CLAUDE.md"
    status: "modified"
    description: "Added FastMCP and MCP server technologies to active technologies list"
tests:
  - status: "pending"
    path: ""
    description: "Tests will be created during implementation phase (/sp.implement)"
---

## Prompt

User invoked `/sp.plan` command for feature 002-mcp-server-prompts with the following input:

"002-mcp-server-prompts use the mcp-builder skill."

The command execution workflow required:
1. Running setup-plan.sh script to initialize plan.md template
2. Loading FEATURE_SPEC and constitution.md
3. Filling Technical Context section with technology choices
4. Completing Constitution Check to verify compliance
5. Phase 0: Generating research.md with technical decisions
6. Phase 1: Generating data-model.md, contracts/, and quickstart.md
7. Updating agent context files via update-agent-context.sh
8. Creating PHR record

Key requirements:
- Use FastMCP framework for MCP server implementation
- Expose .claude/commands/ files as MCP prompt resources
- Support hot-reloading for dynamic prompt discovery
- Use Python 3.13+ with watchfiles and python-frontmatter
- Ensure stdio transport for local development
- Handle malformed YAML gracefully
- Support argument substitution with $ARGUMENTS placeholder

## Response snapshot

Successfully completed planning phase for MCP server feature:

1. **plan.md**: Comprehensive implementation plan created with:
   - Technical context: Python 3.13+, FastMCP, Pydantic, watchfiles
   - Constitution check: All applicable principles pass (I, IV, VI)
   - Architecture: 4 components (loader, watcher, server, models)
   - Project structure: mcp-servers/specifyplus-prompts/ directory
   - Technology decisions: FastMCP 2.x, python-frontmatter, watchfiles

2. **research.md**: Phase 0 research completed with 5 key decisions:
   - FastMCP 2.x fully supports @mcp.prompt decorator
   - MCP prompt protocol provides built-in listChanged capability
   - python-frontmatter library for YAML parsing
   - watchfiles with 2-second debounce for hot-reload
   - Minimal argument sanitization (length limits only)

3. **data-model.md**: Phase 1 data model defined with 4 Pydantic entities:
   - PromptMetadata: YAML frontmatter fields
   - Prompt: Complete command with metadata and template
   - PromptInvocationRequest: MCP request with arguments
   - PromptInvocationResponse: MCP response with messages

4. **contracts/mcp-prompts-schema.yaml**: Phase 1 MCP protocol schemas:
   - prompts/list request/response
   - prompts/get request/response
   - notifications/prompts/list_changed
   - Error response schemas
   - Example flows

5. **quickstart.md**: Phase 1 user guide with:
   - Installation instructions (uv sync)
   - Server startup (stdio and HTTP transports)
   - MCP Inspector testing
   - IDE integration (VSCode, Cursor)
   - Troubleshooting common issues
   - Security considerations

6. **Agent context updated**: CLAUDE.md modified to include:
   - Python 3.13+ with FastMCP framework
   - FastMCP, Pydantic, watchfiles dependencies
   - File system storage (reads .claude/commands/)

## Outcome

- ✅ Impact: Planning phase complete, all design artifacts generated. Ready for implementation phase (/sp.implement or /sp.tasks).
- 🧪 Tests: Tests will be created during implementation. Plan includes pytest with pytest-asyncio for async handler testing, integration tests with MCP client, manual testing with MCP Inspector.
- 📁 Files: Created 5 documentation files (plan.md, research.md, data-model.md, contracts/mcp-prompts-schema.yaml, quickstart.md), modified 1 file (CLAUDE.md).
- 🔁 Next prompts: Run `/sp.tasks` to generate actionable task list, or `/sp.implement` to begin implementation.
- 🧠 Reflection: Planning proceeded smoothly. Research confirmed FastMCP 2.x has native prompt support, eliminating the need for workaround implementation. Constitution check passed with conditional approval (need to add mcp-servers/ directory to Principle VI). All technical decisions are well-supported by documentation and community best practices.

## Evaluation notes (flywheel)

- Failure modes observed: None during planning phase.
- Graders run and results (PASS/FAIL): N/A (implementation not started).
- Prompt variant (if applicable): Standard /sp.plan workflow.
- Next experiment (smallest change to try): Implement minimal viable server with @mcp.prompt decorator and test with MCP Inspector to validate FastMCP prompt resource support before building full hot-reload functionality.
