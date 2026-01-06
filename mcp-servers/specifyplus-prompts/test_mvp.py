#!/usr/bin/env python3
"""Simple test script to verify MCP server MVP functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from specifyplus_prompts.prompt_loader import PromptLoader

def test_prompt_loader():
    """Test that PromptLoader can load all prompts."""
    commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"
    print(f"Testing with commands directory: {commands_dir}")

    if not commands_dir.exists():
        print(f"ERROR: Commands directory does not exist: {commands_dir}")
        return False

    loader = PromptLoader(commands_dir)
    prompts = loader.load_all_prompts()

    print(f"\n✅ Loaded {len(prompts)} prompts:")

    for name, prompt in sorted(prompts.items()):
        print(f"  - {name}: {prompt.metadata.description}")
        # Test argument substitution
        formatted = prompt.format("test arguments")
        if "$ARGUMENTS" in formatted:
            print(f"    ⚠️  WARNING: $ARGUMENTS not substituted in {name}")
        else:
            print(f"    ✅ Argument substitution works")

    # Test get_prompt
    first_name = list(prompts.keys())[0]
    retrieved = loader.get_prompt(first_name)
    if retrieved and retrieved.name == first_name:
        print(f"\n✅ get_prompt('{first_name}') works")
    else:
        print(f"\n❌ get_prompt('{first_name}') failed")
        return False

    # Test list_prompts
    prompt_list = loader.list_prompts()
    if len(prompt_list) == len(prompts):
        print(f"✅ list_prompts() returns {len(prompt_list)} items")
    else:
        print(f"❌ list_prompts() count mismatch")
        return False

    return True

if __name__ == "__main__":
    success = test_prompt_loader()
    sys.exit(0 if success else 1)
