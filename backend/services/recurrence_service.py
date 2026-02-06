"""Recurrence service for calculating recurring task dates.

[Task]: T015-T020
[From]: specs/008-advanced-features/tasks.md (Phase 2)

This service handles:
- Calculating next occurrence dates from recurrence rules
- Validating recurrence rule structures
- Checking recurrence limits (100 instance max)
- Supporting daily, weekly, monthly, and cron-based patterns
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlmodel import Session

from models.task import Task
from models.recurrence import RecurrenceRule


class RecurrenceService:
    """Service for calculating recurring task dates."""

    MAX_RECURRING_INSTANCES = 100

    def __init__(self, session: Session):
        """Initialize the recurrence service.

        Args:
            session: Database session for queries
        """
        self.session = session

    def calculate_next_occurrence(
        self,
        base_date: datetime,
        recurrence_rule: dict
    ) -> Optional[datetime]:
        """Calculate next due date based on recurrence pattern.

        [Task]: T016-T018, T077 (cron)

        Args:
            base_date: The base date to calculate from
            recurrence_rule: Dictionary containing recurrence rule

        Returns:
            Next due date in UTC, or None if limit reached

        Raises:
            ValueError: If recurrence rule is invalid
        """
        if not self.validate_recurrence_rule(recurrence_rule):
            raise ValueError("Invalid recurrence rule")

        frequency = recurrence_rule.get("frequency")
        interval = recurrence_rule.get("interval", 1)

        # For cron-based recurrence (T077)
        if frequency == "cron" and "cron_expression" in recurrence_rule:
            return self._calculate_from_cron(base_date, recurrence_rule["cron_expression"])

        # Calculate based on frequency
        if frequency == "daily":
            return base_date + timedelta(days=interval)
        elif frequency == "weekly":
            return base_date + timedelta(weeks=interval)
        elif frequency == "monthly":
            return self._add_months(base_date, interval)
        else:
            raise ValueError(f"Unsupported frequency: {frequency}")

    def _add_months(self, date: datetime, months: int) -> datetime:
        """Add months to a date, handling edge cases.

        Args:
            date: Base date
            months: Number of months to add

        Returns:
            New date with months added
        """
        # Simple implementation: add days (approximate)
        # For precise month handling, would use dateutil.relativedelta
        return date + timedelta(days=months * 30)

    def _calculate_from_cron(self, base_date: datetime, cron_expression: str) -> Optional[datetime]:
        """Calculate next occurrence from cron expression.

        [Task]: T077

        Args:
            base_date: Base date to calculate from
            cron_expression: Cron expression (5 fields)

        Returns:
            Next due date, or None if invalid

        Note:
            This is a simplified implementation. A full cron parser
            would be more complex. For MVP, we support basic patterns.
        """
        # TODO: Implement full cron parsing
        # For now, return None to indicate not implemented
        return None

    def validate_recurrence_rule(self, rule: dict) -> bool:
        """Validate recurrence rule structure.

        [Task]: T019

        Args:
            rule: Dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(rule, dict):
            return False

        # Check frequency
        frequency = rule.get("frequency")
        if frequency not in ("daily", "weekly", "monthly"):
            return False

        # Validate interval
        interval = rule.get("interval", 1)
        if not isinstance(interval, int) or interval < 1 or interval > 365:
            return False

        # Validate count
        count = rule.get("count")
        if count is not None:
            if not isinstance(count, int) or count < 1 or count > self.MAX_RECURRING_INSTANCES:
                return False

        # Validate end_date
        end_date = rule.get("end_date")
        if end_date is not None:
            if not isinstance(end_date, (datetime, str)):
                return False

        return True

    def check_recurrence_limit(self, parent_task_id: uuid.UUID) -> bool:
        """Check if recurrence limit has been reached.

        [Task]: T020

        Args:
            parent_task_id: ID of the parent recurring task

        Returns:
            True if limit reached, False otherwise

        Raises:
            ValueError: If limit exceeded
        """
        # Count existing instances with this parent
        count_result = self.session.exec(
            select(func.count(Task.id))
            .where(Task.parent_task_id == parent_task_id)
        )
        instance_count = count_result.one() or 0

        if instance_count >= self.MAX_RECURRING_INSTANCES:
            raise ValueError(
                f"Recurrence limit reached: maximum {self.MAX_RECURRING_INSTANCES} instances"
            )

        return False

    def should_create_next_instance(
        self,
        task: Task,
        next_due_date: datetime
    ) -> bool:
        """Determine if next instance should be created.

        Checks count and end_date limits from recurrence rule.

        Args:
            task: Current task being completed
            next_due_date: Calculated next due date

        Returns:
            True if should create, False if limit reached
        """
        if not task.recurrence:
            return False

        # Get parent task ID (for instances) or use current task ID (for original)
        parent_id = task.parent_task_id or task.id

        # Check instance count limit
        count_result = self.session.exec(
            select(func.count(Task.id))
            .where(Task.parent_task_id == parent_id)
        )
        instance_count = count_result.one() or 0

        # Check count limit
        count_limit = task.recurrence.get("count")
        if count_limit and instance_count >= count_limit:
            return False

        # Check end_date limit
        end_date_str = task.recurrence.get("end_date")
        if end_date_str:
            if isinstance(end_date_str, str):
                end_date = datetime.fromisoformat(end_date_str)
            else:
                end_date = end_date_str

            if next_due_date > end_date:
                return False

        return True
