#!/usr/bin/env python3
"""Integration validation script for AI chatbot.

This script validates that all components of the AI chatbot are properly
configured and integrated.

[From]: Phase III Integration Testing

Usage:
    python scripts/validate_chat_integration.py
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def check_environment():
    """Check if required environment variables are set."""
    print("\n🔍 Checking environment variables...")

    from core.config import get_settings

    try:
        settings = get_settings()

        # Check database URL
        if not settings.database_url:
            print("❌ DATABASE_URL not set")
            return False
        print(f"✅ DATABASE_URL: {settings.database_url[:20]}...")

        # Check Gemini API key (optional for testing, required for production)
        if not settings.gemini_api_key:
            print("⚠️  GEMINI_API_KEY not set (required for AI chatbot)")
            print("   Get your API key from: https://aistudio.google.com")
        else:
            print(f"✅ GEMINI_API_KEY: {settings.gemini_api_key[:10]}...")

        # Check frontend URL
        if not settings.frontend_url:
            print("⚠️  FRONTEND_URL not set")
        else:
            print(f"✅ FRONTEND_URL: {settings.frontend_url}")

        return True

    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False


def check_database():
    """Check database connection and schema."""
    print("\n🔍 Checking database...")

    from sqlmodel import select, Session
    from core.database import engine
    from models.task import Task
    from models.conversation import Conversation
    from models.message import Message

    try:
        with Session(engine) as session:
            # Check if conversation table exists
            try:
                session.exec(select(Conversation).limit(1))
                print("✅ Conversation table exists")
            except Exception as e:
                print(f"❌ Conversation table error: {e}")
                return False

            # Check if message table exists
            try:
                session.exec(select(Message).limit(1))
                print("✅ Message table exists")
            except Exception as e:
                print(f"❌ Message table error: {e}")
                return False

            # Check if task table exists
            try:
                session.exec(select(Task).limit(1))
                print("✅ Task table exists")
            except Exception as e:
                print(f"❌ Task table error: {e}")
                return False

        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def check_mcp_tools():
    """Check if MCP tools are registered."""
    print("\n🔍 Checking MCP tools...")

    try:
        from mcp_server.tools import add_task, list_tasks

        # Check add_task tool
        if hasattr(add_task, 'tool_metadata'):
            print(f"✅ add_task tool: {add_task.tool_metadata['name']}")
        else:
            print("❌ add_task tool metadata not found")
            return False

        # Check list_tasks tool
        if hasattr(list_tasks, 'tool_metadata'):
            print(f"✅ list_tasks tool: {list_tasks.tool_metadata['name']}")
        else:
            print("❌ list_tasks tool metadata not found")
            return False

        return True

    except Exception as e:
        print(f"❌ MCP tools check failed: {e}")
        return False


def check_ai_agent():
    """Check if AI agent is configured."""
    print("\n🔍 Checking AI agent...")

    try:
        from ai_agent import is_gemini_configured, get_task_agent

        # Check if Gemini is configured
        if is_gemini_configured():
            print("✅ Gemini API is configured")
        else:
            print("⚠️  Gemini API not configured (required for AI functionality)")

        # Try to get the agent (won't connect to API, just initializes)
        try:
            agent = get_task_agent()
            print(f"✅ AI agent initialized: {agent.name}")
        except ValueError as e:
            print(f"⚠️  AI agent not initialized: {e}")

        return True

    except Exception as e:
        print(f"❌ AI agent check failed: {e}")
        return False


def check_api_routes():
    """Check if chat API routes are registered."""
    print("\n🔍 Checking API routes...")

    try:
        from main import app

        # Get all routes
        routes = [route.path for route in app.routes]

        # Check for chat endpoint
        chat_routes = [r for r in routes if '/chat' in r]
        if chat_routes:
            print(f"✅ Chat routes found: {len(chat_routes)}")
            for route in chat_routes:
                print(f"   - {route}")
        else:
            print("❌ No chat routes found")
            return False

        return True

    except Exception as e:
        print(f"❌ API routes check failed: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n🔍 Checking dependencies...")

    required_packages = [
        ('fastapi', 'FastAPI'),
        ('agents', 'OpenAI Agents SDK'),
        ('openai', 'OpenAI SDK'),
        ('sqlmodel', 'SQLModel'),
        ('pydantic_settings', 'Pydantic Settings'),
    ]

    all_ok = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} not installed")
            all_ok = False

    return all_ok


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("AI Chatbot Integration Validation")
    print("=" * 60)

    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Database", check_database),
        ("MCP Tools", check_mcp_tools),
        ("AI Agent", check_ai_agent),
        ("API Routes", check_api_routes),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with exception: {e}")
            results.append((name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
        if not result:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All checks passed! The AI chatbot is ready for integration.")
        print("\nNext steps:")
        print("1. Start the backend server: uv run python main.py")
        print("2. Test the chat endpoint: http://localhost:8000/docs")
        print("3. Access the frontend chat page: http://localhost:3000/chat")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Set GEMINI_API_KEY in .env file")
        print("2. Run database migrations: python backend/migrations/run_migration.py")
        print("3. Install dependencies: uv sync")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
