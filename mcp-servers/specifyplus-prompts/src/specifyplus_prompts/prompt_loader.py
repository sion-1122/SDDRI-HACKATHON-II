"""Prompt loader for SpecifyPlus command files."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Callable

from frontmatter import Frontmatter
import yaml
from pydantic import ValidationError

from .models import Prompt, PromptMetadata

logger = logging.getLogger(__name__)


class PromptLoader:
    """Loads and caches SpecifyPlus command prompts from file system."""

    def __init__(self, commands_dir: str | Path):
        """Initialize prompt loader with commands directory path.

        Args:
            commands_dir: Path to .claude/commands/ directory
        """
        self.commands_dir = Path(commands_dir)
        self._cache: dict[str, Prompt] = {}

    def scan_commands(self) -> list[Path]:
        """Recursively find all markdown files in commands directory.

        Returns:
            List of paths to .md files
        """
        if not self.commands_dir.exists():
            logger.warning(f"Commands directory does not exist: {self.commands_dir}")
            return []

        return list(self.commands_dir.rglob("*.md"))

    def load_prompt_from_file(self, file_path: Path) -> Prompt:
        """Load and parse a single command file.

        Args:
            file_path: Path to markdown command file

        Returns:
            Prompt object with parsed metadata and template

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
            ValueError: If file is too large or missing required fields
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Command file not found: {file_path}")

        # Check file size (100KB limit)
        size_bytes = file_path.stat().st_size
        if size_bytes > 100_000:
            raise ValueError(f"File too large ({size_bytes} bytes): {file_path}")

        # Read and parse file
        try:
            with open(file_path, "r") as f:
                content = f.read()
            post = Frontmatter.read(content)
            # Frontmatter.read returns dict with 'attributes' (metadata) and 'body'
            metadata = post.get("attributes", {})
            body = post.get("body", "")
        except PermissionError as e:
            raise PermissionError(f"Cannot read file: {file_path}") from e
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to parse {file_path}: {e}") from e

        # Validate required fields
        if "description" not in metadata:
            raise ValueError(f"Missing required 'description' field in {file_path}")

        # Extract prompt name (filename without extension, relative to commands dir)
        rel_path = file_path.relative_to(self.commands_dir)
        name = str(rel_path.with_suffix(""))

        # Build metadata object
        try:
            prompt_metadata = PromptMetadata(
                description=metadata["description"],
                handoffs=metadata.get("handoffs", []),
                send=metadata.get("send", False),
                raw_metadata=metadata,
            )
        except ValidationError as e:
            raise ValueError(f"Invalid metadata in {file_path}: {e}") from e

        # Create prompt object
        return Prompt(
            name=name,
            file_path=str(file_path),
            metadata=prompt_metadata,
            template=body,
            modified_at=datetime.fromtimestamp(file_path.stat().st_mtime),
            size_bytes=size_bytes,
        )

    def load_all_prompts(self, on_error: Callable[[str, Exception], None] | None = None) -> dict[str, Prompt]:
        """Scan and cache all command files.

        Args:
            on_error: Optional callback for load errors (file_path, exception)

        Returns:
            Dictionary mapping prompt names to Prompt objects
        """
        self._cache.clear()

        for file_path in self.scan_commands():
            try:
                prompt = self.load_prompt_from_file(file_path)
                self._cache[prompt.name] = prompt
                logger.debug(f"Loaded prompt: {prompt.name}")
            except (FileNotFoundError, PermissionError, ValueError, yaml.YAMLError) as e:
                logger.error(f"Failed to load {file_path}: {e}")
                if on_error:
                    on_error(str(file_path), e)
                # Skip malformed files and continue
                continue

        logger.info(f"Loaded {len(self._cache)} prompts from {self.commands_dir}")
        return self._cache

    def get_prompt(self, name: str) -> Prompt | None:
        """Retrieve prompt from cache by name.

        Args:
            name: Prompt name (e.g., "sp.specify")

        Returns:
            Prompt object or None if not found
        """
        return self._cache.get(name)

    def list_prompts(self) -> dict[str, str]:
        """List all cached prompts with descriptions.

        Returns:
            Dictionary mapping prompt names to descriptions
        """
        return {name: prompt.metadata.description for name, prompt in self._cache.items()}

    def reload_prompt(self, file_path: Path) -> Prompt | None:
        """Reload a specific prompt from file system.

        Args:
            file_path: Path to command file to reload

        Returns:
            Reloaded Prompt object or None if reload failed
        """
        try:
            prompt = self.load_prompt_from_file(file_path)
            self._cache[prompt.name] = prompt
            logger.debug(f"Reloaded prompt: {prompt.name}")
            return prompt
        except (FileNotFoundError, PermissionError, ValueError, yaml.YAMLError) as e:
            logger.error(f"Failed to reload {file_path}: {e}")
            return None

    def remove_prompt(self, name: str) -> bool:
        """Remove a prompt from cache.

        Args:
            name: Prompt name to remove

        Returns:
            True if prompt was removed, False if not found
        """
        if name in self._cache:
            del self._cache[name]
            logger.debug(f"Removed prompt: {name}")
            return True
        return False
