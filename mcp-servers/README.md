# MCP Servers

This directory contains MCP (Model Context Protocol) servers that integrate SpecifyPlus workflows with MCP-compatible clients (IDEs, agents, tools).

## Available Servers

### SpecifyPlus Prompts

**Location:** `specifyplus-prompts/`

**Purpose:** Exposes SpecifyPlus command files as MCP prompt resources for IDE integration and workflow automation.

**Features:**
- Prompt discovery from `.claude/commands/` directory
- Argument substitution ($ARGUMENTS placeholder)
- Hot-reload with file watching
- IDE integration (VSCode, Cursor)

**Documentation:** See [specifyplus-prompts/README.md](./specifyplus-prompts/README.md)

## Quick Start

### Installation

```bash
cd specifyplus-prompts
uv sync
```

### Start Server

```bash
cd specifyplus-prompts
uv run python src/specifyplus_prompts/server.py
```

### Test with MCP Inspector

```bash
cd specifyplus-prompts
npx @modelcontextprotocol/inspector uv run python src/specifyplus_prompts/server.py
```

## IDE Configuration

### VSCode

Add to `settings.json`:

```json
{
  "mcp.servers": {
    "specifyplus-prompts": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/absolute/path/to/mcp-servers/specifyplus-prompts/src/specifyplus_prompts/server.py"
      ],
      "env": {
        "SPECIFYPLUS_COMMANDS_DIR": "/absolute/path/to/your/project/.claude/commands"
      }
    }
  }
}
```

### Cursor IDE

Add to Settings → Features → MCP Servers:

```json
{
  "mcp.servers": {
    "specifyplus-prompts": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/absolute/path/to/mcp-servers/specifyplus-prompts/src/specifyplus_prompts/server.py"
      ],
      "env": {
        "SPECIFYPLUS_COMMANDS_DIR": "/absolute/path/to/your/project/.claude/commands"
      }
    }
  }
}
```

## Architecture

MCP servers follow the [Model Context Protocol](https://modelcontextprotocol.io) specification:

- **Transport:** stdio (local development), HTTP (future support)
- **Resources:** Prompts from SpecifyPlus commands
- **Tools:** Dynamic prompt registration based on available commands
- **Notifications:** File watching for hot-reload

## Development

### Running Tests

```bash
cd specifyplus-prompts
uv run pytest tests/ -v
```

### Adding New MCP Servers

1. Create new directory in `mcp-servers/`
2. Follow MCP server best practices
3. Add documentation to this README
4. Update project CLAUDE.md with commands

## See Also

- [SpecifyPlus Documentation](../../specs/002-mcp-server-prompts/)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
