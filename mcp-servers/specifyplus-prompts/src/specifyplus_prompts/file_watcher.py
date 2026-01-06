"""File watcher for hot-reloading SpecifyPlus command prompts."""

import asyncio
import logging
from pathlib import Path
from typing import Callable

from watchfiles import Change
from watchfiles import awatch

from .prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class FileWatcher:
    """Watches commands directory for file changes and hot-reloads prompts."""

    def __init__(self, commands_dir: Path, loader: PromptLoader):
        """Initialize file watcher.

        Args:
            commands_dir: Path to .claude/commands/ directory
            loader: PromptLoader instance to reload prompts
        """
        self.commands_dir = Path(commands_dir)
        self.loader = loader
        self.stop_event = asyncio.Event()
        self._debounce_changes: set[Path] = set()

    async def watch(self):
        """Watch for file changes and reload prompts.

        Implements 2-second debounce to coalesce rapid changes.
        """
        logger.info(f"Watching for changes in {self.commands_dir}")

        try:
            async for changes in awatch(self.commands_dir, stop_event=self.stop_event):
                # Collect changed files
                for change in changes:
                    file_path = Path(change[1])
                    self._debounce_changes.add(file_path)

                # Debounce: wait 2 seconds for more changes
                await asyncio.sleep(2.0)

                # Process all debounced changes
                await self._process_changes()

                # Clear debounce set
                self._debounce_changes.clear()

        except Exception as e:
            logger.error(f"File watcher error: {e}", exc_info=True)
            # Graceful degradation: log error but don't crash server

    async def _process_changes(self):
        """Process accumulated file changes.

        Handles Change.added, Change.modified, Change.deleted events.
        """
        for file_path in self._debounce_changes:
            try:
                if not file_path.exists():
                    # File was deleted
                    self._handle_deletion(file_path)
                elif file_path.suffix == ".md":
                    # File was added or modified
                    self._handle_addition_or_modification(file_path)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}", exc_info=True)

        # Send list_changed notification if changes were processed
        if self._debounce_changes:
            self._notify_list_changed()

    def _handle_addition_or_modification(self, file_path: Path):
        """Handle file creation or modification.

        Args:
            file_path: Path to changed file
        """
        try:
            # Reload prompt from file
            prompt = self.loader.reload_prompt(file_path)

            if prompt:
                logger.info(f"Reloaded prompt: {prompt.name}")
            else:
                logger.warning(f"Failed to reload prompt: {file_path}")
        except Exception as e:
            logger.error(f"Failed to reload {file_path}: {e}", exc_info=True)

    def _handle_deletion(self, file_path: Path):
        """Handle file deletion.

        Args:
            file_path: Path to deleted file
        """
        try:
            # Calculate prompt name from file path
            rel_path = file_path.relative_to(self.commands_dir)
            name = str(rel_path.with_suffix(""))

            # Remove from cache
            self.loader.remove_prompt(name)
            logger.info(f"Removed prompt: {name}")
        except Exception as e:
            logger.error(f"Failed to remove {file_path}: {e}", exc_info=True)

    def _notify_list_changed(self):
        """Notify clients that prompt list has changed.

        Note: FastMCP doesn't have a built-in list_changed notification API yet.
        This is a placeholder for when the feature is added.
        """
        # TODO: Use FastMCP notification API when available
        logger.info("Prompt list has changed (list_changed notification)")

    def stop(self):
        """Stop the file watcher."""
        logger.info("Stopping file watcher")
        self.stop_event.set()
