# Data Model: MCP Server for SpecifyPlus Prompts

**Feature**: 002-mcp-server-prompts
**Date**: 2026-01-06
**Phase**: Phase 1 - Design Artifacts

## Overview

This document defines the data model for the MCP server that exposes SpecifyPlus command files as prompt resources. The model consists of four main entities: `PromptMetadata` (YAML frontmatter), `Prompt` (complete prompt with content), `PromptInvocationRequest` (MCP request), and `PromptInvocationResponse` (MCP response).

All entities use Pydantic for validation and serialization, ensuring type safety and automatic JSON schema generation for FastMCP integration.

---

## Entity Definitions

### 1. PromptMetadata

**Purpose**: Represents YAML frontmatter extracted from SpecifyPlus command files.

**Properties**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `description` | `str` | YES | Human-readable description of the command | "Create or update the feature specification" |
| `handoffs` | `list[Handoff]` | No | List of agent handoffs specified in frontmatter | `[{"agent": "sp.plan", "label": "Build Plan"}]` |
| `send` | `bool` | No | Whether to send prompt immediately to handoff agent | `true` |
| `raw_metadata` | `dict[str, Any]` | No | All frontmatter fields for forward compatibility | `{"description": "...", "custom_field": "value"}` |

**Validation Rules**:
- `description` must be non-empty string if present
- `handoffs` list must contain valid `Handoff` objects (see below)
- `send` defaults to `false` if not present

**Pydantic Model**:
```python
from pydantic import BaseModel, Field
from typing import Any

class Handoff(BaseModel):
    """Agent handoff configuration from frontmatter."""
    agent: str = Field(..., description="Target agent name (e.g., 'sp.plan')")
    label: str = Field(..., description="Human-readable label for the handoff")
    prompt: str | None = Field(None, description="Optional prompt template for handoff")
    send: bool = Field(False, description="Whether to send immediately")

class PromptMetadata(BaseModel):
    """YAML frontmatter from SpecifyPlus command files."""
    description: str = Field(..., description="Command description")
    handoffs: list[Handoff] = Field(default_factory=list, description="Agent handoffs")
    send: bool = Field(False, description="Send to handoff immediately")
    raw_metadata: dict[str, Any] = Field(default_factory=dict, description="All frontmatter fields")

    class Config:
        # Allow extra fields for forward compatibility
        extra = "ignore"
```

---

### 2. Prompt

**Purpose**: Represents a complete SpecifyPlus command with metadata, template content, and file information.

**Properties**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | `str` | YES | Unique prompt name (filename without extension) | `"sp.specify"` |
| `file_path` | `str` | YES | Absolute path to command file | `"/path/to/.claude/commands/sp.specify.md"` |
| `metadata` | `PromptMetadata` | YES | Parsed YAML frontmatter | `PromptMetadata(...)` |
| `template` | `str` | YES | Markdown body with `$ARGUMENTS` placeholder | `"## User Input\n\n$ARGUMENTS\n..."` |
| `modified_at` | `datetime` | YES | File modification timestamp | `datetime(2026, 1, 6, 12, 0, 0)` |
| `size_bytes` | `int` | YES | File size in bytes | `7543` |

**Methods**:

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `format(arguments: str)` | `arguments: str` | `str` | Returns template with `$ARGUMENTS` replaced |
| `is_stale()` | - | `bool` | Checks if file was modified since load |
| `reload()` | - | `Prompt` | Reloads prompt from file |

**Validation Rules**:
- `name` must be non-empty and contain only valid filename characters
- `template` must contain at least one `$ARGUMENTS` placeholder (warning if missing)
- `size_bytes` must be ≤ 100,000 (100KB limit)
- `modified_at` must be in the past (not future timestamps)

**Pydantic Model**:
```python
from datetime import datetime
from pathlib import Path

class Prompt(BaseModel):
    """Complete SpecifyPlus command prompt."""
    name: str = Field(..., description="Prompt name (filename without extension)")
    file_path: str = Field(..., description="Absolute path to command file")
    metadata: PromptMetadata = Field(..., description="Parsed frontmatter")
    template: str = Field(..., description="Markdown body template")
    modified_at: datetime = Field(..., description="File modification time")
    size_bytes: int = Field(..., description="File size in bytes", le=100_000)

    def format(self, arguments: str = "") -> str:
        """Replace $ARGUMENTS placeholder in template."""
        return self.template.replace("$ARGUMENTS", arguments)

    def is_stale(self) -> bool:
        """Check if file was modified since load."""
        current_mtime = Path(self.file_path).stat().st_mtime
        return current_mtime != self.modified_at.timestamp()

    def reload(self) -> "Prompt":
        """Reload prompt from file system."""
        from .prompt_loader import load_prompt_from_file
        return load_prompt_from_file(Path(self.file_path))

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

---

### 3. PromptInvocationRequest

**Purpose**: Represents a request from MCP client to invoke a prompt with arguments.

**Properties**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | `str` | YES | Prompt name to invoke | `"sp.specify"` |
| `arguments` | `dict[str, Any]` | No | Arguments for prompt template | `{"arguments": "Add user auth"}` |

**Validation Rules**:
- `name` must match an existing prompt
- `arguments` must contain key "arguments" if present
- `arguments["arguments"]` must be string if present
- `arguments["arguments"]` length ≤ 10,000 characters

**Pydantic Model**:
```python
from typing import Any

class PromptInvocationRequest(BaseModel):
    """Request to invoke a prompt with arguments."""
    name: str = Field(..., description="Prompt name to invoke")
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments for prompt template (key: 'arguments')"
    )

    def get_arguments_str(self) -> str:
        """Extract arguments string from request."""
        return str(self.arguments.get("arguments", ""))

    class Config:
        schema_extra = {
            "example": {
                "name": "sp.specify",
                "arguments": {
                    "arguments": "Add user authentication feature"
                }
            }
        }
```

---

### 4. PromptInvocationResponse

**Purpose**: Represents response from MCP server to prompt invocation request.

**Properties**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `messages` | `list[PromptMessage]` | YES | Formatted prompt messages | `[{"role": "user", "content": {...}}]` |
| `description` | `str` | No | Optional description of response | "Specification creation prompt" |
| `error` | `str` | No | Error message if invocation failed | `"Prompt not found: sp.unknown"` |
| `timestamp` | `datetime` | YES | Response timestamp | `datetime(2026, 1, 6, 12, 0, 1)` |

**Nested Type: PromptMessage**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `role` | `str` | YES | Message role ("user" or "assistant") | `"user"` |
| `content` | `PromptContent` | YES | Message content (text, image, etc.) | `{"type": "text", "text": "..."}` |

**Nested Type: PromptContent** (Text variant):

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `type` | `str` | YES | Content type ("text", "image", "audio", "resource") | `"text"` |
| `text` | `str` | YES | Text content | `"## User Input\n\nAdd user auth..."` |

**Validation Rules**:
- `messages` must be non-empty list
- Each message must have valid `role` ("user" or "assistant")
- Each message must have valid `content` matching `type`
- If `error` is present, `messages` may be empty

**Pydantic Model**:
```python
from enum import Enum

class MessageType(str, Enum):
    """MCP message content types."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    RESOURCE = "resource"

class MessageRole(str, Enum):
    """MCP message role types."""
    USER = "user"
    ASSISTANT = "assistant"

class PromptContent(BaseModel):
    """Message content (discriminated union by type)."""
    type: MessageType = Field(..., description="Content type")
    text: str | None = Field(None, description="Text content (if type='text')")
    data: str | None = Field(None, description="Base64 data (if type='image'/'audio')")
    mimeType: str | None = Field(None, alias="mimeType", description="MIME type for binary data")

    class Config:
        schema_extra = {
            "example": {
                "type": "text",
                "text": "Please summarize the following text:\n\nHello world"
            }
        }

class PromptMessage(BaseModel):
    """MCP prompt message."""
    role: MessageRole = Field(..., description="Message role")
    content: PromptContent = Field(..., description="Message content")

class PromptInvocationResponse(BaseModel):
    """Response from prompt invocation."""
    messages: list[PromptMessage] = Field(..., description="Formatted prompt messages")
    description: str | None = Field(None, description="Optional response description")
    error: str | None = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

---

## Entity Relationships

```
PromptMetadata (1) ----< (1) Prompt
                                  |
                                  | loads from
                                  v |
                             .md file (1)
                                  |
                                  | invoked by
                                  v
PromptInvocationRequest (1) ----> (1) PromptInvocationResponse
```

**Relationship Rules**:
- Each `Prompt` contains exactly one `PromptMetadata`
- `Prompt` is loaded from exactly one `.md` file
- `PromptInvocationRequest` references one `Prompt` by name
- `PromptInvocationResponse` contains formatted messages from one `Prompt`

---

## State Transitions

### Prompt Lifecycle

```
[File on Disk] --> [Loaded in Memory] --> [Cached] --> [Invalidated] --> [Reloaded]
     ^                                    |
     |                                    v
     ------------------------------- [Stale Detection]
```

**States**:
1. **File on Disk**: Static markdown file in `.claude/commands/`
2. **Loaded in Memory**: Prompt parsed and cached in `PromptLoader`
3. **Cached**: Prompt available for MCP requests
4. **Invalidated**: File modified, cache marked stale
5. **Reloaded**: Prompt re-parsed and re-cached

**Transitions**:
- Load: File → Memory (on server startup or first request)
- Stale: Cached → Invalidated (file watcher detects change)
- Reload: Invalidated → Cached (next request triggers reload)

---

## Data Access Patterns

### Reading Prompts

1. **Discovery**: Scan `.claude/commands/` directory for `*.md` files
2. **Parsing**: Load each file, parse YAML frontmatter
3. **Validation**: Check required fields (`description`), file size limits
4. **Caching**: Store in memory with modification timestamp
5. **Exposure**: Register with FastMCP via `@mcp.prompt` decorator

### Invoking Prompts

1. **Request**: MCP client sends `prompts/get` with name and arguments
2. **Lookup**: Retrieve `Prompt` from cache by name
3. **Format**: Replace `$ARGUMENTS` in template with provided arguments
4. **Response**: Wrap formatted content in `PromptMessage` array
5. **Return**: Send `PromptInvocationResponse` to client

### Hot-Reload Flow

1. **Detect**: File watcher detects change event
2. **Debounce**: Wait 2s to collect rapid changes
3. **Invalidate**: Mark affected prompt(s) as stale
4. **Notify**: Send `notifications/prompts/list_changed` to clients
5. **Reload**: On next request, reload stale prompt from disk

---

## Validation Summary

### Type-Level Validation

| Entity | Validation | Tool |
|--------|-----------|------|
| `PromptMetadata` | Pydantic field types, required fields | Automatic |
| `Prompt` | File size ≤ 100KB, name format | Pydantic validators |
| `PromptInvocationRequest` | Arguments string length ≤ 10KB | Pydantic validators |
| `PromptInvocationResponse` | Non-empty messages or error | Pydantic validators |

### Business Logic Validation

| Rule | Implementation |
|------|----------------|
| File exists | Check `Path.exists()` before loading |
| Valid YAML | Catch `YAMLError` during frontmatter parsing |
| Required description | Validate `PromptMetadata.description` non-empty |
| No circular references | N/A (prompts are standalone) |
| Arguments substitution | Simple string replace, no template engine |

---

## Error Handling

### Parse Errors

```python
try:
    post = frontmatter.load(file_path)
    metadata = PromptMetadata(**post.metadata)
except yaml.YAMLError as e:
    raise ParseError(f"Invalid YAML in {file_path}: {e}")
except ValidationError as e:
    raise ParseError(f"Invalid frontmatter in {file_path}: {e}")
```

### File Errors

```python
try:
    content = Path(file_path).read_text(encoding='utf-8')
except FileNotFoundError:
    raise PromptNotFoundError(f"Prompt not found: {name}")
except PermissionError:
    raise AccessDeniedError(f"Cannot read {file_path}: permission denied")
```

### Validation Errors

```python
if prompt.size_bytes > 100_000:
    raise FileTooLargeError(f"Prompt {name} exceeds 100KB limit")

if len(arguments) > 10_000:
    raise ArgumentsTooLongError(f"Arguments exceed 10KB limit")
```

---

## Performance Considerations

### Memory Usage

- 13 prompts × ~5KB average = ~65KB in-memory cache
- Negligible impact for modern systems
- No pagination needed (prompts/list returns all prompts)

### Response Time

- Cached prompt lookup: <1ms (dict lookup)
- Arguments substitution: <1ms (string replace)
- Total invocation time: <500ms (well under spec requirement)

### File Watching Overhead

- watchfiles: ~10-20MB memory for watcher process
- Event-driven: No CPU usage when idle
- Negligible impact on server performance

---

## Extensibility

### Adding New Frontmatter Fields

```python
class PromptMetadata(BaseModel):
    description: str
    handoffs: list[Handoff] = []
    send: bool = False
    # New fields automatically ignored (extra="ignore")
    # Or explicitly add:
    # new_field: str | None = None
```

### Supporting New Content Types

```python
class PromptContent(BaseModel):
    type: MessageType
    text: str | None = None
    # Future: Add image support
    data: str | None = None
    mimeType: str | None = None
```

---

**Next**: See `contracts/mcp-prompts-schema.yaml` for MCP protocol schemas and `quickstart.md` for server setup.
