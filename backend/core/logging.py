"""Clean logging configuration for development.

Provides simple, readable logs for development with optional JSON mode for production.
"""
import logging
import logging.config
import sys
from typing import Optional


class CleanFormatter(logging.Formatter):
    """Simple, clean formatter for readable development logs."""

    # Color codes for terminal output
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",       # Reset
    }

    def __init__(self, use_colors: bool = True):
        """Initialize formatter.

        Args:
            use_colors: Whether to use ANSI color codes (disable for file logs)
        """
        self.use_colors = use_colors
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as a clean, readable string."""
        level = record.levelname
        module = record.name.split(".")[-1] if "." in record.name else record.name
        message = record.getMessage()

        # Build the log line
        if self.use_colors:
            color = self.COLORS.get(level, "")
            reset = self.COLORS["RESET"]
            formatted = f"{color}{level:8}{reset} {module:20} | {message}"
        else:
            formatted = f"{level:8} {module:20} | {message}"

        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logging(
    level: str = "INFO",
    json_mode: bool = False,
    quiet_sql: bool = True
) -> None:
    """Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_mode: Use structured JSON logging (for production)
        quiet_sql: Suppress verbose SQL query logs
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    logging.root.setLevel(log_level)
    logging.root.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Set formatter
    if json_mode:
        # Import JSON formatter for production
        import json
        from datetime import datetime

        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    log_entry["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_entry)

        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(CleanFormatter(use_colors=True))

    logging.root.addHandler(handler)

    # Configure third-party loggers
    if quiet_sql:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
        logging.getLogger("sqlmodel").setLevel(logging.WARNING)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Log startup message (but only in non-JSON mode)
    if not json_mode:
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configured at {level} level")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
