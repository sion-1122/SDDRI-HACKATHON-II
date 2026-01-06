"""MCP server for SpecifyPlus command prompts."""

import argparse
import asyncio
import logging
import os
from pathlib import Path

from fastmcp import FastMCP

from .file_watcher import FileWatcher
from .prompt_loader import PromptLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("SpecifyPlus Prompts")

# Get commands directory from environment or default
_commands_dir = os.getenv("SPECIFYPLUS_COMMANDS_DIR", "./.claude/commands")
COMMANDS_DIR = Path(_commands_dir).resolve()

# Check if file watching is disabled
_no_watch = os.getenv("SPECIFYPLUS_NO_WATCH", "").lower() in ("1", "true", "yes")

# Initialize prompt loader
loader = PromptLoader(COMMANDS_DIR)

# Load all prompts on startup
logger.info(f"Loading prompts from {COMMANDS_DIR}")
prompts = loader.load_all_prompts()
logger.info(f"Loaded {len(prompts)} prompts")

# Register all prompts as MCP prompt resources
for prompt_name, prompt in prompts.items():
    # Create a closure to capture the prompt_name
    def create_prompt_handler(name: str, prompt_obj):
        async def prompt_handler(arguments: str = "") -> str:
            """Handle prompt invocation with arguments."""
            logger.info(
                f"Invoking prompt '{name}' with {len(arguments)} characters of arguments"
            )

            # Get fresh prompt to ensure we have latest content
            current_prompt = loader.get_prompt(name)
            if current_prompt is None:
                logger.error(f"Prompt not found: {name}")
                raise ValueError(f"Prompt not found: {name}")

            # Format with arguments
            return current_prompt.format(arguments)

        return prompt_handler

    # Register the prompt with FastMCP
    handler = create_prompt_handler(prompt_name, prompt)
    mcp.prompt(description=prompt.metadata.description)(handler)

    logger.debug(f"Registered prompt: {prompt_name}")


def main():
    """Start the MCP server."""
    parser = argparse.ArgumentParser(description="SpecifyPlus Prompts MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--host", default="localhost", help="Host for HTTP/SSE transport (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for HTTP/SSE transport (default: 8000)"
    )
    args = parser.parse_args()

    logger.info("Starting SpecifyPlus Prompts MCP server")
    logger.info(f"Commands directory: {COMMANDS_DIR}")
    logger.info(f"Registered {len(prompts)} prompts")
    logger.info(f"Transport: {args.transport}")

    if args.transport in ("http", "sse"):
        logger.info(f"Server URL: http://{args.host}:{args.port}")

    if _no_watch:
        logger.info("File watching disabled (SPECIFYPLUS_NO_WATCH is set)")
    else:
        logger.info("File watching enabled")

    # Start file watcher if enabled
    if not _no_watch:
        watcher = FileWatcher(COMMANDS_DIR, loader)

        # Note: FastMCP's run() doesn't support async context managers yet
        # So we'll start watcher as a background task
        async def start_watcher():
            """Start file watcher in background."""
            await watcher.watch()

        # Get or create event loop
        try:
            loop = asyncio.get_running_loop()
            # Start watcher as background task
            loop.create_task(watcher.watch())
            logger.info("File watcher started")
        except RuntimeError:
            # No running loop, watcher won't start in this mode
            logger.warning("Could not start file watcher - no event loop")

    # Run server with specified transport
    if args.transport == "stdio":
        mcp.run()
    elif args.transport == "http":
        mcp.run(transport="http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
