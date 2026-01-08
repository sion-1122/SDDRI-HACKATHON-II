"""Unit tests for PromptLoader and models."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from specifyplus_prompts.models import Handoff, Prompt, PromptMetadata
from specifyplus_prompts.prompt_loader import PromptLoader


class TestPromptMetadata:
    """Test PromptMetadata model validation."""

    def test_required_fields(self):
        """Test that description field is required."""
        with pytest.raises(ValueError):
            PromptMetadata()

    def test_valid_metadata(self):
        """Test creating valid PromptMetadata."""
        metadata = PromptMetadata(description="Test description")
        assert metadata.description == "Test description"
        assert metadata.handoffs == []
        assert metadata.send is False

    def test_handoffs_field(self):
        """Test handoffs list."""
        handoff = Handoff(agent="sp.plan", label="Build Plan")
        metadata = PromptMetadata(
            description="Test", handoffs=[handoff], send=True
        )
        assert len(metadata.handoffs) == 1
        assert metadata.handoffs[0].agent == "sp.plan"
        assert metadata.send is True


class TestHandoff:
    """Test Handoff model."""

    def test_required_fields(self):
        """Test that agent and label are required."""
        with pytest.raises(ValueError):
            Handoff()

    def test_valid_handoff(self):
        """Test creating valid Handoff."""
        handoff = Handoff(agent="sp.plan", label="Build Plan")
        assert handoff.agent == "sp.plan"
        assert handoff.label == "Build Plan"
        assert handoff.prompt is None
        assert handoff.send is False


class TestPrompt:
    """Test Prompt model."""

    def test_format_method(self):
        """Test format() method replaces $ARGUMENTS."""
        prompt = Prompt(
            name="test",
            file_path="/tmp/test.md",
            metadata=PromptMetadata(description="Test"),
            template="Hello $ARGUMENTS world",
            modified_at=datetime.now(),
            size_bytes=100,
        )
        result = prompt.format("beautiful")
        assert result == "Hello beautiful world"

    def test_format_empty_arguments(self):
        """Test format() with empty arguments."""
        prompt = Prompt(
            name="test",
            file_path="/tmp/test.md",
            metadata=PromptMetadata(description="Test"),
            template="Hello $ARGUMENTS world",
            modified_at=datetime.now(),
            size_bytes=100,
        )
        result = prompt.format("")
        assert result == "Hello  world"


class TestPromptLoader:
    """Test PromptLoader class."""

    def test_init_with_directory(self, tmp_path):
        """Test initializing loader with commands directory."""
        loader = PromptLoader(tmp_path)
        assert loader.commands_dir == tmp_path
        assert loader._cache == {}

    def test_scan_empty_directory(self, tmp_path):
        """Test scanning directory with no markdown files."""
        loader = PromptLoader(tmp_path)
        files = loader.scan_commands()
        assert files == []

    def test_scan_with_markdown_files(self, tmp_path):
        """Test scanning directory with markdown files."""
        (tmp_path / "test.md").touch()
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.md").touch()
        (tmp_path / "readme.txt").touch()

        loader = PromptLoader(tmp_path)
        files = loader.scan_commands()

        assert len(files) == 2
        assert (tmp_path / "test.md") in files
        assert (tmp_path / "subdir" / "nested.md") in files
        assert (tmp_path / "readme.txt") not in files

    def test_load_valid_command_file(self, tmp_path):
        """Test loading a valid command file."""
        content = """---
description: Test command
handoffs:
  - agent: sp.plan
    label: Build Plan
---

## Test Content

This is a test prompt with $ARGUMENTS placeholder.
"""
        cmd_file = tmp_path / "test.md"
        cmd_file.write_text(content)

        loader = PromptLoader(tmp_path)
        prompt = loader.load_prompt_from_file(cmd_file)

        assert prompt.name == "test"
        assert prompt.metadata.description == "Test command"
        assert len(prompt.metadata.handoffs) == 1
        assert "$ARGUMENTS" in prompt.template

    def test_load_file_missing_description(self, tmp_path):
        """Test that file without description raises ValueError."""
        content = """---
author: Test Author
---

Test content
"""
        cmd_file = tmp_path / "test.md"
        cmd_file.write_text(content)

        loader = PromptLoader(tmp_path)
        with pytest.raises(ValueError, match="description"):
            loader.load_prompt_from_file(cmd_file)

    def test_load_file_too_large(self, tmp_path):
        """Test that file >100KB raises ValueError."""
        cmd_file = tmp_path / "test.md"
        cmd_file.write_text("x" * 100_001)  # Just over 100KB

        loader = PromptLoader(tmp_path)
        with pytest.raises(ValueError, match="too large"):
            loader.load_prompt_from_file(cmd_file)

    def test_load_malformed_yaml(self, tmp_path):
        """Test that malformed YAML is handled gracefully."""
        content = """---
description: Test
invalid yaml: [unclosed
---

Test content
"""
        cmd_file = tmp_path / "test.md"
        cmd_file.write_text(content)

        loader = PromptLoader(tmp_path)
        with pytest.raises(ValueError, match="Invalid YAML"):
            loader.load_prompt_from_file(cmd_file)

    def test_load_all_prompts(self, tmp_path):
        """Test loading all prompts from directory."""
        # Create valid files
        (tmp_path / "spec.md").write_text(
            """---
description: Create spec
---

Spec content with $ARGUMENTS
"""
        )
        (tmp_path / "plan.md").write_text(
            """---
description: Create plan
---

Plan content with $ARGUMENTS
"""
        )
        # Create malformed file (should be skipped)
        (tmp_path / "broken.md").write_text(
            """---
author: No description
---

Broken content
"""
        )

        loader = PromptLoader(tmp_path)
        prompts = loader.load_all_prompts()

        assert len(prompts) == 2
        assert "spec" in prompts
        assert "plan" in prompts
        assert "broken" not in prompts

    def test_get_prompt(self, tmp_path):
        """Test retrieving prompt from cache."""
        (tmp_path / "test.md").write_text(
            """---
description: Test
---

Content with $ARGUMENTS
"""
        )

        loader = PromptLoader(tmp_path)
        loader.load_all_prompts()

        prompt = loader.get_prompt("test")
        assert prompt is not None
        assert prompt.name == "test"

        # Test non-existent prompt
        assert loader.get_prompt("nonexistent") is None

    def test_list_prompts(self, tmp_path):
        """Test listing all prompts with descriptions."""
        (tmp_path / "test.md").write_text(
            """---
description: Test description
---

Content
"""
        )

        loader = PromptLoader(tmp_path)
        loader.load_all_prompts()

        prompts = loader.list_prompts()
        assert "test" in prompts
        assert prompts["test"] == "Test description"

    def test_nested_directory_structure(self, tmp_path):
        """Test scanning nested directories."""
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.md").write_text(
            """---
description: Nested prompt
---

Content with $ARGUMENTS
"""
        )

        loader = PromptLoader(tmp_path)
        prompts = loader.load_all_prompts()

        assert "subdir/nested" in prompts
        assert prompts["subdir/nested"].metadata.description == "Nested prompt"
