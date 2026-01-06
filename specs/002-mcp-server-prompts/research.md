# Research Report: MCP Server for SpecifyPlus Prompts

**Feature**: 002-mcp-server-prompts
**Date**: 2026-01-06
**Status**: Phase 0 Complete

## Executive Summary

Research confirms that FastMCP 2.x fully supports MCP prompt resources via the `@mcp.prompt` decorator. The MCP prompt protocol provides built-in support for listing, getting, and dynamic prompt discovery through the `listChanged` capability. Python's `frontmatter` library is the best choice for YAML frontmatter parsing, and `watchfiles` provides cross-platform file watching with minimal overhead.

## 1. FastMCP Framework Capabilities

### Decision: Use FastMCP 2.x with `@mcp.prompt` decorator

**Rationale**:
- FastMCP 2.x provides native support for MCP prompt resources via `@mcp.prompt` decorator
- Prompts are first-class citizens alongside tools and resources
- Built-in stdio transport with easy HTTP/SSE transport upgrade for future
- Decorator-based registration automatically handles schema generation
- Excellent Python 3.13+ compatibility

**Key Features Discovered**:
- Prompt registration: `@mcp.prompt(name="prompt-name")` decorator
- Automatic argument schema generation from function signatures
- Support for both string and Message object returns
- Optional `listChanged` capability for hot-reload notifications
- Context injection for logging and resource access

**Implementation Pattern**:
```python
from fastmcp import FastMCP

mcp = FastMCP("SpecifyPlus Prompts")

@mcp.prompt()
def sp_specify(arguments: str = "") -> str:
    """Create or update feature specification."""
    # Load prompt from file, substitute arguments
    return prompt_content

# Dynamic registration supported
for prompt_name in prompt_loader.list_prompts():
    mcp.prompt()(create_handler(prompt_name))
```

**Transport Flexibility**:
- Default: stdio (perfect for local development)
- Easy upgrade: `mcp.run(transport="http", host="0.0.0.0", port=8000)`
- Future: SSE transport for cloud deployment
- No architectural changes required to switch transports

**Alternatives Considered**:
- Official MCP Python SDK: More boilerplate, less opinionated
- TypeScript SDK: Excellent but requires different tech stack
- **Rejected**: Would require deviating from existing Python tooling

---

## 2. MCP Prompt Resource Specification

### Decision: Implement prompts/list, prompts/get, and listChanged notification

**Rationale**:
- MCP prompt protocol is well-defined with three main operations
- Prompts support arguments (perfect for `$ARGUMENTS` substitution)
- Built-in discovery mechanism via prompts/list
- Optional metadata (title, description, argument schemas)
- Message-based return format supports multi-part content

**Protocol Details**:

**prompts/list**:
- Returns all available prompts with metadata
- Supports pagination (not needed for 13 commands, but good for future)
- Each prompt includes: name, title, description, arguments schema
- Arguments can be marked required/optional
- Optional icons support (not needed for MVP)

**prompts/get**:
- Retrieves specific prompt with arguments substituted
- Returns PromptMessage array with role/content
- Content can be text, image, audio, or embedded resource
- We'll use text content for markdown prompts
- Arguments passed as key-value pairs

**notifications/prompts/list_changed**:
- Server sends notification when prompt list changes
- Requires `listChanged: true` in capabilities
- Perfect for hot-reload feature
- Client can re-list prompts after notification

**Metadata Exposure Strategy**:
- `name`: Filename without extension (e.g., "sp.specify")
- `title`: From frontmatter description field
- `description`: First line of frontmatter description
- `arguments`: Single argument named "arguments" (optional)
- No icons needed for MVP (can add later if desired)

**Argument Passing Pattern**:
- Single string argument named "arguments"
- Maps to `$ARGUMENTS` placeholder in command files
- Default value: empty string
- FastMCP auto-generates JSON schema for this

**Implementation Notes**:
- FastMCP's `@mcp.prompt` decorator automatically registers prompts/list handler
- Decorator function receives arguments, returns string or Message
- FastMCP handles JSON-RPC protocol details
- We just need to load file, substitute arguments, return content

---

## 3. YAML Frontmatter Parsing Best Practices

### Decision: Use `python-frontmatter` library with error handling

**Rationale**:
- Specialized library for markdown + YAML parsing
- Handles edge cases (missing delimiters, malformed YAML)
- Preserves original markdown formatting (crucial for prompts)
- Widely used (50k+ downloads/month)
- Simple API: `frontmatter.load(file)` returns Post object

**Implementation Strategy**:
```python
import frontmatter

def load_command_file(file_path: str) -> Prompt:
    try:
        post = frontmatter.load(file_path)
        metadata = post.metadata  # YAML frontmatter as dict
        content = post.content     # Markdown body

        # Validate required fields
        if 'description' not in metadata:
            raise ValueError(f"Missing description in {file_path}")

        return Prompt(
            name=file_path.stem,
            description=metadata['description'],
            handoffs=metadata.get('handoffs', []),
            content=content
        )
    except yaml.YAMLError as e:
        raise ParseError(f"Invalid YAML in {file_path}: {e}")
```

**Error Handling**:
- Catch `yaml.YAMLError` for malformed frontmatter
- Catch `FileNotFoundError` for missing files
- Catch `PermissionError` for access denied
- Log all errors, skip file in listings
- Never crash due to parsing errors

**Encoding Handling**:
- `frontmatter.load()` uses UTF-8 by default
- Can specify encoding: `frontmatter.load(file, encoding='utf-8')`
- For non-UTF-8 files, catch `UnicodeDecodeError`
- Strategy: Try UTF-8, fallback to latin-1 if needed, log error

**Required vs Optional Fields**:
- Required: `description` (used for prompt metadata)
- Optional: `handoffs`, `send` flag (SpecifyPlus-specific)
- All other fields: Ignored (forward compatibility)

**Alternatives Considered**:
- Custom YAML + markdown parsing: More control, but reinvents wheel
- `python-frontmatter` vs `yaml.markdown`: frontmatter is more robust
- **Rejected**: Would require handling edge cases manually

---

## 4. File System Watching Strategies

### Decision: Use `watchfiles` with 2-second debounce

**Rationale**:
- Cross-platform support (Linux/macOS/Windows)
- Efficient Rust-based implementation (no polling overhead)
- Simple API: `watch(...)` returns async iterator
- Integrates well with async/await pattern
- Better performance than `watchdog` for our use case

**Implementation Pattern**:
```python
import asyncio
from watchfiles import awatch

async def watch_commands_directory(commands_dir: str, loader: PromptLoader):
    """Watch for file changes and invalidate cache."""
    async for changes in awatch(commands_dir):
        # Debounce: collect changes for 2s
        await asyncio.sleep(2.0)

        # Process all changes
        for change_type, file_path in changes:
            if change_type == Change.deleted:
                loader.remove_prompt(file_path)
            else:  # Change.added or Change.modified
                loader.reload_prompt(file_path)

        # Notify MCP clients of list change
        await send_list_changed_notification()
```

**Debounce Strategy**:
- Rapid file edits (e.g., vim save) trigger multiple events
- Wait 2s after first event, then process all accumulated changes
- Balances responsiveness with efficiency
- Aligns with success criteria: 95% reloads within 2s

**Performance Impact**:
- `watchfiles` uses native OS file watching APIs (inotify on Linux)
- Minimal CPU usage (event-driven, not polling)
- Memory overhead: ~10-20MB for watcher process
- With 13 files and nested directories: Negligible impact

**Graceful Degradation**:
- If `awatch()` fails (permissions, unsupported platform):
  - Log warning: "File watching unavailable, hot-reload disabled"
  - Continue server startup without watcher
  - Server still works, just no automatic reloads
- Runtime errors during watching:
  - Catch and log exception
  - Continue watching (don't crash server)

**Alternatives Considered**:
- Polling with `time.sleep()`: Simple but inefficient
- `watchdog`: More features but heavier
- **Rejected**: watchfiles is lighter and more modern

---

## 5. Argument Sanitization and Security

### Decision: Minimal sanitization with length limits

**Rationale**:
- Arguments are text substitution, not code execution
- Risk: Prompt injection attacks (arguments manipulating prompt behavior)
- Mitigation: Replace `$ARGUMENTS` after YAML parsing, not before
- Additional safeguard: Length limits and logging

**Sanitization Strategy**:

**1. Length Limit**:
```python
MAX_ARGUMENTS_LENGTH = 10_000  # 10KB

def sanitize_arguments(arguments: str) -> str:
    if len(arguments) > MAX_ARGUMENTS_LENGTH:
        logger.warning(f"Arguments truncated to {MAX_ARGUMENTS_LENGTH} chars")
        return arguments[:MAX_ARGUMENTS_LENGTH]
    return arguments
```

**2. Markdown Preservation**:
- Don't escape markdown formatting (newlines, bullets, code blocks)
- Users expect markdown in arguments to work
- Prompt templates already markdown-formatted
- Let LLM handle any weirdness

**3. No Code Execution**:
- Arguments never passed to `eval()` or `exec()`
- Only string substitution: `template.replace("$ARGUMENTS", arguments)`
- No risk of code injection from arguments
- YAML parsing happens BEFORE substitution (safe)

**4. Logging**:
- Log all prompt invocations with argument length
- Don't log full arguments (may contain sensitive data)
- Example: `logger.info(f"Invoked sp.specify with {len(args)} chars")`

**Injection Attack Vectors Addressed**:

**Markdown Injection**:
- User provides: `---\ndescription: fake\n---`
- Our defense: YAML parsing complete before substitution
- Result: Treated as markdown text, not frontmatter

**Template Manipulation**:
- User provides: `$ARGUMENTS` and `$OTHER`
- Our defense: Only replace `$ARGUMENTS` literal
- Result: `$OTHER` passed through as-is

**Excessive Output**:
- User provides: 1MB of text
- Our defense: 10KB length limit
- Result: Truncated with warning logged

**What We DON'T Do** (and Why):
- Don't HTML-escape: Prompts are markdown, not HTML
- Don't LaTeX-escape: No LaTeX in our prompts
- Don't remove special chars: Breaks legitimate use cases
- Don't blacklist keywords: Too fragile, false positives

**Security Assessment**:
- **Risk Level**: LOW
- **Attack Surface**: Arguments only affect LLM context, not system
- **Mitigation**: Length limits + no code execution
- **Monitoring**: Log all invocations for auditing

---

## 6. Additional Technical Decisions

### 6.1 Nested Directory Structure

**Decision**: Support nested subdirectories in `.claude/commands/`

**Rationale**:
- Flat structure works now (13 files in root)
- Future: Organize by category (e.g., `sp/`, `git/`)
- MCP prompt names use "/" separator naturally
- No additional complexity: recursive file scan

**Implementation**:
```python
from pathlib import Path

def scan_commands_dir(commands_dir: Path) -> dict[str, Prompt]:
    prompts = {}
    for md_file in commands_dir.rglob("*.md"):
        prompt_name = str(md_file.relative_to(commands_dir).with_suffix(''))
        prompts[prompt_name] = load_prompt(md_file)
    return prompts
```

**Example Prompt Names**:
- `.claude/commands/sp.specify.md` → `sp.specify`
- `.claude/commands/git/commit.md` → `git/commit`
- `.claude/commands/utils/helpers.md` → `utils/helpers`

### 6.2 Circular References

**Decision**: Detect and reject circular references

**Rationale**:
- Prompts shouldn't reference other prompts (no include mechanism)
- Circular reference = bug in command file
- Better to fail fast than hang

**Detection**:
- Not applicable: Our prompts don't include other prompts
- Each prompt is standalone markdown file
- No template inheritance or composition
- **Action**: Document that prompts must be standalone

### 6.3 Excessive File Sizes

**Decision**: Load files up to 100KB, reject larger

**Rationale**:
- Current commands: ~2-8KB each
- 100KB = generous limit for future growth
- Larger files likely indicate bug (e.g., binary data)
- Protects memory usage

**Implementation**:
```python
MAX_FILE_SIZE = 100_000  # 100KB

def load_prompt(file_path: Path) -> Prompt:
    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {file_size} bytes")
    # ... load and parse
```

### 6.4 Prompt Metadata Exposure

**Decision**: Expose all frontmatter as prompt metadata

**Rationale**:
- Frontmatter already contains useful metadata (description, handoffs)
- MCP protocol allows arbitrary metadata in prompts
- Clients can inspect metadata for advanced features
- Forward-compatible with new frontmatter fields

**Implementation**:
```python
@mcp.prompt()
def sp_specify(arguments: str = "") -> list[Message]:
    prompt = loader.get_prompt("sp.specify")

    return [
        Message(
            role="user",
            content=Content(
                type="text",
                text=prompt.format(arguments)
            )
        )
    ]
```

**Metadata in prompts/list Response**:
```json
{
  "name": "sp.specify",
  "description": "Create or update feature specification",
  "arguments": [
    {
      "name": "arguments",
      "description": "User input for feature description",
      "required": false
    }
  ]
}
```

---

## 7. Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| MCP Framework | FastMCP | 2.x | Native prompt support, Pythonic |
| Transport | stdio | - | Default, works with MCP Inspector |
| YAML Parsing | python-frontmatter | latest | Robust markdown + YAML handling |
| File Watching | watchfiles | latest | Cross-platform, efficient |
| Validation | Pydantic | 2.x | Built-in to FastMCP |
| Testing | pytest + pytest-asyncio | latest | Async testing support |

---

## 8. Open Questions Resolved

### Q1: Does FastMCP support prompt resources?
**Answer**: YES. FastMCP 2.x has native `@mcp.prompt` decorator that registers MCP prompt resources. No tools workaround needed.

### Q2: How to handle circular references?
**Answer**: Not applicable. Our prompts are standalone markdown files with no include mechanism. Document this constraint.

### Q3: Support nested subdirectories?
**Answer**: YES. Use recursive glob (`rglob("*.md")`) and "/" separator in prompt names. Natural fit for MCP protocol.

### Q4: Expose prompt metadata?
**Answer**: YES. Use frontmatter fields for prompt description and arguments schema. MCP clients can display this metadata.

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| FastMCP 3.0 breaking changes | Low | Medium | Pin to `fastmcp<3` in dependencies |
| File watching fails on Windows | Low | Low | Graceful degradation, server works without hot-reload |
| Malformed YAML in existing commands | Medium | Low | Parse errors logged, file skipped, others work |
| Prompt injection via arguments | Low | Low | Length limits, no code execution path |
| Performance with 100+ files | Low | Low | Lazy loading, cache hits, <500ms response |

**Overall Risk Level**: LOW

---

## 10. Next Steps

Phase 0 complete. Proceed to Phase 1:

1. Create `data-model.md` with Pydantic schema definitions
2. Create `contracts/mcp-prompts-schema.yaml` with protocol schemas
3. Create `quickstart.md` with server setup and testing instructions
4. Update agent context files with MCP server technology
5. Re-run Constitution Check to verify no violations

**Ready to proceed to `/sp.plan` Phase 1 design artifacts.**
