"""Uvicorn configuration for the FastAPI application.

This configuration ensures the file watcher only monitors source code,
not the virtual environment or dependencies.
"""
from uvicorn.config import Config
from uvicorn.supervisors.watchfilesreload import WatchFilesReload

# Configure which directories to watch for changes
# Only watch the actual application code, not .venv or dependencies
reload_dirs = [
    ".",  # Current directory (backend/)
    "api",
    "ai_agent",
    "core",
    "models",
    "mcp_server",
    "services",
    "tests",
]

# Explicitly exclude directories from watching
reload_excludes = [
    ".venv",
    ".venv/lib",
    ".venv/lib64",
    ".venv/lib64/python*",
    "__pycache__",
    "*.pyc",
    ".git",
    ".pytest_cache",
    "node_modules",
    ".ruff_cache",
    "*.egg-info",
]

# Export configuration for uvicorn command
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=reload_dirs,
        reload_excludes=reload_excludes,
        log_level="info"
    )
