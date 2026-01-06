# Feature Specification: MCP Server for SpecifyPlus Prompts

**Feature Branch**: `002-mcp-server-prompts`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "We have specifyplus commands on @.claude/commands/** Each command takes user input and updates its prompt variable before sending it to the agent. Now you will use your mcp builder skill and create an mcp server where these commands are available as prompts. Goal: Now we can run this MCP server and connect with any agent and IDE"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Access SpecifyPlus Commands via MCP (Priority: P1)

A developer wants to use SpecifyPlus commands (like specification creation, planning, task generation) directly from their IDE or any MCP-compatible agent without switching to a terminal or running CLI commands.

**Why this priority**: This is the core functionality - making prompts available via MCP enables all other use cases and provides immediate value by integrating workflows into existing development environments.

**Independent Test**: Can be fully tested by starting the MCP server, connecting an MCP client, listing available prompts, and invoking one prompt to verify it returns the correct template.

**Acceptance Scenarios**:

1. **Given** the MCP server is running, **When** a client connects and lists available resources/prompts, **Then** all SpecifyPlus command files are discovered and exposed with their descriptions
2. **Given** a prompt is selected from the MCP server, **When** the client invokes it with arguments, **Then** the server returns the complete prompt content with the `$ARGUMENTS` placeholder replaced with the provided arguments
3. **Given** a prompt contains variable substitutions, **When** the prompt is invoked, **Then** all substitutions are correctly applied before returning the content

---

### User Story 2 - Dynamic Prompt Discovery and Updates (Priority: P2)

A developer adds a new SpecifyPlus command file to `.claude/commands/` and wants it immediately available to MCP clients without restarting the server or manual configuration.

**Why this priority**: Hot-reloading prompts improves developer experience and reduces friction when iterating on command definitions. Not critical for MVP but valuable for active development.

**Independent Test**: Can be tested by adding a new command file while the server is running, then listing prompts again to verify the new command appears without restart.

**Acceptance Scenarios**:

1. **Given** the MCP server is running, **When** a new command file is added to `.claude/commands/`, **Then** the next prompt list request includes the new command
2. **Given** an existing command file is modified, **When** the prompt is requested, **Then** the updated content is returned
3. **Given** a command file is deleted, **When** prompts are listed, **Then** the deleted command no longer appears

---

### User Story 3 - IDE Integration for Workflow Automation (Priority: P3)

A developer uses their IDE's MCP integration to trigger SpecifyPlus workflows (e.g., create spec from selection, generate tasks from spec) directly from the editor with context from the current file.

**Why this priority**: This represents the full vision of seamless IDE integration but builds on top of P1 and P2 functionality. Lower priority because the MCP server enables this, but specific IDE integrations can be developed incrementally.

**Independent Test**: Can be tested by connecting from an MCP-enabled IDE, invoking a prompt with selected text as arguments, and verifying the workflow executes correctly.

**Acceptance Scenarios**:

1. **Given** text is selected in an IDE, **When** the user invokes a SpecifyPlus prompt via MCP, **Then** the selected text is passed as arguments and the prompt content is returned
2. **Given** an IDE with multiple open files, **When** a prompt is invoked, **Then** the server maintains context isolation between different invocations
3. **Given** a workflow completes, **When** the prompt generates a file or output, **Then** the IDE receives notification of the result

---

### Edge Cases

- What happens when a command file is malformed or missing required frontmatter (description, handoffs)?
- How does the server handle concurrent requests for the same prompt from different clients?
- What happens when `$ARGUMENTS` is empty or contains special characters that need escaping?
- How does the server handle deeply nested directory structures in `.claude/commands/`?
- What happens when a command file exceeds size limits or contains circular references?
- How does the server handle encoding issues or non-UTF-8 characters in command files?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose all SpecifyPlus command files from `.claude/commands/` directory as MCP prompts
- **FR-002**: System MUST parse command file frontmatter (YAML) to extract metadata including descriptions and handoff information
- **FR-003**: System MUST support prompt invocation with user arguments that replace `$ARGUMENTS` placeholders in command content
- **FR-004**: System MUST return complete prompt content including both frontmatter and body sections when a prompt is invoked
- **FR-005**: System MUST provide a list operation that enumerates all available prompts with their names and descriptions
- **FR-006**: System MUST handle file system errors gracefully (missing files, permission errors, corrupted files)
- **FR-007**: System MUST support hot-reloading of command files without server restart
- **FR-008**: System MUST validate command files have required frontmatter fields before exposing them as prompts
- **FR-009**: System MUST escape or sanitize user arguments to prevent injection attacks in prompt content
- **FR-010**: System MUST maintain prompt versioning or modification timestamps for cache invalidation

### Key Entities

- **MCP Prompt**: A named resource consisting of command file frontmatter (metadata) and body (prompt template), uniquely identified by filename
- **Command File**: A markdown file in `.claude/commands/` with YAML frontmatter containing description, handoffs, and prompt template
- **Prompt Arguments**: User-provided text that replaces `$ARGUMENTS` placeholders in the prompt template
- **Prompt Metadata**: Frontmatter fields including description, handoff agents, and send flags that describe how prompts should be used

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can discover and invoke all SpecifyPlus commands through any MCP-compatible client within 10 seconds of server startup
- **SC-002**: Prompt invocation completes in under 500ms for files up to 100KB in size
- **SC-003**: Server supports at least 10 concurrent prompt invocations without performance degradation
- **SC-004**: 95% of command file additions or modifications are reflected in prompt listings within 2 seconds without server restart
- **SC-005**: Server successfully handles malformed command files by logging errors without crashing or affecting other prompts
- **SC-006**: All existing SpecifyPlus commands (currently 13 files) are successfully exposed and invocable via MCP

## Assumptions

1. The MCP protocol implementation follows the Model Context Protocol standard for prompt resources
2. Command files use standard YAML frontmatter format as shown in existing SpecifyPlus commands
3. The `.claude/commands/` directory is located relative to the project root where the server runs
4. Clients connecting to the MCP server understand how to handle prompt responses and process arguments
5. Hot-reloading uses file system watchers rather than polling for efficiency
6. Server runs as a local development tool and does not require authentication or multi-user isolation
7. Command files do not change structure during runtime (no schema migrations required)
