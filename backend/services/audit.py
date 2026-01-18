"""Audit logging service for MCP tool invocations.

[Task]: T058
[From]: specs/004-ai-chatbot/tasks.md

This module provides audit logging for all MCP tool invocations to track
usage patterns, detect abuse, and maintain compliance records.
"""
import logging
import json
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlmodel import Session

from core.database import engine


# Configure audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Audit log handler (separate from main logs)
audit_handler = logging.FileHandler("logs/audit.log")
audit_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s'
))
audit_logger.addHandler(audit_handler)


def log_tool_invocation(
    tool_name: str,
    user_id: str | UUID,
    args: dict[str, Any],
    result: dict[str, Any],
    conversation_id: Optional[str | UUID] = None,
    execution_time_ms: Optional[float] = None,
    error: Optional[str] = None
) -> None:
    """Log an MCP tool invocation for audit purposes.

    [From]: specs/004-ai-chatbot/spec.md - NFR-018

    Args:
        tool_name: Name of the tool that was invoked
        user_id: ID of the user who invoked the tool
        args: Arguments passed to the tool
        result: Result returned by the tool
        conversation_id: Optional conversation context
        execution_time_ms: Optional execution time in milliseconds
        error: Optional error message if invocation failed
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "tool_name": tool_name,
        "user_id": str(user_id),
        "conversation_id": str(conversation_id) if conversation_id else None,
        "success": error is None,
        "error": error,
        "execution_time_ms": execution_time_ms,
        "args_summary": _summarize_args(tool_name, args),
        "result_summary": _summarize_result(result)
    }

    # Log to file
    audit_logger.info(json.dumps(log_entry))

    # Also log to database for querying (if needed)
    _persist_audit_log(log_entry)


def _summarize_args(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Create a summary of tool arguments for logging.

    [From]: T058 - Add audit logging for all MCP tool invocations

    Args:
        tool_name: Name of the tool
        args: Full arguments dict

    Returns:
        Summarized arguments (sanitized for sensitive data)
    """
    # Don't log full user content for privacy
    if "message" in args:
        return {"message_length": len(str(args.get("message", "")))}

    # For task operations, log relevant info
    if tool_name in ["add_task", "update_task", "complete_task", "delete_task"]:
        summary = {}
        if "task_id" in args:
            summary["task_id"] = str(args["task_id"])
        if "title" in args:
            summary["title"] = args["title"][:50]  # Truncate long titles
        if "completed" in args:
            summary["completed"] = args["completed"]
        if "priority" in args:
            summary["priority"] = args["priority"]
        return summary

    # For list_tasks, log filters
    if tool_name == "list_tasks":
        summary = {}
        if "status" in args:
            summary["status"] = args["status"]
        if "limit" in args:
            summary["limit"] = args["limit"]
        return summary

    # Default: return all args (tool-specific sanitization could be added)
    return args


def _summarize_result(result: dict[str, Any]) -> dict[str, Any]:
    """Create a summary of tool result for logging.

    [From]: T058 - Add audit logging for all MCP tool invocations

    Args:
        result: Full result dict from tool

    Returns:
        Summarized result
    """
    if not isinstance(result, dict):
        return {"result_type": type(result).__name__}

    summary = {}

    # Extract key fields
    if "success" in result:
        summary["success"] = result["success"]

    if "error" in result:
        summary["error"] = result["error"]

    if "task" in result:
        task = result["task"]
        summary["task_id"] = task.get("id")
        summary["task_title"] = task.get("title", "")[:50] if task.get("title") else None

    if "tasks" in result:
        tasks = result.get("tasks", [])
        summary["task_count"] = len(tasks) if isinstance(tasks, list) else 0

    if "updated_count" in result:
        summary["updated_count"] = result["updated_count"]

    if "deleted_count" in result:
        summary["deleted_count"] = result["deleted_count"]

    if "message" in result:
        # Truncate long messages
        msg = result["message"]
        summary["message"] = msg[:100] + "..." if len(msg) > 100 else msg

    return summary


def _persist_audit_log(log_entry: dict) -> None:
    """Persist audit log to database for querying.

    [From]: T058 - Add audit logging for all MCP tool invocations

    Args:
        log_entry: The audit log entry to persist
    """
    # Note: This could be extended to write to an audit_logs table
    # For now, file-based logging is sufficient
    pass


def get_user_activity_summary(
    user_id: str | UUID,
    limit: int = 100
) -> list[dict[str, Any]]:
    """Get a summary of user activity from audit logs.

    [From]: T058 - Add audit logging for all MCP tool invocations

    Args:
        user_id: User ID to get activity for
        limit: Maximum number of entries to return

    Returns:
        List of audit log entries for the user
    """
    # Read audit log file and filter by user_id
    try:
        with open("logs/audit.log", "r") as f:
            user_entries = []
            for line in f:
                try:
                    entry = json.loads(line.split(" | ", 2)[-1])
                    if entry.get("user_id") == str(user_id):
                        user_entries.append(entry)
                        if len(user_entries) >= limit:
                            break
                except (json.JSONDecodeError, IndexError):
                    continue
            return user_entries
    except FileNotFoundError:
        return []


# Decorator for automatic audit logging of MCP tools
def audit_log(tool_name: Optional[str] = None):
    """Decorator to automatically log MCP tool invocations.

    [From]: T058 - Add audit logging for all MCP tool invocations

    Args:
        tool_name: Optional override for tool name (defaults to function name)

    Usage:
        @audit_log("add_task")
        async def add_task(user_id: str, title: str, ...):
            ...
    """
    import functools
    import time

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            name = tool_name or func.__name__
            start_time = time.time()

            # Extract user_id from args/kwargs
            user_id = kwargs.get("user_id") or (args[0] if args else None)

            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000

                log_tool_invocation(
                    tool_name=name,
                    user_id=user_id or "unknown",
                    args=kwargs,
                    result=result,
                    execution_time_ms=execution_time
                )
                return result

            except Exception as e:
                execution_time = (time.time() - start_time) * 1000

                log_tool_invocation(
                    tool_name=name,
                    user_id=user_id or "unknown",
                    args=kwargs,
                    result={},
                    execution_time_ms=execution_time,
                    error=str(e)
                )
                raise

        return wrapper
    return decorator


__all__ = [
    "log_tool_invocation",
    "get_user_activity_summary",
    "audit_log",
]
