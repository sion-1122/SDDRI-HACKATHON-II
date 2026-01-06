# Implementation Plan: MCP Server for SpecifyPlus Prompts

**Branch**: `002-mcp-server-prompts` | **Date**: 2026-01-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-mcp-server-prompts/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a Model Context Protocol (MCP) server that exposes SpecifyPlus command files from `.claude/commands/` as MCP prompt resources. The server will enable any MCP-compatible client (IDEs, agents, tools) to discover and invoke SpecifyPlus workflows (spec creation, planning, task generation, etc.) without requiring terminal access or CLI execution. The server uses FastMCP (Python) for rapid development, implements hot-reloading for dynamic prompt discovery, and supports stdio transport for local development with potential for HTTP transport in future iterations.

## Technical Context

**Language/Version**: Python 3.13+ with FastMCP framework
**Primary Dependencies**: FastMCP (MCP server framework), Pydantic (schema validation), watchfiles (file system watching)
**Storage**: File system (reads `.claude/commands/` directory, no write operations)
**Testing**: pytest with pytest-asyncio for async MCP handler testing
**Target Platform**: Local development server (stdio transport), Linux/macOS/Windows compatible
**Project Type**: cli (MCP server as CLI tool)
**Performance Goals**: <500ms prompt invocation response time, <2s hot-reload detection, support 10+ concurrent clients
**Constraints**: No authentication (local dev tool), read-only file access, must handle malformed YAML gracefully
**Scale/Scope**: 13+ existing command files, supports nested directory structures, files up to 100KB

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Analysis

**Principle I (In-Memory Execution)**: ✅ PASS
- MCP server maintains prompts in memory during runtime
- No persistence layer required (reads from files on demand)
- Prompt cache invalidated on file changes (hot-reload)

**Principle II (Terminal UI Excellence)**: ⚠️ NOT APPLICABLE
- This is a backend service (MCP server), not a TUI application
- No UI component - exposes API via MCP protocol
- Justification: Feature 002 is infrastructure/tooling, not user-facing CLI

**Principle III (REPL Architecture)**: ⚠️ NOT APPLICABLE
- MCP server uses request/response pattern, not REPL
- Justification: MCP protocol is stateless server model, different from REPL architecture

**Principle IV (Single User, Single Session)**: ✅ PASS
- Local development tool assumes single user context
- No authentication/multi-user isolation (assumption #6 from spec)
- Concurrent requests supported but no user separation required

**Principle V (Incremental Phase Evolution)**: ✅ PASS
- This is feature 002 (tooling enhancement), not Phase 1/2/3
- Constitution Phase 1 constraints apply to CLI TUI app (feature 001)
- This MCP server is separate infrastructure

**Principle VI (Monorepo Structure Standard)**: ✅ PASS (conditional)
- MCP server code will be placed in `mcp-servers/` directory at repo root
- NEW directory structure required (addition to monorepo)
- Complies with standardized layout while extending it for MCP infrastructure

### Gate Decision: ✅ PROCEED WITH CONDITIONS

**Required Amendment**: Add `mcp-servers/` directory to Principle VI structure definition as permitted extension for tooling infrastructure.

**No Complexity Tracking Required**: No constitution violations - feature is compliant with applicable principles.

## Project Structure

### Documentation (this feature)

```text
specs/002-mcp-server-prompts/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── mcp-prompts-schema.yaml  # MCP prompt resource schema
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
mcp-servers/
├── specifyplus-prompts/         # MCP server for SpecifyPlus commands
│   ├── README.md                # Server documentation and usage
│   ├── pyproject.toml           # Python project configuration
│   ├── src/
│   │   └── specifyplus_prompts/
│   │       ├── __init__.py      # Package initialization
│   │       ├── server.py        # MCP server entry point
│   │       ├── prompt_loader.py # Command file parsing and caching
│   │       ├── file_watcher.py  # Hot-reload file system watcher
│   │       └── models.py        # Pydantic schemas for prompts/metadata
│   └── tests/
│       ├── test_prompt_loader.py    # Unit tests for file parsing
│       ├── test_file_watcher.py     # Unit tests for hot-reload
│       └── test_server_integration.py # Integration tests with MCP client
│
└── README.md                    # MCP servers overview (if multiple servers)

# Existing structure unchanged
.claude/
├── commands/                    # Source of prompt definitions
│   ├── sp.specify.md
│   ├── sp.plan.md
│   └── ... (13 command files)
```

**Structure Decision**: Option 1 (CLI/TUI application) adapted for MCP server. The `mcp-servers/` directory extends the monorepo structure (Principle VI) to house MCP infrastructure alongside `cli/`, `backend/`, and `frontend/` directories. This aligns with Spec-Kit tooling philosophy and maintains separation of concerns. Server code is organized into clear modules: loader (file parsing), watcher (hot-reload), and server (MCP protocol).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No violations | N/A |

---

## Phase 0: Research & Technical Decisions

### Research Tasks

1. **FastMCP Framework Capabilities**
   - Document FastMCP's prompt resource API (not just tools)
   - Research prompt registration patterns and metadata support
   - Investigate built-in file watching/hot-reload capabilities
   - Evaluate stdio vs transport flexibility for future HTTP support

2. **MCP Prompt Resource Specification**
   - Study MCP prompt resource protocol (vs tools/resources)
   - Understand prompt argument passing and template substitution
   - Document prompt metadata standards (descriptions, annotations)
   - Research prompt discovery and enumeration protocols

3. **YAML Frontmatter Parsing Best Practices**
   - Evaluate python-frontmatter vs custom yaml.markdown parsing
   - Test error handling for malformed YAML in existing commands
   - Document required vs optional frontmatter fields
   - Research encoding handling for non-UTF-8 files

4. **File System Watching Strategies**
   - Compare watchfiles vs watchdog for cross-platform support
   - Test debounce strategies for rapid file changes
   - Research performance impact with 13+ files and nested directories
   - Document graceful degradation if watching fails

5. **Argument Sanitization & Security**
   - Research prompt injection attack vectors
   - Document best practices for `$ARGUMENTS` substitution
   - Test special character handling (newlines, quotes, markdown)
   - Evaluate output encoding strategies

### Research Output

See `research.md` for detailed findings and decisions.

---

## Phase 1: Design Artifacts

### Data Model

See `data-model.md` for entity definitions, relationships, and validation rules.

### API Contracts

See `contracts/mcp-prompts-schema.yaml` for:
- MCP prompt resource definitions
- Prompt invocation request/response schemas
- Error response formats
- Metadata structure

### Quickstart Guide

See `quickstart.md` for:
- Server installation and startup
- MCP client configuration examples
- Testing prompts with MCP Inspector
- Troubleshooting common issues

---

## Phase 2: Architecture & Components

### Component Overview

**Prompt Loader (`prompt_loader.py`)**
- Scans `.claude/commands/` directory for `.md` files
- Parses YAML frontmatter and markdown body
- Validates required fields (description, etc.)
- Maintains in-memory cache with modification timestamps
- Provides prompt lookup by name
- Returns formatted prompt content with `$ARGUMENTS` substitution

**File Watcher (`file_watcher.py`)**
- Monitors `.claude/commands/` for create/modify/delete events
- Debounces rapid changes (2s window)
- Triggers cache invalidation on detected changes
- Logs file system errors without crashing
- Gracefully degrades if watching unavailable

**MCP Server (`server.py`)**
- Initializes FastMCP server with stdio transport
- Registers prompt resources from loader
- Handles MCP prompt listing requests
- Handles MCP prompt invocation requests
- Performs argument sanitization
- Returns errors with actionable messages

**Data Models (`models.py`)**
- `PromptMetadata`: Frontmatter fields (description, handoffs, send flag)
- `Prompt`: Complete prompt with metadata, template, file path, timestamp
- `PromptInvocationRequest`: Arguments and prompt name
- `PromptInvocationResponse`: Formatted content or error

### Technology Stack Decisions

**Python 3.13+ with FastMCP**:
- Rapid development with decorators (`@mcp.prompt`)
- Built-in stdio transport handling
- Strong typing with Pydantic integration
- Excellent async support for concurrent requests
- Alignment with existing Python tooling in monorepo

**watchfiles for hot-reload**:
- Cross-platform file watching (Linux/macOS/Windows)
- Efficient Rust-based implementation
- Simple API for directory watching
- Better performance than polling

**python-frontmatter**:
- Specialized library for markdown + YAML parsing
- Handles edge cases (missing delimiters, malformed YAML)
- Preserves original markdown formatting
- Widely used and well-tested

### Error Handling Strategy

**Malformed Command Files**:
- Log error with file path and specific issue
- Skip file in prompt listings (don't expose broken prompts)
- Return partial listings if some files fail
- Example error: `"Failed to parse .claude/commands/sp.broken.md: Invalid YAML line 15"`

**Missing Required Fields**:
- Validate frontmatter has `description` field
- Log missing fields as warnings
- Skip prompts without required metadata
- Document validation rules in README

**File System Errors**:
- Catch permission errors, log, continue
- Handle missing directory gracefully (start with empty prompt list)
- Retry file watching on failure with exponential backoff
- Never crash due to file system issues

**Argument Sanitization**:
- Escape special markdown characters in arguments
- Handle empty arguments (return template unchanged)
- Truncate excessively long arguments (>10KB)
- Sanitize but preserve formatting (newlines, bullets)

### Security Considerations

**Argument Injection**:
- Replace `$ARGUMENTS` after markdown parsing (not in YAML)
- Escape HTML/LaTeX special characters if present
- Limit argument length to prevent DoS
- No code execution from arguments (text substitution only)

**File Access**:
- Read-only access to `.claude/commands/`
- No path traversal (validate paths stay within commands dir)
- No symbolic link following outside target directory
- Respect file system permissions

**Local Development Scope**:
- No network exposure (stdio transport only)
- No authentication (assumes trusted local environment)
- No multi-user isolation
- Logs all prompt invocations for debugging

---

## Implementation Notes

### Prompt Registration Pattern

```python
# Pseudo-code for FastMCP prompt registration
@mcp.prompt("sp.specify")
async def specify_prompt(arguments: str | None = None) -> str:
    """Create or update the feature specification from a natural language feature description."""
    prompt = loader.get_prompt("sp.specify")
    return prompt.format(arguments or "")

# Dynamic registration for all discovered prompts
for prompt_name in loader.list_prompts():
    metadata = loader.get_metadata(prompt_name)
    mcp.prompt(prompt_name)(create_prompt_handler(prompt_name))
```

### Hot-Reload Flow

1. File watcher detects change in `.claude/commands/`
2. Debounce for 2s to collect rapid changes
3. Invalidate cache for changed file(s)
4. Reload prompt metadata and content
5. Next MCP request sees updated content
6. Log reload event: `"Reloaded prompt sp.specify (modified)"`

### Testing Strategy

**Unit Tests**:
- Test YAML parsing with valid and malformed frontmatter
- Test argument substitution with special characters
- Test file watcher event detection and debouncing
- Test prompt loader caching and invalidation

**Integration Tests**:
- Start server with stdio transport
- Connect with test MCP client
- List prompts and verify all 13 commands appear
- Invoke prompt with arguments and verify output
- Modify command file, verify hot-reload updates prompt
- Test error handling with corrupted files

**Manual Testing**:
- Use MCP Inspector: `npx @modelcontextprotocol/inspector uv run src/specifyplus_prompts/server.py`
- Connect from VSCode MCP extension
- Verify prompt discovery and invocation from IDE

---

## Success Metrics

From spec success criteria:

- **SC-001**: Server starts and exposes prompts within 10s ✓ (lazy loading, cache on first request)
- **SC-002**: Prompt invocation <500ms ✓ (in-memory cache, minimal processing)
- **SC-003**: 10+ concurrent clients ✓ (async handlers, no shared state)
- **SC-004**: 95% hot-reload within 2s ✓ (watchfiles debounce 2s, immediate reload)
- **SC-005**: Malformed files handled gracefully ✓ (try/except, log and skip)
- **SC-006**: All 13 existing commands exposed ✓ (scan all .md files in directory)

---

## Open Questions for Phase 0 Research

1. Does FastMCP support prompt resources or only tools? (Affects implementation pattern)
2. How should we handle prompts with circular references or excessive size?
3. Should we support nested subdirectories in `.claude/commands/` or flatten structure?
4. What's the recommended way to expose prompt metadata (descriptions, handoffs) via MCP?

These will be resolved in `research.md`.
