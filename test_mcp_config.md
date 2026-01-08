# Testing MCP Server Configuration

## Quick Test

Once you've added the `.claude/mcp_settings.json` file, restart Claude Code and you should be able to:

1. **List all available prompts:**
   - Ask Claude: "What prompts are available from the specifyplus-prompts MCP server?"
   - You should see all 13 SpecifyPlus commands (sp.specify, sp.plan, sp.tasks, etc.)

2. **Invoke a prompt with arguments:**
   - Select some text in your editor
   - Ask Claude: "Use the sp.specify prompt with this text: [your text]"
   - Or: "Use sp.plan to create an implementation plan for: [your description]"

3. **Test hot-reload:**
   - Modify a file in `.claude/commands/`
   - The changes should be reflected within 2 seconds without restart

## Example Usage

### Creating a Spec
```
Use the sp.specify prompt to create a spec for: A feature that tracks user login history
```

### Creating a Plan
```
Use the sp.plan prompt to generate an implementation plan for the authentication feature
```

### Generating Tasks
```
Use the sp.tasks prompt to break down the spec in specs/001-authentication/spec.md into tasks
```

## Troubleshooting

If MCP doesn't connect:
1. Check that `uv` is installed: `which uv`
2. Verify the path to `server.py` is correct
3. Check Claude Code logs for MCP connection errors
4. Try running the server manually: `uv run python mcp-servers/specifyplus-prompts/src/specifyplus_prompts/server.py`
