/** Animated progress bar for AI agent tool execution.
 *
 * [Task]: T074
 * [From]: specs/004-ai-chatbot/tasks.md
 *
 * This component displays real-time progress events during AI tool execution
 * with beautiful animated indicators and smooth transitions.
 *
 * @example
 * ```tsx
 * <ProgressBar
 *   events={[
 *     { event_type: "tool_starting", message: "Searching tasks..." },
 *     { event_type: "tool_complete", message: "Found 3 tasks", count: 3 }
 *   ]}
 * />
 * ```
 */
"use client";

import { useEffect, useState } from "react";
import type { ToolProgressEvent } from "./useWebSocket";

/** Props for the ProgressBar component. */
export interface ProgressBarProps {
  /** Array of progress events to display. */
  events: ToolProgressEvent[];
  /** Time in milliseconds before clearing events after completion (default: 5000). */
  clearAfter?: number;
  /** Maximum number of events to display (default: 5). */
  maxEvents?: number;
}

/**
 * Animated progress bar component for AI agent tool execution.
 *
 * [From]: specs/004-ai-chatbot/research.md - Section 5
 */
export function ProgressBar({
  events,
  clearAfter = 5000,
  maxEvents = 5,
}: ProgressBarProps) {
  const [visibleEvents, setVisibleEvents] = useState<ToolProgressEvent[]>([]);

  useEffect(() => {
    // Update visible events when events change
    setVisibleEvents(events);

    // Auto-clear after agent_done or when no events
    if (events.length > 0) {
      const lastEvent = events[events.length - 1];
      if (lastEvent.event_type === "agent_done") {
        const timeout = setTimeout(() => {
          setVisibleEvents([]);
        }, clearAfter);
        return () => clearTimeout(timeout);
      }
    }
  }, [events, clearAfter]);

  // Don't render if no events
  if (visibleEvents.length === 0) {
    return null;
  }

  // Show only the most recent events
  const displayEvents = visibleEvents.slice(-maxEvents);

  return (
    <div className="mx-4 my-2 overflow-hidden">
      <div className="flex flex-col gap-1 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-lg border border-blue-200 dark:border-blue-800 shadow-sm animate-fadeIn">
        {displayEvents.map((event, index) => (
          <ProgressItem
            key={`${event.event_type}-${index}`}
            event={event}
            index={index}
          />
        ))}
      </div>
    </div>
  );
}

/** Individual progress item component. */
function ProgressItem({
  event,
  index,
}: {
  event: ToolProgressEvent;
  index: number;
}) {
  const getIcon = (): {
    icon: string;
    className: string;
    animateClass?: string;
  } => {
    switch (event.event_type) {
      case "tool_complete":
      case "agent_done":
        return {
          icon: "✓",
          className: "text-green-600 dark:text-green-400 text-lg",
        };
      case "tool_error":
        return {
          icon: "✗",
          className: "text-red-600 dark:text-red-400 text-lg",
        };
      case "tool_progress":
        return {
          icon: "⏳",
          className: "text-blue-600 dark:text-blue-400",
          animateClass: "animate-spin",
        };
      case "tool_starting":
        return {
          icon: "▶",
          className: "text-yellow-600 dark:text-yellow-400",
          animateClass: "animate-pulse",
        };
      case "agent_thinking":
        return {
          icon: "…",
          className: "text-gray-500 dark:text-gray-400",
          animateClass: "animate-pulse",
        };
      default:
        return {
          icon: "•",
          className: "text-gray-500 dark:text-gray-400",
        };
    }
  };

  const { icon, className, animateClass } = getIcon();

  return (
    <div
      className="flex items-center gap-2 text-sm animate-fadeIn"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <span className={`flex-shrink-0 ${className} ${animateClass || ""}`}>
        {icon}
      </span>
      <span className="text-gray-700 dark:text-gray-300 font-medium flex-1">
        {event.message}
      </span>
      {event.count !== undefined && event.count > 0 && (
        <span className="ml-auto px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full text-xs font-semibold">
          {event.count}
        </span>
      )}
    </div>
  );
}
