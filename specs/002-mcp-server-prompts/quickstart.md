# Quickstart Guide: MCP Server for SpecifyPlus Prompts

**Feature**: 002-mcp-server-prompts
**Target Audience**: Developers integrating SpecifyPlus workflows with MCP clients
**Time to Complete**: 10 minutes

---

## Overview

This guide will help you:
1. Install and run the SpecifyPlus MCP server
2. Connect from MCP clients (Inspector, IDE extensions)
3. Test prompt discovery and invocation
4. Troubleshoot common issues

**What is this server?**

The SpecifyPlus MCP server exposes your `.claude/commands/` directory as MCP prompt resources. This means you can use SpecifyPlus workflows (spec creation, planning, task generation, etc.) from any MCP-compatible client without leaving your IDE or running terminal commands.

---

## Prerequisites

- Python 3.13+
- `uv` package manager (recommended) or `pip`
- Existing SpecifyPlus project with `.claude/commands/` directory

**Verify prerequisites**:
```bash
python --version  # Should be 3.13+
uv --version      # Should be installed
ls .claude/commands/ | wc -l  # Should show command files
```

---

## Installation

### Option 1: Local Development (Recommended)

1. **Navigate to MCP server directory**:
   ```bash
   cd mcp-servers/specifyplus-prompts
   ```

2. **Create virtual environment and install dependencies**:
   ```bash
   uv sync
   # Or with pip:
   # pip install -e .
   ```

3. **Verify installation**:
   ```bash
   uv run python -c "from fastmcp import FastMCP; print('FastMCP installed')"
   ```

### Option 2: Install from Package Registry (Future)

```bash
pip install specifyplus-prompts-mcp
```

---

## Running the Server

### Development Mode (stdio Transport)

1. **Start the server**:
   ```bash
   uv run python src/specifyplus_prompts/server.py
   ```

2. **Server starts and waits for stdio connection**:
   - No output (waiting for MCP client)
   - Press Ctrl+C to stop

3. **Environment variables** (optional):
   ```bash
   # Custom commands directory (default: .claude/commands)
   export SPECIFYPLUS_COMMANDS_DIR="/path/to/commands"

   # Enable debug logging
   export SPECIFYPLUS_DEBUG="true"

   # Disable file watching (no hot-reload)
   export SPECIFYPLUS_NO_WATCH="true"
   ```

### Production Mode (HTTP Transport)

```bash
uv run python src/specifyplus_prompts/server.py --transport http --host 0.0.0.0 --port 8000
```

Access at: `http://localhost:8000/mcp`

---

## Testing with MCP Inspector

The MCP Inspector is the official tool for testing MCP servers interactively.

### Install and Run Inspector

1. **Install Inspector** (Node.js required):
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

2. **Connect Inspector to server**:
   ```bash
   npx @modelcontextprotocol/inspector uv run python src/specifyplus_prompts/server.py
   ```

3. **Inspector opens in browser**:
   - URL: `http://localhost:5173`
   - Explore available prompts
   - Test prompt invocation with arguments

### Inspector Workflow

**1. List Prompts**:
- Click "Prompts" tab
- See all available prompts (e.g., `sp.specify`, `sp.plan`, `git.commit`)
- View descriptions and argument schemas

**2. Invoke a Prompt**:
- Select a prompt (e.g., `sp.specify`)
- Enter arguments in JSON format:
  ```json
  {
    "arguments": "Add user authentication feature"
  }
  ```
- Click "Invoke"
- View returned messages with substituted arguments

**3. Test Hot-Reload**:
- Modify a command file in `.claude/commands/`
- Save the file
- In Inspector, re-list prompts
- Verify updated prompt appears

---

## IDE Integration

### VSCode with MCP Extension

1. **Install MCP extension**:
   - Search "MCP" in VSCode extensions
   - Install official Model Context Protocol extension

2. **Configure MCP server**:
   - Open VSCode Settings (JSON)
   - Add to `mcp.servers` configuration:
     ```json
     {
       "mcp.servers": {
         "specifyplus": {
           "command": "uv",
           "args": [
             "run",
             "python",
             "/path/to/mcp-servers/specifyplus-prompts/src/specifyplus_prompts/server.py"
           ],
           "env": {
             "SPECIFYPLUS_COMMANDS_DIR": "/path/to/.claude/commands"
           }
         }
       }
     }
     ```

3. **Restart VSCode**

4. **Use prompts from Command Palette**:
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Type "MCP: SpecifyPlus"
   - Select a prompt (e.g., "Create Specification")
   - Enter arguments when prompted
   - Prompt content is inserted into editor or sent to LLM

### JetBrains IDEs (Future Support)

Similar configuration via:
- Settings → Tools → Model Context Protocol
- Add server with stdio command
- Access via "Tools" menu

### Cursor Editor

1. **Settings → Features → MCP Servers**
2. **Add server**:
   - Name: `specifyplus`
   - Command: `uv run python /path/to/server.py`
3. **Access via Cmd+K → Prompts**

---

## Usage Examples

### Example 1: Create Specification from Selection

**Scenario**: You have a feature description in your editor and want to create a spec.

1. **Select feature description text**:
   ```
   Add OAuth2 authentication with Google provider
   ```

2. **Invoke `sp.specify` prompt**:
   - VSCode: `Ctrl+Shift+P` → "MCP: sp.specify"
   - Cursor: Cmd+K → "sp.specify"

3. **Paste selection as arguments**:
   - MCP client passes selected text as `arguments`

4. **Receive formatted prompt**:
   - Full specification creation workflow
   - With your feature description substituted
   - Ready to send to LLM

### Example 2: Generate Implementation Plan

**Scenario**: You have a spec and want to create an implementation plan.

1. **Invoke `sp.plan` prompt**:
   - Pass spec identifier as argument: `"002-mcp-server-prompts"`

2. **Receive plan creation prompt**:
   - Pre-populated with spec context
   - Includes architecture questions
   - Ready for LLM to generate plan

### Example 3: Chain Multiple Prompts

**Scenario**: Full Spec-Driven Development workflow.

1. **sp.specify**: Create specification from feature description
2. **sp.plan**: Generate implementation plan from spec
3. **sp.tasks**: Break down plan into actionable tasks
4. **sp.implement**: Execute tasks with code generation

Each prompt passes context to the next, creating a seamless workflow.

---

## Troubleshooting

### Server Won't Start

**Symptom**: `ModuleNotFoundError: No module named 'fastmcp'`

**Solution**:
```bash
# Ensure dependencies installed
uv sync

# Or with pip
pip install fastmcp frontmatter watchfiles
```

**Symptom**: `FileNotFoundError: .claude/commands`

**Solution**:
```bash
# Verify commands directory exists
ls .claude/commands

# Set correct path via environment variable
export SPECIFYPLUS_COMMANDS_DIR="/path/to/.claude/commands"
```

### No Prompts Appear in Inspector

**Symptom**: prompts/list returns empty array

**Possible causes**:
1. **No markdown files in commands directory**:
   ```bash
   # Check for .md files
   ls .claude/commands/*.md
   ```

2. **All files have malformed YAML**:
   - Check server logs for parse errors
   - Verify YAML frontmatter syntax:
     ```yaml
     ---
     description: "Required field"
     ---
     ```

3. **File permissions**:
   ```bash
   # Ensure readable
   chmod +r .claude/commands/*.md
   ```

### Hot-Reload Not Working

**Symptom**: Modified commands don't appear updated

**Possible causes**:
1. **File watching disabled**:
   ```bash
   # Check environment variable
   echo $SPECIFYPLUS_NO_WATCH
   # Unset to enable watching
   unset SPECIFYPLUS_NO_WATCH
   ```

2. **Watcher crashed**:
   - Check server logs for watcher errors
   - Restart server

3. **Debounce delay**:
   - Hot-reload has 2-second debounce
   - Wait 2-3 seconds after saving file

### Arguments Not Substituting

**Symptom**: Prompt returns template with `$ARGUMENTS` literal

**Possible causes**:
1. **Missing placeholder in template**:
   - Verify command file contains `$ARGUMENTS`
   - Check it's not escaped: `\$ARGUMENTS`

2. **Arguments not passed correctly**:
   - Inspector: Verify JSON format
   - IDE: Check arguments are being sent

3. **Prompt loader caching issue**:
   - Restart server to clear cache

---

## Performance Tips

### 1. Lazy Loading

Server loads prompts on first request (not startup).
- **Startup time**: <1 second
- **First request**: ~500ms (file loading)
- **Subsequent requests**: <50ms (cached)

### 2. Limit File Sizes

Large files (>100KB) are rejected.
- **Keep prompts focused**: <10KB recommended
- **Split large prompts**: Into multiple command files

### 3. Reduce File Watching Overhead

If hot-reload not needed:
```bash
export SPECIFYPLUS_NO_WATCH="true"
```

Saves ~10-20MB memory and eliminates file watcher thread.

---

## Security Considerations

### Local Development Only

This server is designed for local development:
- **No authentication**: Assumes trusted environment
- **No encryption**: stdio transport is local only
- **No network exposure**: Unless HTTP transport explicitly enabled

### File Access

- **Read-only**: Server only reads `.claude/commands/`
- **No path traversal**: Validates paths stay in commands dir
- **No symlink following**: Prevents escaping directory

### Argument Sanitization

- **Length limits**: Arguments truncated at 10KB
- **No code execution**: Only text substitution
- **Logging**: All invocations logged for auditing

**For production deployment**:
1. Enable authentication (FastMCP supports OAuth)
2. Use HTTP/SSE transport with HTTPS
3. Run in isolated environment (Docker, VM)
4. Add rate limiting

---

## Next Steps

### Advanced Configuration

See the full documentation for:
- Custom argument validation
- Multiple commands directories
- Prompt filtering (include/exclude patterns)
- Custom transport configuration
- Authentication setup

### Contributing

Want to extend the server?
- See `plan.md` for architecture
- See `data-model.md` for entity definitions
- See `contracts/` for protocol schemas

### Getting Help

- **Issues**: Report bugs via GitHub issues
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: See `specs/002-mcp-server-prompts/` for complete design docs

---

**Happy specifying! May your specs be clear and your plans be solid.** 🚀
