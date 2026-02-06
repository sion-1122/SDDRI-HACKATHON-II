"""Recurrence rule model for recurring tasks.

[Task]: T002
[From]: specs/008-advanced-features/tasks.md (Phase 1)

This module defines the RecurrenceRule Pydantic model used for
defining how tasks repeat (daily, weekly, monthly).
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class RecurrenceRule(BaseModel):
    """Defines how a task repeats.

    Used for creating recurring tasks that automatically generate
    new instances when completed.

    Attributes:
        frequency: How often the task repeats (daily, weekly, monthly)
        interval: Repeat every N periods (default: 1)
        count: Maximum number of occurrences (max 100)
        end_date: Stop recurring after this date

    Examples:
        Daily forever: {"frequency": "daily"}
        Weekly: {"frequency": "weekly"}
        Every 2 weeks: {"frequency": "weekly", "interval": 2}
        Monthly, 10 times: {"frequency": "monthly", "count": 10}
        Daily until Dec 31: {"frequency": "daily", "end_date": "2026-12-31"}
    """

    frequency: Literal['daily', 'weekly', 'monthly'] = Field(
        ...,
        description="How often the task repeats"
    )

    interval: Optional[int] = Field(
        default=1,
        ge=1,
        le=365,
        description="Repeat every N periods (max 365, e.g., 2 = every 2 days)"
    )

    count: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Maximum number of occurrences (max 100)"
    )

    end_date: Optional[datetime] = Field(
        default=None,
        description="Stop recurring after this date"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"frequency": "daily"},
                {"frequency": "weekly"},
                {"frequency": "weekly", "interval": 2},
                {"frequency": "monthly", "count": 10},
                {"frequency": "daily", "interval": 1, "count": 30},
            ]
        }
    }
