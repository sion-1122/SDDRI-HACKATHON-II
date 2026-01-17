#!/usr/bin/env python3
"""Test script for AI chatbot prompts.

Sends test prompts to the chatbot API and generates a report on what worked.
Run from backend directory: PYTHONPATH=. uv run python scripts/test_chatbot_prompts.py

Usage:
    python scripts/test_chatbot_prompts.py [--base-url URL] [--user-id UUID]
"""
import argparse
import asyncio
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx


# Test prompts organized by tool/functionality
TEST_CASES = [
    # 1. add_task tests
    {
        "category": "add_task",
        "prompt": "Add a task to buy groceries",
        "expected_indicators": ["added", "created", "task", "groceries"],
        "expected_tool": "add_task"
    },
    {
        "category": "add_task",
        "prompt": "Create a high priority task called 'Finish project report' due tomorrow",
        "expected_indicators": ["added", "created", "task", "high priority"],
        "expected_tool": "add_task"
    },

    # 2. list_tasks tests
    {
        "category": "list_tasks",
        "prompt": "What are my tasks?",
        "expected_indicators": ["task"],
        "expected_tool": "list_tasks"
    },
    {
        "category": "list_tasks",
        "prompt": "Show me my pending tasks",
        "expected_indicators": ["task", "pending"],
        "expected_tool": "list_tasks"
    },

    # 3. update_task tests (requires existing task)
    {
        "category": "update_task",
        "prompt": "Change my first task to high priority",
        "expected_indicators": ["updated", "changed", "priority"],
        "expected_tool": "update_task",
        "note": "Requires at least one existing task"
    },

    # 4. complete_task tests
    {
        "category": "complete_task",
        "prompt": "Mark my first task as complete",
        "expected_indicators": ["complete", "done", "marked"],
        "expected_tool": "complete_task",
        "note": "Requires at least one existing task"
    },
    {
        "category": "complete_task",
        "prompt": "Mark all my tasks as complete",
        "expected_indicators": ["complete", "marked"],
        "expected_tool": "complete_all_tasks"
    },

    # 5. delete_task tests
    {
        "category": "delete_task",
        "prompt": "Delete my last task",
        "expected_indicators": ["deleted", "removed"],
        "expected_tool": "delete_task",
        "note": "Requires at least one existing task"
    },
    {
        "category": "delete_all_tasks",
        "prompt": "Delete all my tasks",
        "expected_indicators": ["delete", "confirm"],
        "expected_tool": "delete_all_tasks"
    },

    # 6. Edge cases
    {
        "category": "edge_case",
        "prompt": "What are my tasks?",
        "expected_indicators": [],
        "expected_tool": None,
        "note": "Empty list - should handle gracefully"
    },

    # 7. Ambiguous references
    {
        "category": "ambiguous_reference",
        "prompt": "Show me my tasks",
        "expected_indicators": ["task"],
        "expected_tool": "list_tasks",
        "note": "Priming for ambiguous reference"
    },
]


class ChatbotTester:
    """Test chatbot with various prompts."""

    def __init__(self, base_url: str, user_id: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.user_id = user_id
        self.timeout = timeout
        self.conversation_id: str | None = None
        self.results: list[dict[str, Any]] = []

    async def send_prompt(self, prompt: str) -> dict[str, Any]:
        """Send a prompt to the chatbot API."""
        url = f"{self.base_url}/api/{self.user_id}/chat"
        payload = {
            "message": prompt,
            "conversation_id": self.conversation_id
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

                # Update conversation_id for next request
                self.conversation_id = data.get("conversation_id")

                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": data.get("response", ""),
                    "conversation_id": data.get("conversation_id"),
                    "error": None
                }
            except httpx.HTTPStatusError as e:
                return {
                    "success": False,
                    "status_code": e.response.status_code,
                    "response": None,
                    "conversation_id": self.conversation_id,
                    "error": f"HTTP {e.response.status_code}: {e.response.text}"
                }
            except httpx.RequestError as e:
                return {
                    "success": False,
                    "status_code": None,
                    "response": None,
                    "conversation_id": self.conversation_id,
                    "error": f"Request error: {str(e)}"
                }
            except Exception as e:
                return {
                    "success": False,
                    "status_code": None,
                    "response": None,
                    "conversation_id": self.conversation_id,
                    "error": f"Unexpected error: {str(e)}"
                }

    def check_indicators(self, response_text: str, indicators: list[str]) -> bool:
        """Check if expected indicators are present in response."""
        if not indicators:
            return True
        response_lower = response_text.lower()
        return any(ind in response_lower for ind in indicators)

    async def run_test_case(self, test_case: dict[str, Any], index: int) -> dict[str, Any]:
        """Run a single test case."""
        prompt = test_case["prompt"]
        category = test_case["category"]
        expected_indicators = test_case.get("expected_indicators", [])
        expected_tool = test_case.get("expected_tool")

        print(f"\n[{index}] Testing: {category}")
        print(f"    Prompt: \"{prompt}\"")

        result = await self.send_prompt(prompt)

        # Determine if test passed
        passed = False
        failure_reason = ""

        if not result["success"]:
            failure_reason = f"Request failed: {result['error']}"
        elif result["response"] is None:
            failure_reason = "No response received"
        elif expected_indicators and not self.check_indicators(result["response"], expected_indicators):
            missing = [i for i in expected_indicators if i not in result["response"].lower()]
            failure_reason = f"Missing indicators: {missing}"
        else:
            passed = True

        return {
            "index": index,
            "category": category,
            "prompt": prompt,
            "expected_tool": expected_tool,
            "passed": passed,
            "failure_reason": failure_reason,
            "response": result.get("response") if result["success"] else None,
            "error": result.get("error"),
            "status_code": result.get("status_code"),
            "note": test_case.get("note", "")
        }

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all test cases."""
        print(f"\n{'='*60}")
        print(f"Chatbot Test Suite")
        print(f"Target: {self.base_url}")
        print(f"User ID: {self.user_id}")
        print(f"Started at: {datetime.now().isoformat()}")
        print(f"{'='*60}")

        start_time = datetime.now()

        for i, test_case in enumerate(TEST_CASES, 1):
            result = await self.run_test_case(test_case, i)
            self.results.append(result)

            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            print(f"    {status}")

            if result["response"]:
                response_preview = result["response"][:100]
                if len(result["response"]) > 100:
                    response_preview += "..."
                print(f"    Response: \"{response_preview}\"")
            elif result["error"]:
                print(f"    Error: {result['error']}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return self.generate_report(duration)

    def generate_report(self, duration: float) -> dict[str, Any]:
        """Generate test report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        # Group by category
        by_category: dict[str, dict[str, int]] = {}
        for result in self.results:
            cat = result["category"]
            if cat not in by_category:
                by_category[cat] = {"passed": 0, "failed": 0, "total": 0}
            by_category[cat]["total"] += 1
            if result["passed"]:
                by_category[cat]["passed"] += 1
            else:
                by_category[cat]["failed"] += 1

        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{pass_rate:.1f}%",
                "duration_seconds": duration
            },
            "by_category": by_category,
            "results": self.results
        }

    def print_report(self, report: dict[str, Any]) -> None:
        """Print formatted report."""
        print(f"\n{'='*60}")
        print(f"TEST REPORT")
        print(f"{'='*60}")

        summary = report["summary"]
        print(f"\nSummary:")
        print(f"  Total Tests:  {summary['total']}")
        print(f"  Passed:       {summary['passed']} ✓")
        print(f"  Failed:       {summary['failed']} ✗")
        print(f"  Pass Rate:    {summary['pass_rate']}")
        print(f"  Duration:     {summary['duration_seconds']:.2f}s")

        print(f"\nResults by Category:")
        for cat, stats in report["by_category"].items():
            print(f"  {cat}:")
            print(f"    Passed: {stats['passed']}/{stats['total']}")

        if summary["failed"] > 0:
            print(f"\n{'='*60}")
            print(f"Failed Tests:")
            print(f"{'='*60}")
            for result in report["results"]:
                if not result["passed"]:
                    print(f"\n[{result['index']}] {result['category']}")
                    print(f"  Prompt: \"{result['prompt']}\"")
                    print(f"  Reason: {result['failure_reason']}")
                    if result["note"]:
                        print(f"  Note: {result['note']}")

        print(f"\n{'='*60}")

    def save_report(self, report: dict[str, Any], output_path: str) -> None:
        """Save report to JSON file."""
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {output_path}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test chatbot with sample prompts")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the chatbot API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--user-id",
        default=str(uuid.uuid4()),
        help="User ID for testing (default: random UUID)"
    )
    parser.add_argument(
        "--output",
        default="test_chatbot_report.json",
        help="Output file for JSON report (default: test_chatbot_report.json)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30.0)"
    )

    args = parser.parse_args()

    tester = ChatbotTester(
        base_url=args.base_url,
        user_id=args.user_id,
        timeout=args.timeout
    )

    report = await tester.run_all_tests()
    tester.print_report(report)
    tester.save_report(report, args.output)

    # Exit with error code if any tests failed
    sys.exit(0 if report["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
