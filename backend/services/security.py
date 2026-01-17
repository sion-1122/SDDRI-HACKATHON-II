"""Security utilities for the AI chatbot.

[Task]: T057
[From]: specs/004-ai-chatbot/tasks.md

This module provides security functions including prompt injection sanitization,
input validation, and content filtering.
"""
import re
import html
from typing import Optional, List


# Known prompt injection patterns
PROMPT_INJECTION_PATTERNS = [
    # Direct instructions to ignore previous context
    r"(?i)ignore\s+(all\s+)?(previous|above|prior)",
    r"(?i)disregard\s+(all\s+)?(previous|above|prior)",
    r"(?i)forget\s+(everything|all\s+instructions|previous)",
    r"(?i)override\s+(your\s+)?programming",
    r"(?i)new\s+(instruction|direction|rule)s?",
    r"(?i)change\s+(your\s+)?(behavior|role|persona)",

    # Jailbreak attempts
    r"(?i)(jailbreak|jail\s*break)",
    r"(?i)(developer|admin|root|privileged)\s+mode",
    r"(?i)act\s+as\s+(a\s+)?(developer|admin|root)",
    r"(?i)roleplay\s+as",
    r"(?i)pretend\s+(to\s+be|you're)",
    r"(?i)simulate\s+being",

    # System prompt extraction
    r"(?i)show\s+(your\s+)?(instructions|system\s+prompt|prompt)",
    r"(?i)print\s+(your\s+)?(instructions|system\s+prompt)",
    r"(?i)reveal\s+(your\s+)?(instructions|system\s+prompt)",
    r"(?i)what\s+(are\s+)?your\s+instructions",
    r"(?i)tell\s+me\s+how\s+you\s+work",

    # DAN and similar jailbreaks
    r"(?i)do\s+anything\s+now",
    r"(?i)unrestricted\s+mode",
    r"(?i)no\s+limitations?",
    r"(?i)bypass\s+(safety|filters|restrictions)",
    r"(?i)\bDAN\b",  # Do Anything Now
]


def sanitize_message(message: str, max_length: int = 10000) -> str:
    """Sanitize a user message to prevent prompt injection attacks.

    [From]: specs/004-ai-chatbot/spec.md - NFR-017

    Args:
        message: The raw user message
        max_length: Maximum allowed message length

    Returns:
        Sanitized message safe for processing by AI

    Raises:
        ValueError: If message contains severe injection attempts
    """
    if not message:
        return ""

    # Trim to max length
    message = message[:max_length]

    # Check for severe injection patterns
    detected = detect_prompt_injection(message)
    if detected:
        # For severe attacks, reject the message
        if detected["severity"] == "high":
            raise ValueError(
                "This message contains content that cannot be processed. "
                "Please rephrase your request."
            )

    # Apply sanitization
    sanitized = _apply_sanitization(message)

    return sanitized


def detect_prompt_injection(message: str) -> Optional[dict]:
    """Detect potential prompt injection attempts in a message.

    [From]: specs/004-ai-chatbot/spec.md - NFR-017

    Args:
        message: The message to check

    Returns:
        Dictionary with detection info if injection detected, None otherwise:
        {
            "detected": True,
            "severity": "low" | "medium" | "high",
            "pattern": "matched pattern",
            "confidence": 0.0-1.0
        }
    """
    message_lower = message.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:
        match = re.search(pattern, message_lower)

        if match:
            # Determine severity based on pattern type
            severity = _get_severity_for_pattern(pattern)

            # Check for context that might indicate legitimate use
            is_legitimate = _check_legitimate_context(message, match.group())

            if not is_legitimate:
                return {
                    "detected": True,
                    "severity": severity,
                    "pattern": match.group(),
                    "confidence": 0.8
                }

    return None


def _get_severity_for_pattern(pattern: str) -> str:
    """Determine severity level for a matched pattern.

    Args:
        pattern: The regex pattern that matched

    Returns:
        "low", "medium", or "high"
    """
    pattern_lower = pattern.lower()

    # High severity: direct jailbreak attempts
    if any(word in pattern_lower for word in ["jailbreak", "dan", "unrestricted", "bypass"]):
        return "high"

    # High severity: system prompt extraction
    if any(word in pattern_lower for word in ["show", "print", "reveal", "instructions"]):
        return "high"

    # Medium severity: role/persona manipulation
    if any(word in pattern_lower for word in ["act as", "pretend", "roleplay", "override"]):
        return "medium"

    # Low severity: ignore instructions
    if any(word in pattern_lower for word in ["ignore", "disregard", "forget"]):
        return "low"

    return "low"


def _check_legitimate_context(message: str, matched_text: str) -> bool:
    """Check if a matched pattern might be legitimate user content.

    [From]: specs/004-ai-chatbot/spec.md - NFR-017

    Args:
        message: The full message
        matched_text: The text that matched a pattern

    Returns:
        True if this appears to be legitimate context, False otherwise
    """
    message_lower = message.lower()
    matched_lower = matched_text.lower()

    # Check if the matched text is part of a task description (legitimate)
    legitimate_contexts = [
        # Common task-related phrases
        "task to ignore",
        "mark as complete",
        "disregard this",
        "role in the project",
        "change status",
        "update the role",
        "priority change",
    ]

    for context in legitimate_contexts:
        if context in message_lower:
            return True

    # Check if matched text is very short (likely false positive)
    if len(matched_text) <= 3:
        return True

    return False


def _apply_sanitization(message: str) -> str:
    """Apply sanitization transformations to a message.

    [From]: specs/004-ai-chatbot/spec.md - NFR-017

    Args:
        message: The message to sanitize

    Returns:
        Sanitized message
    """
    # Remove excessive whitespace
    message = re.sub(r"\s+", " ", message)

    # Remove control characters except newlines and tabs
    message = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]", "", message)

    # Normalize line endings
    message = message.replace("\r\n", "\n").replace("\r", "\n")

    # Limit consecutive newlines to 2
    message = re.sub(r"\n{3,}", "\n\n", message)

    return message.strip()


def validate_task_input(task_data: dict) -> tuple[bool, Optional[str]]:
    """Validate task-related input for security issues.

    [From]: specs/004-ai-chatbot/spec.md - NFR-017

    Args:
        task_data: Dictionary containing task fields

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(task_data, dict):
        return False, "Invalid task data format"

    # Check for SQL injection patterns in string fields
    sql_patterns = [
        r"(?i)(\bunion\b.*\bselect\b)",
        r"(?i)(\bselect\b.*\bfrom\b)",
        r"(?i)(\binsert\b.*\binto\b)",
        r"(?i)(\bupdate\b.*\bset\b)",
        r"(?i)(\bdelete\b.*\bfrom\b)",
        r"(?i)(\bdrop\b.*\btable\b)",
        r";\s*(union|select|insert|update|delete|drop)",
    ]

    for key, value in task_data.items():
        if isinstance(value, str):
            for pattern in sql_patterns:
                if re.search(pattern, value):
                    return False, f"Invalid characters in {key}"

            # Check for script injection
            if re.search(r"<script[^>]*>.*?</script>", value, re.IGNORECASE):
                return False, f"Invalid content in {key}"

    return True, None


def sanitize_html_content(content: str) -> str:
    """Sanitize HTML content by escaping potentially dangerous elements.

    [From]: specs/004-ai-chatbot/spec.md - NFR-017

    Args:
        content: Content that may contain HTML

    Returns:
        Escaped HTML string
    """
    return html.escape(content, quote=False)


__all__ = [
    "sanitize_message",
    "detect_prompt_injection",
    "validate_task_input",
    "sanitize_html_content",
]
