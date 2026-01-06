# SpecifyPlus Prompts MCP Server

Exposes SpecifyPlus command files as MCP (Model Context Protocol) prompt resources.

## Overview

This MCP server enables any MCP-compatible client (IDEs, agents, tools) to discover and invoke SpecifyPlus workflows (spec creation, planning, task generation, etc.) without requiring terminal access or CLI execution.

## Features

- **Prompt Discovery**: Automatically discovers all SpecifyPlus commands from `.claude/commands/`
- **Argument Substitution**: Replaces `$ARGUMENTS` placeholders in command templates
- **Hot Reload**: File watching for dynamic prompt updates (User Story 2)
- **IDE Integration**: Works with VSCode, Cursor, and other MCP-enabled IDEs (User Story 3)

## Installation

```bash
cd mcp-servers/specifyplus-prompts
uv sync
```

## Usage

### Start Server (stdio transport)

**Option 1: Using wrapper script (Recommended for MCP clients):**
```bash
./run_server.sh
```

**Option 2: Using uv directly:**
```bash
uv run python src/specifyplus_prompts/server.py
```

**Option 3: As a Python module:**
```bash
cd mcp-servers/specifyplus-prompts
source .venv/bin/activate
python -m specifyplus_prompts.server
```

### Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run python src/specifyplus_prompts/server.py
```

## Configuration

Environment variables:
- `SPECIFYPLUS_COMMANDS_DIR`: Path to commands directory (default: `./.claude/commands`)
- `SPECIFYPLUS_DEBUG`: Enable debug logging (optional)
- `SPECIFYPLUS_NO_WATCH`: Disable file watching (optional)

## IDE Integration

### VSCode

1. Install the [MCP extension for VSCode](https://marketplace.visualstudio.com/items?itemName=modelcontextprotocol.mcp-vscode)

2. Add to your VSCode `settings.json`:

```json
{
  "mcp.servers": {
    "specifyplus-prompts": {
      "command": "/absolute/path/to/mcp-servers/specifyplus-prompts/run_server.sh",
      "args": [],
      "env": {
        "SPECIFYPLUS_COMMANDS_DIR": "/absolute/path/to/your/project/.claude/commands"
      }
    }
  }
}
```

**Example for this project:**
```json
{
  "mcp.servers": {
    "specifyplus-prompts": {
      "command": "/mnt/d/class/todo-list-hackathon/mcp-servers/specifyplus-prompts/run_server.sh",
      "args": [],
      "env": {
        "SPECIFYPLUS_COMMANDS_DIR": "/mnt/d/class/todo-list-hackathon/.claude/commands"
      }
    }
  }
}
```

3. Restart VSCode

4. Use the MCP sidebar to invoke SpecifyPlus commands:
   - Select text in your editor
   - Choose a prompt (e.g., `sp.specify`)
   - The selected text will be passed as arguments

### Cursor IDE

1. Cursor has built-in MCP support

2. Add to your Cursor settings (Settings → Features → MCP Servers):

```json
{
  "mcp.servers": {
    "specifyplus-prompts": {
      "command": "/absolute/path/to/mcp-servers/specifyplus-prompts/run_server.sh",
      "args": [],
      "env": {
        "SPECIFYPLUS_COMMANDS_DIR": "/absolute/path/to/your/project/.claude/commands"
      }
    }
  }
}
```

**Example for this project:**
```json
{
  "mcp.servers": {
    "specifyplus-prompts": {
      "command": "/mnt/d/class/todo-list-hackathon/mcp-servers/specifyplus-prompts/run_server.sh",
      "args": [],
      "env": {
        "SPECIFYPLUS_COMMANDS_DIR": "/mnt/d/class/todo-list-hackathon/.claude/commands"
      }
    }
  }
}
```

3. Restart Cursor

4. Access prompts via the MCP panel in Cursor

### Usage Examples

**Invoke sp.specify with selected text:**
1. Select your feature description in the editor
2. Right-click → MCP Prompts → sp.specify
3. The prompt will execute with your selection as `$ARGUMENTS`

**Invoke sp.plan for current context:**
1. Open your spec.md file
2. Select the entire file content
3. Use sp.plan prompt to generate implementation plan

**Create GitHub issues from tasks:**
1. Open tasks.md
2. Select task descriptions
3. Use sp.taskstoissues to generate GitHub issues

## Documentation

See [quickstart.md](../../specs/002-mcp-server-prompts/quickstart.md) for complete usage guide.

## Architecture

- `models.py`: Pydantic schemas for prompts and metadata
- `prompt_loader.py`: Command file parsing and caching
- `file_watcher.py`: Hot-reload file system watcher
- `server.py`: MCP server entry point
