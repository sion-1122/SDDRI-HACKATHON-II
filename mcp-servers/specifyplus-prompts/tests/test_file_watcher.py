"""Unit tests for FileWatcher."""

import asyncio
from pathlib import Path

import pytest

from specifyplus_prompts.file_watcher import FileWatcher
from specifyplus_prompts.prompt_loader import PromptLoader


class TestFileWatcher:
    """Test FileWatcher class."""

    @pytest.fixture
    def tmp_loader(self, tmp_path):
        """Create a PromptLoader with temp directory."""
        return PromptLoader(tmp_path)

    def test_initialization(self, tmp_path, tmp_loader):
        """Test FileWatcher initialization."""
        watcher = FileWatcher(tmp_path, tmp_loader)
        assert watcher.commands_dir == tmp_path
        assert watcher.loader == tmp_loader
        assert not watcher.stop_event.is_set()

    def test_stop(self, tmp_path, tmp_loader):
        """Test stopping the watcher."""
        watcher = FileWatcher(tmp_path, tmp_loader)
        assert not watcher.stop_event.is_set()

        watcher.stop()
        assert watcher.stop_event.is_set()

    @pytest.mark.asyncio
    async def test_handle_addition(self, tmp_path, tmp_loader):
        """Test handling file addition."""
        watcher = FileWatcher(tmp_path, tmp_loader)

        # Create a new file
        new_file = tmp_path / "new.md"
        new_file.write_text(
            """---
description: New prompt
---

Content with $ARGUMENTS
"""
        )

        # Handle addition
        watcher._handle_addition_or_modification(new_file)

        # Verify prompt was loaded
        prompt = tmp_loader.get_prompt("new")
        assert prompt is not None
        assert prompt.metadata.description == "New prompt"

    @pytest.mark.asyncio
    async def test_handle_modification(self, tmp_path, tmp_loader):
        """Test handling file modification."""
        # Create initial file
        test_file = tmp_path / "test.md"
        test_file.write_text(
            """---
description: Original
---

Content with $ARGUMENTS
"""
        )
        tmp_loader.load_all_prompts()

        watcher = FileWatcher(tmp_path, tmp_loader)

        # Modify file
        test_file.write_text(
            """---
description: Modified
---

Updated content with $ARGUMENTS
"""
        )

        # Handle modification
        watcher._handle_addition_or_modification(test_file)

        # Verify prompt was reloaded
        prompt = tmp_loader.get_prompt("test")
        assert prompt is not None
        assert prompt.metadata.description == "Modified"
        assert "Updated content" in prompt.template

    @pytest.mark.asyncio
    async def test_handle_deletion(self, tmp_path, tmp_loader):
        """Test handling file deletion."""
        # Create initial file
        test_file = tmp_path / "test.md"
        test_file.write_text(
            """---
description: Test
---

Content with $ARGUMENTS
"""
        )
        tmp_loader.load_all_prompts()

        # Verify file exists in cache
        assert tmp_loader.get_prompt("test") is not None

        watcher = FileWatcher(tmp_path, tmp_loader)

        # Handle deletion (file already deleted)
        watcher._handle_deletion(test_file)

        # Verify prompt was removed from cache
        assert tmp_loader.get_prompt("test") is None

    @pytest.mark.asyncio
    async def test_graceful_error_handling(self, tmp_path, tmp_loader):
        """Test graceful error handling in file operations."""
        watcher = FileWatcher(tmp_path, tmp_loader)

        # Create file with invalid YAML
        bad_file = tmp_path / "bad.md"
        bad_file.write_text(
            """---
description: Test
invalid yaml: [unclosed
---

Content
"""
        )

        # Should handle error gracefully
        watcher._handle_addition_or_modification(bad_file)

        # Prompt should not be in cache
        assert tmp_loader.get_prompt("bad") is None

    @pytest.mark.asyncio
    async def test_non_markdown_files_ignored(self, tmp_path, tmp_loader):
        """Test that non-.md files are ignored."""
        watcher = FileWatcher(tmp_path, tmp_loader)

        # Create non-markdown file
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Not a markdown file")

        # Add to debounce changes
        watcher._debounce_changes.add(txt_file)

        # Process changes - should ignore .txt file
        await watcher._process_changes()

        # Verify no prompt was created for .txt file
        assert tmp_loader.get_prompt("test") is None


class TestPromptLoaderReload:
    """Test PromptLoader reload and remove methods."""

    def test_reload_prompt(self, tmp_path):
        """Test reloading a specific prompt."""
        # Create initial file
        test_file = tmp_path / "test.md"
        test_file.write_text(
            """---
description: Original
---

Original content
"""
        )

        loader = PromptLoader(tmp_path)
        loader.load_all_prompts()

        assert loader.get_prompt("test").metadata.description == "Original"

        # Modify file
        test_file.write_text(
            """---
description: Reloaded
---

Reloaded content
"""
        )

        # Reload prompt
        loader.reload_prompt(test_file)

        # Verify reloaded
        assert loader.get_prompt("test").metadata.description == "Reloaded"
        assert "Reloaded content" in loader.get_prompt("test").template

    def test_reload_nonexistent_file(self, tmp_path):
        """Test reloading a file that doesn't exist."""
        loader = PromptLoader(tmp_path)

        result = loader.reload_prompt(tmp_path / "nonexistent.md")
        assert result is None

    def test_remove_prompt(self, tmp_path):
        """Test removing a prompt from cache."""
        # Create file
        test_file = tmp_path / "test.md"
        test_file.write_text(
            """---
description: Test
---

Content
"""
        )

        loader = PromptLoader(tmp_path)
        loader.load_all_prompts()

        # Verify prompt exists
        assert loader.get_prompt("test") is not None

        # Remove prompt
        result = loader.remove_prompt("test")
        assert result is True

        # Verify removed
        assert loader.get_prompt("test") is None

    def test_remove_nonexistent_prompt(self, tmp_path):
        """Test removing a prompt that doesn't exist."""
        loader = PromptLoader(tmp_path)

        result = loader.remove_prompt("nonexistent")
        assert result is False
