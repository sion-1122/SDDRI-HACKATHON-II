/** Individual tool status display component.
 *
 * [Task]: T075
 * [From]: specs/004-ai-chatbot/tasks.md
 *
 * This component displays the status of a single tool execution event.
 * It's designed to be used alongside or within the progress bar to show
 * detailed status of the current or most recent tool operation.
 *
 * @example
 * ```tsx
 * <ToolStatus
 *   event={{
 *     event_type: "tool_complete",
 *     tool: "list_tasks",
 *     message: "Found 3 tasks",
 *     count: 3
 *   }}
 * />
 * ```
 */
"use client";

import type { ToolProgressEvent } from "./useWebSocket";

/** Props for the ToolStatus component. */
export interface ToolStatusProps {
  /** The progress event to display. */
  event: ToolProgressEvent;
  /** Whether to show compact version (default: false). */
  compact?: boolean;
}

/**
 * Individual tool status display component.
 *
 * [From]: specs/004-ai-chatbot/research.md - Section 5
 */
export function ToolStatus({ event, compact = false }: ToolStatusProps) {
  const getStatusDisplay = (): {
    icon: string;
    bgColor: string;
    borderColor: string;
    textColor: string;
    animateClass?: string;
  } => {
    switch (event.event_type) {
      case "connection_established":
        return {
          icon: "🔗",
          bgColor: "bg-green-50 dark:bg-green-900/20",
          borderColor: "border-green-200 dark:border-green-800",
          textColor: "text-green-700 dark:text-green-300",
        };
      case "agent_thinking":
        return {
          icon: "💭",
          bgColor: "bg-purple-50 dark:bg-purple-900/20",
          borderColor: "border-purple-200 dark:border-purple-800",
          textColor: "text-purple-700 dark:text-purple-300",
          animateClass: "animate-pulse",
        };
      case "tool_starting":
        return {
          icon: "🚀",
          bgColor: "bg-yellow-50 dark:bg-yellow-900/20",
          borderColor: "border-yellow-200 dark:border-yellow-800",
          textColor: "text-yellow-700 dark:text-yellow-300",
          animateClass: "animate-pulse",
        };
      case "tool_progress":
        return {
          icon: "⏳",
          bgColor: "bg-blue-50 dark:bg-blue-900/20",
          borderColor: "border-blue-200 dark:border-blue-800",
          textColor: "text-blue-700 dark:text-blue-300",
          animateClass: "animate-spin",
        };
      case "tool_complete":
        return {
          icon: "✅",
          bgColor: "bg-green-50 dark:bg-green-900/20",
          borderColor: "border-green-200 dark:border-green-800",
          textColor: "text-green-700 dark:text-green-300",
        };
      case "tool_error":
        return {
          icon: "❌",
          bgColor: "bg-red-50 dark:bg-red-900/20",
          borderColor: "border-red-200 dark:border-red-800",
          textColor: "text-red-700 dark:text-red-300",
        };
      case "agent_done":
        return {
          icon: "✨",
          bgColor: "bg-indigo-50 dark:bg-indigo-900/20",
          borderColor: "border-indigo-200 dark:border-indigo-800",
          textColor: "text-indigo-700 dark:text-indigo-300",
        };
      default:
        return {
          icon: "•",
          bgColor: "bg-gray-50 dark:bg-gray-900/20",
          borderColor: "border-gray-200 dark:border-gray-800",
          textColor: "text-gray-700 dark:text-gray-300",
        };
    }
  };

  const { icon, bgColor, borderColor, textColor, animateClass } = getStatusDisplay();

  if (compact) {
    return (
      <div
        className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${bgColor} ${borderColor} ${textColor} border ${animateClass || ""}`}
      >
        <span>{icon}</span>
        <span className="truncate max-w-[150px]">{event.message}</span>
        {event.count !== undefined && event.count > 0 && (
          <span className="px-1.5 py-0.5 bg-white/50 rounded-full text-[10px] font-semibold">
            {event.count}
          </span>
        )}
      </div>
    );
  }

  return (
    <div
      className={`flex items-center gap-3 px-3 py-2 rounded-lg border ${bgColor} ${borderColor} ${textColor} ${animateClass || ""} animate-fadeIn`}
    >
      <span className="text-lg flex-shrink-0">{icon}</span>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{event.message}</p>

        {event.tool && (
          <p className="text-xs opacity-70 mt-0.5">
            Tool: <code className="px-1 py-0.5 bg-white/30 rounded">{event.tool}</code>
          </p>
        )}

        {event.error && (
          <p className="text-xs mt-1 text-red-600 dark:text-red-400">
            Error: {event.error}
          </p>
        )}
      </div>

      {event.count !== undefined && event.count > 0 && (
        <div className="flex-shrink-0">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-white/50 text-sm font-bold">
            {event.count}
          </span>
        </div>
      )}
    </div>
  );
}

/** Loading skeleton for tool status. */
export function ToolStatusSkeleton() {
  return (
    <div className="flex items-center gap-3 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/20 animate-pulse">
      <div className="w-5 h-5 rounded-full bg-gray-300 dark:bg-gray-700" />
      <div className="flex-1">
        <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-3/4 mb-1" />
        <div className="h-3 bg-gray-300 dark:bg-gray-700 rounded w-1/2" />
      </div>
    </div>
  );
}
