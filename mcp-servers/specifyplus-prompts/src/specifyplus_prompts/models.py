"""Pydantic models for SpecifyPlus prompts and metadata."""

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Handoff(BaseModel):
    """Agent handoff configuration from frontmatter."""

    agent: str = Field(..., description="Target agent name (e.g., 'sp.plan')")
    label: str = Field(..., description="Human-readable label for the handoff")
    prompt: str | None = Field(None, description="Optional prompt template for handoff")
    send: bool = Field(False, description="Whether to send immediately")


class PromptMetadata(BaseModel):
    """YAML frontmatter from SpecifyPlus command files."""

    model_config = ConfigDict(extra="ignore")

    description: str = Field(..., description="Command description")
    handoffs: list[Handoff] = Field(default_factory=list, description="Agent handoffs")
    send: bool = Field(False, description="Send to handoff immediately")
    raw_metadata: dict[str, Any] = Field(default_factory=dict, description="All frontmatter fields")


class Prompt(BaseModel):
    """Complete SpecifyPlus command prompt."""

    model_config = ConfigDict()

    name: str = Field(..., description="Prompt name (filename without extension)")
    file_path: str = Field(..., description="Absolute path to command file")
    metadata: PromptMetadata = Field(..., description="Parsed frontmatter")
    template: str = Field(..., description="Markdown body template")
    modified_at: datetime = Field(..., description="File modification time")
    size_bytes: int = Field(..., description="File size in bytes", le=100_000)

    def format(self, arguments: str = "") -> str:
        """Replace $ARGUMENTS placeholder in template.

        Args:
            arguments: Arguments string to substitute for $ARGUMENTS placeholder

        Returns:
            Formatted template with $ARGUMENTS replaced
        """
        return self.template.replace("$ARGUMENTS", arguments)
