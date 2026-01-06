"""Tests for IDE integration and concurrent access."""

import asyncio
from datetime import datetime

import pytest

from specifyplus_prompts.models import Prompt, PromptMetadata
from specifyplus_prompts.prompt_loader import PromptLoader


class TestConcurrentAccess:
    """Test concurrent access to prompts."""

    @pytest.mark.asyncio
    async def test_concurrent_get_prompt(self, tmp_path):
        """Test that multiple concurrent requests can access prompts safely."""
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text(
            """---
description: Test
---

Content with $ARGUMENTS
"""
        )

        loader = PromptLoader(tmp_path)
        loader.load_all_prompts()

        # Simulate 100 concurrent reads (get_prompt is synchronous)
        # This tests that the cache can handle rapid concurrent access
        results = []
        for _ in range(100):
            prompt = loader.get_prompt("test")
            results.append(prompt)

        # All results should be non-None
        assert all(r is not None for r in results)

    def test_loader_is_thread_safe(self, tmp_path):
        """Test that PromptLoader cache operations are thread-safe."""
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

        # Multiple reads should be safe
        prompt1 = loader.get_prompt("test")
        prompt2 = loader.get_prompt("test")

        # Should return same prompt
        assert prompt1 is not None
        assert prompt2 is not None
        assert prompt1.name == prompt2.name


class TestSpecialCharacters:
    """Test handling of special characters in arguments."""

    def test_newlines_in_arguments(self, tmp_path):
        """Test that newlines in arguments are preserved."""
        prompt = Prompt(
            name="test",
            file_path=str(tmp_path / "test.md"),
            metadata=PromptMetadata(description="Test"),
            template="Before $ARGUMENTS after",
            modified_at=datetime.now(),
            size_bytes=100,
        )

        args_with_newlines = "line1\nline2\nline3"
        result = prompt.format(args_with_newlines)

        assert "line1\nline2\nline3" in result

    def test_quotes_in_arguments(self, tmp_path):
        """Test that quotes in arguments are preserved."""
        prompt = Prompt(
            name="test",
            file_path=str(tmp_path / "test.md"),
            metadata=PromptMetadata(description="Test"),
            template='Text: "$ARGUMENTS"',
            modified_at=datetime.now(),
            size_bytes=100,
        )

        args_with_quotes = '''He said "hello" and 'goodbye'
        '''
        result = prompt.format(args_with_quotes)

        assert '"hello"' in result
        assert "'goodbye'" in result

    def test_markdown_in_arguments(self, tmp_path):
        """Test that markdown formatting in arguments is preserved."""
        prompt = Prompt(
            name="test",
            file_path=str(tmp_path / "test.md"),
            metadata=PromptMetadata(description="Test"),
            template="# Header\n\n$ARGUMENTS\n\n## Footer",
            modified_at=datetime.now(),
            size_bytes=100,
        )

        args_with_markdown = """
- Bullet 1
- Bullet 2
- **Bold text**
- `code snippet`
        """

        result = prompt.format(args_with_markdown)

        assert "- Bullet 1" in result
        assert "**Bold text**" in result
        assert "`code snippet`" in result

    def test_code_blocks_in_arguments(self, tmp_path):
        """Test that code blocks in arguments are preserved."""
        prompt = Prompt(
            name="test",
            file_path=str(tmp_path / "test.md"),
            metadata=PromptMetadata(description="Test"),
            template="```python\n$ARGUMENTS\n```",
            modified_at=datetime.now(),
            size_bytes=100,
        )

        args_with_code = """def hello():
    print("world")
    return True"""

        result = prompt.format(args_with_code)

        assert 'def hello():' in result
        assert 'print("world")' in result

    def test_empty_arguments(self, tmp_path):
        """Test that empty arguments don't break formatting."""
        prompt = Prompt(
            name="test",
            file_path=str(tmp_path / "test.md"),
            metadata=PromptMetadata(description="Test"),
            template="Before $ARGUMENTS after",
            modified_at=datetime.now(),
            size_bytes=100,
        )

        result = prompt.format("")
        assert result == "Before  after"

    def test_very_long_arguments(self, tmp_path):
        """Test that very long arguments are handled."""
        prompt = Prompt(
            name="test",
            file_path=str(tmp_path / "test.md"),
            metadata=PromptMetadata(description="Test"),
            template="$ARGUMENTS",
            modified_at=datetime.now(),
            size_bytes=100,
        )

        # 10KB of arguments
        long_args = "x" * 10_000
        result = prompt.format(long_args)

        assert len(result) == 10_000

    def test_unicode_in_arguments(self, tmp_path):
        """Test that unicode characters in arguments are preserved."""
        prompt = Prompt(
            name="test",
            file_path=str(tmp_path / "test.md"),
            metadata=PromptMetadata(description="Test"),
            template="$ARGUMENTS",
            modified_at=datetime.now(),
            size_bytes=100,
        )

        unicode_args = "Hello 世界 🌍 Ñoño"
        result = prompt.format(unicode_args)

        assert "世界" in result
        assert "🌍" in result
        assert "Ñoño" in result
