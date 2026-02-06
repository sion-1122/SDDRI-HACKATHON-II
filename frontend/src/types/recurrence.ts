/* Recurrence rule type definitions.

[Task]: T010
[From]: specs/008-advanced-features/tasks.md (Phase 1)

Defines how tasks repeat (daily, weekly, monthly) with support
for custom intervals, count limits, and end dates.
*/

export type RecurrenceFrequency = 'daily' | 'weekly' | 'monthly';

export interface RecurrenceRule {
  frequency: RecurrenceFrequency;
  interval?: number;        // 1-365, default: 1 (e.g., 2 = every 2 days)
  count?: number;           // 1-100, max occurrences
  end_date?: string;        // ISO 8601 date
}
