"""NLP service for extracting task attributes from natural language.

[Task]: T029
[From]: specs/007-intermediate-todo-features/tasks.md (User Story 2)

This service provides:
- Tag extraction from natural language ("tagged with X", "add tag Y")
- Priority detection patterns
- Due date parsing patterns
"""
from typing import List, Optional
import re


def extract_tags(text: str) -> List[str]:
    """Extract tags from natural language input.

    [Task]: T029, T031 - Tag extraction from natural language

    Supports patterns:
    - "tagged with X", "tags X", "tag X"
    - "add tag X", "with tag X"
    - "labeled X"
    - Hashtags: "#tagname"

    Args:
        text: Natural language input text

    Returns:
        List of extracted tag names (lowercased, deduplicated)

    Examples:
        >>> extract_tags("Add task tagged with work and urgent")
        ['work', 'urgent']
        >>> extract_tags("Buy groceries #shopping #home")
        ['shopping', 'home']
        >>> extract_tags("Create task with label review")
        ['review']
    """
    if not text:
        return []

    tags = set()
    text_lower = text.lower()

    # Pattern 1: Hashtag extraction
    hashtag_pattern = r'#(\w+)'
    hashtags = re.findall(hashtag_pattern, text)
    tags.update(hashtags)

    # Pattern 2: "tagged with X and Y" or "tags X, Y"
    tagged_with_pattern = r'(?:tagged|tags?|labeled?)\s+(?:with\s+)?(?:[,\s]+)?(\w+(?:\s+(?:and|,)\s+\w+)*)'
    matches = re.findall(tagged_with_pattern, text_lower)
    for match in matches:
        # Split by common separators
        parts = re.split(r'\s+(?:and|,)\s+', match)
        tags.update(parts)

    # Pattern 3: "add tag X" or "with tag X"
    add_tag_pattern = r'(?:add|with|has)\s+tag\s+(\w+)'
    matches = re.findall(add_tag_pattern, text_lower)
    tags.update(matches)

    # Pattern 4: "label X"
    label_pattern = r'(?:label|categorize|file\s*(?:under)?)(?:ed|s+as)?\s+(\w+)'
    matches = re.findall(label_pattern, text_lower)
    tags.update(matches)

    # Filter out common non-tag words
    excluded_words = {
        'a', 'an', 'the', 'with', 'for', 'and', 'or', 'but', 'not',
        'this', 'that', 'to', 'of', 'in', 'on', 'at', 'by', 'as', 'is',
        'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
        'might', 'must', 'can', 'need', 'want', 'like', 'such'
    }

    filtered_tags = [tag for tag in tags if tag not in excluded_words and len(tag) > 1]

    return sorted(list(filtered_tags))


def normalize_tag_name(tag: str) -> str:
    """Normalize tag name for consistency.

    Args:
        tag: Raw tag name from user input

    Returns:
        Normalized tag name (lowercase, trimmed, no special chars)
    """
    # Remove special characters except hyphens and underscores
    normalized = re.sub(r'[^\w\s-]', '', tag)
    # Convert to lowercase and trim
    normalized = normalized.lower().strip()
    # Replace spaces with hyphens for multi-word tags
    normalized = re.sub(r'\s+', '-', normalized)
    return normalized


def extract_tags_from_task_data(
    title: str,
    description: Optional[str] = None
) -> List[str]:
    """Extract tags from task title and description.

    Convenience function that extracts tags from both title and description.

    Args:
        title: Task title
        description: Optional task description

    Returns:
        List of extracted and normalized tag names
    """
    text = title
    if description:
        text = f"{title} {description}"

    raw_tags = extract_tags(text)
    # Normalize each tag
    return [normalize_tag_name(tag) for tag in raw_tags]
