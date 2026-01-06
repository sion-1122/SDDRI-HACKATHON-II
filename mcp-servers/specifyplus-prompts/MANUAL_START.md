# Running the MCP Server Manually (Recommended for Development)

This approach lets you see server logs in real-time while developing!

## Setup (One-Time)

The `.mcp.json` is now configured to connect via HTTP:
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

## How to Use

### Step 1: Start the Server Manually

Open a terminal and run:

```bash
cd mcp-servers/specifyplus-prompts
source .venv/bin/activate
python -m specifyplus_prompts.server --transport http --port 8000
```

You should see:
```
2026-01-06 18:45:00 - specifyplus_prompts.server - INFO - Starting SpecifyPlus Prompts MCP server
2026-01-06 18:45:00 - specifyplus_prompts.server - INFO - Commands directory: /mnt/d/class/todo-list-hackathon/.claude/commands
2026-01-06 18:45:00 - specifyplus_prompts.server - INFO - Registered 13 prompts
2026-01-06 18:45:00 - specifyplus_prompts.server - INFO - Transport: http
2026-01-06 18:45:00 - specifyplus_prompts.server - INFO - Server URL: http://localhost:8000
2026-01-06 18:45:00 - specifyplus_prompts.server - INFO - File watching enabled
2026-01-06 18:45:00 - specifyplus_prompts.server - INFO - File watcher started
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

### Step 2: Restart Claude Code

Claude Code will automatically connect to `http://localhost:8000/mcp` when it starts.

### Step 3: Use the Server

Now you can:
- See all server logs in real-time in your terminal
- Make changes to `.claude/commands/` and see them hot-reloaded
- Debug issues more easily

## Testing the Connection

Ask Claude Code:
```
What prompts are available from the specifyplus-prompts MCP server?
```

You should see all 13 commands, and in your server terminal you'll see:
```
INFO:     127.0.0.1:54321 - "GET /prompts HTTP/1.1" 200 OK
```

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Alternative: Using stdio (Original Approach)

If you prefer the stdio approach (server starts automatically with Claude Code):

```bash
# Update .mcp.json to use:
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

## Advantages of HTTP Transport

✅ **Real-time logs** - See all requests/responses in terminal
✅ **Easy debugging** - Server stays running across Claude Code restarts
✅ **Hot-reload works** - Changes to commands are picked up immediately
✅ **No process spawning** - Server runs independently
✅ **Can test with curl** - `curl http://localhost:8000/prompts`

## Troubleshooting

**Port already in use:**
```bash
# Use a different port
python -m specifyplus_prompts.server --transport http --port 8001
```

**Connection refused:**
- Make sure the server is running before starting Claude Code
- Check the URL matches (http://localhost:8000/mcp)

**Commands not loading:**
- Check that `SPECIFYPLUS_COMMANDS_DIR` points to the correct directory
- Verify the `.claude/commands/` directory exists and has .md files
