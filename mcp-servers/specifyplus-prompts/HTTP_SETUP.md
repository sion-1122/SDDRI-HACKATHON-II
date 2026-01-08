# ✅ HTTP MCP Server Setup Complete!

## Quick Start (3 Steps)

### 1. Start the Server in a Separate Terminal

```bash
cd /mnt/d/class/todo-list-hackathon/mcp-servers/specifyplus-prompts
source .venv/bin/activate
SPECIFYPLUS_COMMANDS_DIR="/mnt/d/class/todo-list-hackathon/.claude/commands" \
python -m specifyplus_prompts.server --transport http --port 8000
```

**You'll see:**
```
2026-01-06 19:00:21 - INFO - Loading prompts from /mnt/d/class/todo-list-hackathon/.claude/commands
2026-01-06 19:00:21 - INFO - Loaded 13 prompts
2026-01-06 19:00:21 - INFO - Starting SpecifyPlus Prompts MCP server
2026-01-06 19:00:21 - INFO - Server URL: http://localhost:8000
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

### 2. Restart Claude Code

Claude Code will connect to `http://localhost:8000/mcp` automatically.

### 3. Test It

Ask Claude Code:
```
What prompts are available from the specifyplus-prompts MCP server?
```

You should see all 13 SpecifyPlus commands!

## Configuration Files

### `.mcp.json` (Already Configured)
```json
{
  "mcpServers": {
    "specifyplus-prompts": {
      "url": "http://localhost:8000/mcp",
      "env": {
        "SPECIFYPLUS_COMMANDS_DIR": "/mnt/d/class/todo-list-hackathon/.claude/commands"
      }
    }
  }
}
```

### Server Features
- ✅ **HTTP Transport**: Connect via `http://localhost:8000/mcp`
- ✅ **Hot-reload**: Changes to `.claude/commands/` detected in 2 seconds
- ✅ **Real-time logs**: See all requests in your terminal
- ✅ **Independent process**: Server stays running across Claude Code restarts

## Testing the Server

### Test with curl (Optional)
```bash
# List all prompts
curl http://localhost:8000/prompts

# Get a specific prompt
curl -X POST http://localhost:8000/prompts/sp.specify \
  -H "Content-Type: application/json" \
  -d '{"arguments": "Create a user login feature"}'
```

### Monitor Real-time Activity

When you use the MCP server, you'll see logs like:
```
INFO:     127.0.0.1:54321 - "POST /prompts/sp.specify HTTP/1.1" 200 OK
2026-01-06 19:05:30 - INFO - Invoking prompt 'sp.specify' with 28 characters of arguments
```

## Troubleshooting

**"Connection refused" error:**
- Make sure the server is running before starting Claude Code
- Check that port 8000 is available: `lsof -i :8000`

**"Loaded 0 prompts":**
- Verify the environment variable is set correctly
- Check that `.claude/commands/` exists and has .md files

**Port already in use:**
```bash
# Use a different port
python -m specifyplus_prompts.server --transport http --port 8001
```

Then update `.mcp.json` to match:
```json
{
  "url": "http://localhost:8001/mcp"
}
```

## Alternative: stdio Transport

If you prefer the server to start automatically with Claude Code, use stdio transport:

```bash
# Update .mcp.json to:
{
  "mcpServers": {
    "specifyplus-prompts": {
      "command": "/mnt/d/class/todo-list-hackathon/mcp-servers/specifyplus-prompts/run_server.sh",
      "args": [],
      "env": {
        "SPECIFYPLUS_TRANSPORT": "stdio",
        "SPECIFYPLUS_COMMANDS_DIR": "/mnt/d/class/todo-list-hackathon/.claude/commands"
      }
    }
  }
}
```

## Advantages of HTTP Approach

✅ See real-time server logs
✅ Easier debugging
✅ Server survives Claude Code restarts
✅ Can test with curl/browser
✅ Hot-reload works immediately
✅ No process spawning overhead

Enjoy your MCP server! 🎉
