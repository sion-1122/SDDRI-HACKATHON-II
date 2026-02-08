# Feature Specification: ChatKit Migration with Gemini Compatibility

**Feature Branch**: `010-chatkit-migration`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Migrate Custom Chat System to ChatKit (Gemini-Compatible)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Chat with Task Management (Priority: P1)

A user interacts with the AI chatbot to manage their todo tasks. They send natural language messages like "create a task to call mom tomorrow at 5pm" and receive intelligent responses. The system shows tool execution in real-time, persists conversation history, and maintains context across sessions.

**Why this priority**: This is the core value proposition of the AI assistant. Without this working, the migration has failed.

**Independent Test**: Can be fully tested by opening the chat interface, sending a task creation command, and verifying that (1) the response streams correctly, (2) the tool execution visualizes, and (3) the task appears in the user's task list.

**Acceptance Scenarios**:

1. **Given** a user is authenticated and on the dashboard, **When** they open the chat and send "create a task called buy groceries", **Then** the AI responds with confirmation and the task appears in their list
2. **Given** a user has an existing conversation, **When** they refresh the page and reopen chat, **Then** the conversation history is preserved and displayed
3. **Given** the AI is executing a tool, **When** the tool runs, **Then** the user sees real-time progress visualization of the tool execution
4. **Given** a user sends a malformed request, **When** the system cannot process it, **Then** an appropriate error message is displayed in the chat interface

---

### User Story 2 - Cross-Tab Chat Synchronization (Priority: P2)

A user has the application open in multiple browser tabs. When they send a message in one tab, the conversation state updates across all tabs simultaneously.

**Why this priority**: Improves UX for power users who work across multiple tabs/windows, but doesn't block core functionality.

**Independent Test**: Can be tested by opening the app in two tabs, sending a message in one tab, and verifying the conversation state updates in the other tab.

**Acceptance Scenarios**:

1. **Given** a user has two browser tabs open, **When** they send a chat message in tab A, **Then** tab B reflects the new message in conversation history
2. **Given** a user closes and reopens a tab, **When** the chat loads, **Then** it shows the latest conversation state

---

### User Story 3 - Error Resilience and Connection Status (Priority: P3)

A user experiences network interruptions or backend errors. The chat interface gracefully handles these scenarios, displays appropriate status indicators, and allows recovery when connectivity is restored.

**Why this priority**: Important for production reliability but can be addressed incrementally after core functionality works.

**Independent Test**: Can be tested by simulating network failures (Chrome DevTools offline mode) and verifying the interface shows connection status and recovers when network returns.

**Acceptance Scenarios**:

1. **Given** a user is chatting, **When** the network connection is lost, **Then** the interface shows a "disconnected" indicator
2. **Given** the interface shows "disconnected", **When** network connectivity returns, **Then** the interface reconnects automatically and resumes normal operation
3. **Given** a backend error occurs during chat, **When** the error happens, **Then** the user sees a friendly error message without the UI freezing

---

### Edge Cases

- What happens when the user sends a message while a previous message is still being processed?
- How does the system handle conversation state when the session expires?
- What happens if ChatKit session creation fails due to authentication issues?
- How does the system behave when the Gemini API rate limits are hit?
- What occurs if a tool execution times out during streaming?
- How does the system handle malformed responses from the LLM?
- What happens when the user has multiple concurrent conversations?
- How does the system behave if the ChatKit client secret expires mid-conversation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a chat interface that streams AI responses in real-time
- **FR-002**: System MUST visualize tool/function executions as they occur
- **FR-003**: System MUST persist conversation history across page refreshes
- **FR-004**: System MUST authenticate all chat requests using existing authentication mechanism
- **FR-005**: System MUST use Gemini as the LLM provider exclusively
- **FR-006**: System MUST execute task management tools (create, read, update, delete, complete)
- **FR-007**: System MUST maintain conversation context within a session
- **FR-008**: System MUST display connection status to the user
- **FR-009**: System MUST handle API errors gracefully without breaking the UI
- **FR-010**: System MUST support multiple concurrent tool executions
- **FR-011**: System MUST remove all WebSocket-related code from the codebase
- **FR-012**: System MUST NOT use any OpenAI-hosted models
- **FR-013**: System MUST keep all tool execution server-side
- **FR-014**: System MUST provide a session endpoint for ChatKit initialization
- **FR-015**: System MUST rate limit chat requests to prevent abuse

### Key Entities

- **Conversation**: A sequence of messages between a user and the AI, associated with a specific user account, containing the full message history and metadata
- **Message**: An individual text communication from either the user or the AI, including content, timestamp, role (user/assistant/system), and optional tool call attachments
- **Tool Execution**: A record of a tool/function invoked by the AI, including tool name, parameters, execution status, result, and timing information
- **Chat Session**: An authenticated session context for ChatKit that includes user identity, conversation state, and authorization credentials
- **Streaming Response**: A partial AI response that updates incrementally as content is generated, providing real-time feedback to the user

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can send a chat message and receive the first token of the AI response within 2 seconds
- **SC-002**: Tool execution status is visible to users within 500ms of the tool being invoked
- **SC-003**: 100% of tool executions complete using the Gemini LLM (no OpenAI models)
- **SC-004**: Zero WebSocket-related code remains in the codebase after migration
- **SC-005**: 95% of chat conversations persist correctly across page refreshes
- **SC-006**: The codebase has at least 600 fewer lines of code after removing custom UI components
- **SC-007**: All 7 task management tools (create, read, update, delete, complete, bulk-complete, bulk-delete) execute successfully through ChatKit
- **SC-008**: API error responses are handled gracefully without UI freezes 100% of the time
- **SC-009**: ChatKit session creation completes successfully for authenticated users within 1 second

## Out of Scope

- Migrating task management tools to OpenAI Actions format
- Switching from Gemini to any other LLM provider
- Using OpenAI-hosted models or workflows
- Redesigning the chat UI beyond ChatKit's native theming capabilities
- Modifying the task management data models or database schema
- Changing the authentication/authorization system
- Implementing multi-modal capabilities (image/file uploads via ChatKit)
- Creating custom ChatKit extensions or plugins

## Assumptions

- ChatKit React library supports custom base_url for OpenAI-compatible endpoints (Gemini)
- ChatKit session creation can be implemented server-side with FastAPI
- Existing MCP tools can continue operating without modification
- The Neon PostgreSQL database requires no schema changes
- Current authentication cookies (httpOnly) remain compatible with ChatKit flow
- Gemini's OpenAI-compatible endpoint supports streaming responses
- ChatKit's tool visualization format can accommodate custom tool schemas

## Dependencies

- ChatKit Python and JavaScript libraries must support custom OpenAI-compatible base URLs
- Gemini's OpenAI-compatible endpoint must support all required features (streaming, tool calling)
- Existing FastAPI backend must be able to create ChatKit-compatible sessions
- Frontend build system must support ChatKit React component integration

## Risks

- **Risk 1**: ChatKit may not fully support custom base URLs, forcing an architectural pivot
- **Risk 2**: Gemini's OpenAI-compatible endpoint may have limitations not present in native Gemini API
- **Risk 3**: ChatKit's tool visualization may not align with existing MCP tool schemas
- **Risk 4**: Session management between ChatKit and existing auth system may have incompatibilities
