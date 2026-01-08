
@AGENTS.md
# todo-list-hackathon Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-02

## Active Technologies
- Python 3.13+ with FastMCP framework + FastMCP (MCP server framework), Pydantic (schema validation), watchfiles (file system watching) (002-mcp-server-prompts)
- File system (reads `.claude/commands/` directory, no write operations) (002-mcp-server-prompts)

- Python 3.13+ + TUI library (textual, rich, or prompt_toolkit - to be determined in research phase) (001-todo-cli-tui)

## Project Structure

```text
src/
tests/
```

## Commands

**MCP Server (002-mcp-server-prompts):**
```bash
cd mcp-servers/specifyplus-prompts
uv sync                              # Install dependencies
uv run python src/specifyplus_prompts/server.py    # Start MCP server
uv run pytest tests/                # Run tests
npx @modelcontextprotocol/inspector uv run python src/specifyplus_prompts/server.py  # Test with MCP Inspector
```

**General (for all features):**
cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.13+: Follow standard conventions

## Recent Changes
- 002-mcp-server-prompts: Added Python 3.13+ with FastMCP framework + FastMCP (MCP server framework), Pydantic (schema validation), watchfiles (file system watching)

- 001-todo-cli-tui: Added Python 3.13+ + TUI library (textual, rich, or prompt_toolkit - to be determined in research phase)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
