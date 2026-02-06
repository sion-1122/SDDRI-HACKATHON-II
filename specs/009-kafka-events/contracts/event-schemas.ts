# Kafka Event Streaming - Type Definitions

> **Language**: TypeScript 5+
> **Purpose**: Event schema contracts for type safety and validation
> **Status**: Production Ready | **Deployment**: Not Required

```typescript
/**
 * Base Event Contract
 * All events MUST extend this interface
 */
export interface BaseEvent {
  /** Unique identifier for this event instance (UUID v4) */
  event_id: string;

  /** Type of event - determines payload structure */
  event_type: EventType;

  /** Schema version for compatibility */
  event_version: 'v1';

  /** Event creation timestamp in ISO-8601 UTC */
  timestamp: string;

  /** Correlation ID for distributed tracing (UUID v4) */
  correlation_id: string;

  /** Service that produced this event */
  producer: EventProducer;

  /** Event-specific payload data */
  payload: unknown;
}

/**
 * All possible event types in the system
 */
export type EventType =
  | 'task-created'
  | 'task-updated'
  | 'task-deleted'
  | 'task-completed'
  | 'reminder-scheduled'
  | 'reminder-triggered'
  | 'reminder-cancelled'
  | 'recurrence-instance-created';

/**
 * Services that can produce events
 */
export type EventProducer =
  | 'chat-api'
  | 'reminder-worker'
  | 'recurrence-worker'
  | 'system';

// ============================================================================
// TASK EVENTS
// ============================================================================

/**
 * Event emitted when a new task is created
 */
export interface TaskCreatedEvent extends BaseEvent {
  event_type: 'task-created';
  payload: TaskCreatedPayload;
}

export interface TaskCreatedPayload {
  task_id: string;
  title: string;
  description: string | null;
  priority: TaskPriority;
  status: TaskStatus;
  due_date: string | null;           // ISO-8601
  recurrence: RecurrenceRule | null;
  tags: string[];
  user_id: string;
  created_at: string;
}

/**
 * Event emitted when a task is updated
 * Only contains changed fields for efficiency
 */
export interface TaskUpdatedEvent extends BaseEvent {
  event_type: 'task-updated';
  payload: TaskUpdatedPayload;
}

export interface TaskUpdatedPayload {
  task_id: string;
  changed_fields: string[];
  changes: Record<string, FieldChange>;
  updated_at: string;
}

export interface FieldChange {
  old: unknown;
  new: unknown;
}

/**
 * Event emitted when a task is deleted
 */
export interface TaskDeletedEvent extends BaseEvent {
  event_type: 'task-deleted';
  payload: TaskDeletedPayload;
}

export interface TaskDeletedPayload {
  task_id: string;
  user_id: string;
  deleted_at: string;
}

/**
 * Event emitted when a task is marked as complete
 */
export interface TaskCompletedEvent extends BaseEvent {
  event_type: 'task-completed';
  payload: TaskCompletedPayload;
}

export interface TaskCompletedPayload {
  task_id: string;
  user_id: string;
  completed_at: string;
  was_overdue: boolean;
}

// ============================================================================
// REMINDER EVENTS
// ============================================================================

/**
 * Event emitted when a reminder is scheduled
 */
export interface ReminderScheduledEvent extends BaseEvent {
  event_type: 'reminder-scheduled';
  payload: ReminderScheduledPayload;
}

export interface ReminderScheduledPayload {
  task_id: string;
  reminder_id: string;
  due_date: string;                  // ISO-8601
  reminder_time: string;             // ISO-8601
  recurrence: RecurrenceRule | null;
}

/**
 * Event emitted when a reminder should be triggered
 * Produced by reminder worker at scheduled time
 */
export interface ReminderTriggeredEvent extends BaseEvent {
  event_type: 'reminder-triggered';
  payload: ReminderTriggeredPayload;
}

export interface ReminderTriggeredPayload {
  task_id: string;
  reminder_id: string;
  task_title: string;
  user_id: string;
  due_date: string;
  is_overdue: boolean;
}

/**
 * Event emitted when a reminder is cancelled
 * (e.g., task deleted, due_date removed)
 */
export interface ReminderCancelledEvent extends BaseEvent {
  event_type: 'reminder-cancelled';
  payload: ReminderCancelledPayload;
}

export interface ReminderCancelledPayload {
  task_id: string;
  reminder_id: string;
  reason: 'task-deleted' | 'due-date-removed' | 'task-completed';
}

// ============================================================================
// RECURRENCE EVENTS
// ============================================================================

/**
 * Event emitted when a new instance of a recurring task is created
 */
export interface RecurrenceInstanceCreatedEvent extends BaseEvent {
  event_type: 'recurrence-instance-created';
  payload: RecurrenceInstanceCreatedPayload;
}

export interface RecurrenceInstanceCreatedPayload {
  parent_task_id: string;
  instance_task_id: string;
  scheduled_date: string;           // ISO-8601
  recurrence_rule: RecurrenceRule;
}

// ============================================================================
// SHARED TYPES
// ============================================================================

export type TaskPriority = 'HIGH' | 'MEDIUM' | 'LOW';
export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'DONE';

export interface RecurrenceRule {
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY';
  interval: number;                 // e.g., 1 = every, 2 = every other
  days_of_week?: number[];          // 0-6 (Sunday-Saturday), for WEEKLY
  end_date?: string;                // ISO-8601, optional
  end_after_occurrences?: number;   // Optional
  cron_expression?: string;         // For advanced scheduling
}

// ============================================================================
// EVENT UTILITIES
// ============================================================================

/**
 * Type guard to check if an event is of a specific type
 */
export function isEventType<T extends BaseEvent>(
  event: BaseEvent,
  eventType: T['event_type']
): event is T {
  return event.event_type === eventType;
}

/**
 * Validate event structure
 * Throws if event is malformed
 */
export function validateEvent(event: unknown): BaseEvent {
  // TODO: Implement Zod schema validation
  // This would use Zod schemas to validate the event structure
  return event as BaseEvent;
}

/**
 * Extract task_id from any event if present
 */
export function extractTaskId(event: BaseEvent): string | null {
  const payload = event.payload as Record<string, unknown>;
  return (payload.task_id as string) ?? null;
}

// ============================================================================
// ZOD SCHEAS (For Runtime Validation)
// ============================================================================

import { z } from 'zod';

export const EventProducerSchema = z.enum([
  'chat-api',
  'reminder-worker',
  'recurrence-worker',
  'system'
]);

export const EventTypeSchema = z.enum([
  'task-created',
  'task-updated',
  'task-deleted',
  'task-completed',
  'reminder-scheduled',
  'reminder-triggered',
  'reminder-cancelled',
  'recurrence-instance-created'
]);

export const BaseEventSchema = z.object({
  event_id: z.string().uuid(),
  event_type: EventTypeSchema,
  event_version: z.literal('v1'),
  timestamp: z.string().datetime(),
  correlation_id: z.string().uuid(),
  producer: EventProducerSchema,
  payload: z.unknown()
});

export const TaskPrioritySchema = z.enum(['HIGH', 'MEDIUM', 'LOW']);
export const TaskStatusSchema = z.enum(['TODO', 'IN_PROGRESS', 'DONE']);

export const RecurrenceRuleSchema = z.object({
  frequency: z.enum(['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']),
  interval: z.number().int().positive(),
  days_of_week: z.array(z.number().int().min(0).max(6)).optional(),
  end_date: z.string().datetime().optional(),
  end_after_occurrences: z.number().int().positive().optional(),
  cron_expression: z.string().optional()
});

export const TaskCreatedPayloadSchema = z.object({
  task_id: z.string().uuid(),
  title: z.string().min(1).max(500),
  description: z.string().nullable(),
  priority: TaskPrioritySchema,
  status: TaskStatusSchema,
  due_date: z.string().datetime().nullable(),
  recurrence: RecurrenceRuleSchema.nullable(),
  tags: z.array(z.string()),
  user_id: z.string().uuid(),
  created_at: z.string().datetime()
});

export const TaskCreatedEventSchema: z.ZodType<TaskCreatedEvent> = BaseEventSchema.extend({
  event_type: z.literal('task-created'),
  payload: TaskCreatedPayloadSchema
});

// ============================================================================
// KAFKA TOPIC CONFIGURATIONS
// ============================================================================

export const KAFKA_TOPICS = {
  TASK_EVENTS: 'task-events',
  REMINDERS: 'reminders',
  TASK_UPDATES: 'task-updates',
  DEAD_LETTER: 'dead-letter'
} as const;

export type KafkaTopic = typeof KAFKA_TOPICS[keyof typeof KAFKA_TOPICS];

/**
 * Maps event types to their target Kafka topics
 */
export const EVENT_TO_TOPIC: Record<EventType, KafkaTopic> = {
  'task-created': KAFKA_TOPICS.TASK_EVENTS,
  'task-updated': KAFKA_TOPICS.TASK_UPDATES,
  'task-deleted': KAFKA_TOPICS.TASK_EVENTS,
  'task-completed': KAFKA_TOPICS.TASK_UPDATES,
  'reminder-scheduled': KAFKA_TOPICS.REMINDERS,
  'reminder-triggered': KAFKA_TOPICS.REMINDERS,
  'reminder-cancelled': KAFKA_TOPICS.REMINDERS,
  'recurrence-instance-created': KAFKA_TOPICS.TASK_EVENTS
};
```

---

## Usage Example

```typescript
import { TaskCreatedEvent, TaskCreatedEventSchema, validateEvent } from './event-schemas';

// Create a new event
const event: TaskCreatedEvent = {
  event_id: crypto.randomUUID(),
  event_type: 'task-created',
  event_version: 'v1',
  timestamp: new Date().toISOString(),
  correlation_id: crypto.randomUUID(),
  producer: 'chat-api',
  payload: {
    task_id: crypto.randomUUID(),
    title: 'Complete Phase 5 documentation',
    description: 'Create comprehensive architecture docs',
    priority: 'HIGH',
    status: 'TODO',
    due_date: null,
    recurrence: null,
    tags: ['documentation', 'phase-5'],
    user_id: 'user-123',
    created_at: new Date().toISOString()
  }
};

// Validate using Zod
const validated = TaskCreatedEventSchema.parse(event);

// Get the target topic for this event
import { EVENT_TO_TOPIC } from './event-schemas';
const topic = EVENT_TO_TOPIC[event.event_type]; // 'task-events'
```
