/** Connection status indicator for WebSocket.
 *
 * [Task]: T076
 * [From]: specs/004-ai-chatbot/tasks.md
 *
 * This component displays the current WebSocket connection status
 * with visual indicators (dot, text, and signal strength bars).
 *
 * @example
 * ```tsx
 * <ConnectionStatus
 *   isConnected={true}
 *   isConnecting={false}
 * />
 * ```
 */
"use client";

/** Props for the ConnectionStatus component. */
export interface ConnectionStatusProps {
  /** Whether WebSocket is currently connected. */
  isConnected: boolean;
  /** Whether WebSocket is currently attempting to connect. */
  isConnecting: boolean;
  /** Whether to show compact version (default: false). */
  compact?: boolean;
  /** Whether to show signal strength indicator (default: true). */
  showSignal?: boolean;
}

/**
 * Connection status indicator component.
 *
 * [From]: specs/004-ai-chatbot/research.md - Section 5
 */
export function ConnectionStatus({
  isConnected,
  isConnecting,
  compact = false,
  showSignal = true,
}: ConnectionStatusProps) {
  const getStatusDisplay = (): {
    dotColor: string;
    dotAnimate: string;
    textColor: string;
    text: string;
  } => {
    if (isConnected) {
      return {
        dotColor: "bg-green-500",
        dotAnimate: "animate-pulse",
        textColor: "text-green-600 dark:text-green-400",
        text: "Live",
      };
    }
    if (isConnecting) {
      return {
        dotColor: "bg-yellow-500",
        dotAnimate: "animate-ping",
        textColor: "text-yellow-600 dark:text-yellow-400",
        text: "Connecting...",
      };
    }
    return {
      dotColor: "bg-gray-400",
      dotAnimate: "",
      textColor: "text-gray-500 dark:text-gray-400",
      text: "Offline",
    };
  };

  const { dotColor, dotAnimate, textColor, text } = getStatusDisplay();

  if (compact) {
    return (
      <div className="flex items-center gap-1.5">
        <span
          className={`w-2 h-2 rounded-full transition-colors ${dotColor} ${dotAnimate}`}
          aria-label={text}
        />
        <span className={`text-xs ${textColor}`}>{text}</span>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between px-3 py-1.5 border-b border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-gray-900/50">
      <div className="flex items-center gap-2 text-sm">
        {/* Connection dot */}
        <span
          className={`w-2 h-2 rounded-full transition-colors ${dotColor} ${dotAnimate}`}
          aria-label={`WebSocket connection: ${text}`}
        />

        {/* Connection text */}
        <span className={textColor}>{text}</span>

        {/* Connection info tooltip */}
        {!isConnected && !isConnecting && (
          <span className="text-xs text-gray-400 dark:text-gray-500 ml-1">
            (Real-time updates unavailable)
          </span>
        )}
      </div>

      {/* Signal strength indicator */}
      {showSignal && isConnected && (
        <div className="flex gap-0.5 items-end h-3" aria-label="Signal strength">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className={`w-1 bg-green-500 rounded-sm opacity-80`}
              style={{
                height: `${i * 3}px`,
                animationDelay: `${i * 100}ms`,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

/** Loading skeleton for connection status. */
export function ConnectionStatusSkeleton() {
  return (
    <div className="flex items-center justify-between px-3 py-1.5 border-b border-gray-200 dark:border-gray-800">
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-gray-300 dark:bg-gray-700 animate-pulse" />
        <div className="h-4 w-16 bg-gray-300 dark:bg-gray-700 rounded animate-pulse" />
      </div>
      <div className="flex gap-0.5 h-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="w-1 bg-gray-300 dark:bg-gray-700 rounded-sm animate-pulse"
            style={{ height: `${i * 3}px` }}
          />
        ))}
      </div>
    </div>
  );
}
