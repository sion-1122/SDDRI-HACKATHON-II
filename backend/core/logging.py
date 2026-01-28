"""Structured JSON logging configuration.

Provides structured logging with JSON format, correlation IDs, and log levels
for cloud-native deployment and aggregation.

[Task]: T012 - Phase IV Kubernetes deployment
[From]: specs/006-k8s-deployment/plan.md
"""
import logging
import logging.config
import json
import sys
from datetime import datetime
import traceback
from typing import Any, Dict
from contextvars import ContextVar

# Context variable for correlation ID (e.g., request ID)
CORRELATION_ID: ContextVar[str] = ContextVar("correlation_id", default="")


class JSONFormatter(logging.Formatter):
    """Structured JSON formatter for cloud-native logging.

    Formats log records as JSON with timestamp, level, correlation ID, and message.
    Compatible with log aggregators like Elasticsearch, Splunk, and Cloud Logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        # Create base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if available
        correlation_id = CORRELATION_ID.get()
        if correlation_id:
            log_entry["correlation_id"] = correlation_id

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add process info (useful for container logging)
        log_entry["process"] = {
            "pid": record.process,
            "name": record.processName,
        }

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> None:
    """Configure structured JSON logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger with JSON handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    handler.setLevel(log_level)

    # Root logger configuration
    logging.root.setLevel(log_level)
    logging.root.handlers.clear()
    logging.root.addHandler(handler)

    # Configure uvicorn logging
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)

    # Configure SQLModel logging
    logging.getLogger("sqlmodel").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Configure FastAPI logging
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Log startup
    logger = logging.getLogger(__name__)
    logger.info(f"Structured logging configured at {level} level")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the configured JSON formatter.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def with_correlation_id(correlation_id: str) -> Dict[str, Any]:
    """Create a context dict with correlation ID for logging.

    Usage:
        logger.info("Processing request", extra={"extra_fields": with_correlation_id(request_id)})

    Args:
        correlation_id: Correlation ID (e.g., request ID, session ID)

    Returns:
        Dict with extra_fields for logging
    """
    token = CORRELATION_ID.set(correlation_id)
    return {"extra_fields": {"correlation_id": correlation_id}}


def clear_correlation_id() -> None:
    """Clear the correlation ID context."""
    CORRELATION_ID.set("")
