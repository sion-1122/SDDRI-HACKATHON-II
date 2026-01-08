#!/bin/bash
# Wrapper script to start the SpecifyPlus Prompts MCP server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR" || exit 1

# Parse arguments
TRANSPORT="${SPECIFYPLUS_TRANSPORT:-http}"
HOST="${SPECIFYPLUS_HOST:-localhost}"
PORT="${SPECIFYPLUS_PORT:-8000}"

# Activate the virtual environment and run the server as a module
source .venv/bin/activate && python -m specifyplus_prompts.server --transport "$TRANSPORT" --host "$HOST" --port "$PORT"
