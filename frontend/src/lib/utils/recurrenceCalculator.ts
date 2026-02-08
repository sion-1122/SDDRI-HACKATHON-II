/* Recurrence calculation utilities for frontend.

[Task]: T024-T026
[From]: specs/008-advanced-features/tasks.md (Phase 2)

Provides recurrence calculation functions that mirror the backend
RecurrenceService logic for client-side validation and UI updates.
*/
import { addDays, addWeeks, addMonths } from 'date-fns';
import type { RecurrenceRule } from '@/types/recurrence';

/**
 * Calculate next occurrence date from recurrence rule.
 *
 * [Task]: T025
 *
 * @param baseDate - Base date to calculate from
 * @param rule - Recurrence rule
 * @returns Next due date, or null if invalid
 */
export function calculateNext(
  baseDate: Date,
  rule: RecurrenceRule
): Date | null {
  if (!isValidRecurrenceRule(rule)) {
    return null;
  }

  const interval = rule.interval || 1;

  switch (rule.frequency) {
    case 'daily':
      return addDays(baseDate, interval);
    case 'weekly':
      return addWeeks(baseDate, interval);
    case 'monthly':
      // Approximate: add days (30 * interval)
      // For precision, would use date-fns addMonths
      return addMonths(baseDate, interval);
    default:
      return null;
  }
}

/**
 * Validate recurrence rule structure.
 *
 * [Task]: T026
 *
 * @param rule - Object to validate
 * @returns True if valid, False otherwise
 */
export function isValidRecurrenceRule(rule: any): rule is RecurrenceRule {
  if (!rule || typeof rule !== 'object') {
    return false;
  }

  // Check frequency
  if (
    typeof rule.frequency !== 'string' ||
    !['daily', 'weekly', 'monthly'].includes(rule.frequency)
  ) {
    return false;
  }

  // Validate interval (optional, default 1)
  if (rule.interval !== undefined) {
    if (
      typeof rule.interval !== 'number' ||
      rule.interval < 1 ||
      rule.interval > 365
    ) {
      return false;
    }
  }

  // Validate count (optional)
  if (rule.count !== undefined) {
    if (
      typeof rule.count !== 'number' ||
      rule.count < 1 ||
      rule.count > 100
    ) {
      return false;
    }
  }

  // Validate end_date (optional)
  if (rule.end_date !== undefined) {
    const endDate = new Date(rule.end_date);
    if (isNaN(endDate.getTime())) {
      return false;
    }
  }

  return true;
}

/**
 * Get recurrence display text.
 *
 * @param rule - Recurrence rule
 * @returns Human-readable recurrence text
 */
export function getRecurrenceText(rule: RecurrenceRule): string {
  const interval = rule.interval || 1;
  const frequency = rule.frequency;

  if (interval === 1) {
    switch (frequency) {
      case 'daily':
        return 'Daily';
      case 'weekly':
        return 'Weekly';
      case 'monthly':
        return 'Monthly';
    }
  }

  switch (frequency) {
    case 'daily':
      return `Every ${interval} days`;
    case 'weekly':
      return `Every ${interval} weeks`;
    case 'monthly':
      return `Every ${interval} months`;
    default:
      return 'Custom';
  }
}

/**
 * Check if recurrence has an end condition.
 *
 * @param rule - Recurrence rule
 * @returns True if has count or end_date limit
 */
export function hasEndCondition(rule: RecurrenceRule): boolean {
  return (
    rule.count !== undefined ||
    rule.end_date !== undefined
  );
}

/**
 * Get recurrence end condition text.
 *
 * @param rule - Recurrence rule
 * @returns Human-readable end condition
 */
export function getEndConditionText(rule: RecurrenceRule): string {
  if (rule.count) {
    return `${rule.count} time${rule.count > 1 ? 's' : ''}`;
  }

  if (rule.end_date) {
    const endDate = new Date(rule.end_date);
    return endDate.toLocaleDateString();
  }

  return 'Forever';
}
