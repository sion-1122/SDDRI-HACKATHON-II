
@AGENTS.md
# todo-list-hackathon Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-02

## Active Technologies
- Python 3.13+ with FastMCP framework + FastMCP (MCP server framework), Pydantic (schema validation), watchfiles (file system watching) (002-mcp-server-prompts)
- File system (reads `.claude/commands/` directory, no write operations) (002-mcp-server-prompts)
- TypeScript 5+ with Next.js 16.1.1 and React 19.2.3 + Next.js (App Router), Better Auth (authentication), React 19, Tailwind CSS 4 (003-frontend-task-manager)
- No direct database access - all data via REST API to existing FastAPI backend (003-frontend-task-manager)

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
- 003-frontend-task-manager: Added TypeScript 5+ with Next.js 16.1.1 and React 19.2.3 + Next.js (App Router), Better Auth (authentication), React 19, Tailwind CSS 4
- 001-backend-task-api: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
