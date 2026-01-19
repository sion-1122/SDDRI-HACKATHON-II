/** Custom React hook for WebSocket connection with auto-reconnect.
 *
 * [Task]: T073
 * [From]: specs/004-ai-chatbot/tasks.md
 *
 * This hook manages WebSocket connection lifecycle for real-time progress events:
 * - Auto-connects on mount
 * - Auto-reconnects with exponential backoff on disconnect
 * - Handles connection state (connecting, connected, disconnected, error)
 * - Parses JSON event messages
 * - Cleans up connection on unmount
 *
 * @example
 * ```tsx
 * const { isConnected, lastEvent } = useWebSocket(userId, {
 *   onEvent: (event) => console.log('Progress:', event),
 *   onConnectionChange: (connected) => console.log('Connected:', connected)
 * });
 * ```
 */
"use client";

import { useEffect, useRef, useState, useCallback } from "react";

/** WebSocket event types for AI agent progress. */
export interface ToolProgressEvent {
  event_type:
    | "connection_established"
    | "agent_thinking"
    | "tool_starting"
    | "tool_progress"
    | "tool_complete"
    | "tool_error"
    | "agent_done";
  tool?: string;
  task_id?: string;
  count?: number;
  message: string;
  result?: Record<string, unknown>;
  error?: string;
}

/** Options for the useWebSocket hook. */
export interface WebSocketOptions {
  /** Called when a new event is received from the server. */
  onEvent: (event: ToolProgressEvent) => void;
  /** Called when connection state changes. */
  onConnectionChange?: (connected: boolean) => void;
  /** Called when a connection error occurs. */
  onError?: (error: Event) => void;
  /** Base URL for WebSocket connection (default: ws://localhost:8000). */
  baseUrl?: string;
  /** Reconnection delay in milliseconds (default: 3000). */
  reconnectDelay?: number;
}

/** Return value of the useWebSocket hook. */
export interface WebSocketReturn {
  /** Whether WebSocket is currently connected. */
  isConnected: boolean;
  /** Whether WebSocket is currently attempting to connect. */
  isConnecting: boolean;
  /** The most recent event received from the server. */
  lastEvent: ToolProgressEvent | null;
  /** Manually disconnect the WebSocket. */
  disconnect: () => void;
  /** Manually reconnect the WebSocket. */
  reconnect: () => void;
}

/**
 * Custom React hook for managing WebSocket connections.
 *
 * [From]: specs/004-ai-chatbot/research.md - Section 5
 */
export function useWebSocket(
  userId: string,
  options: WebSocketOptions
): WebSocketReturn {
  const {
    onEvent,
    onConnectionChange,
    onError,
    baseUrl = "ws://localhost:8000",
    reconnectDelay = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(true);
  const [lastEvent, setLastEvent] = useState<ToolProgressEvent | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  // Use refs for callbacks to prevent connection recreation on every render
  const onEventRef = useRef(onEvent);
  const onConnectionChangeRef = useRef(onConnectionChange);
  const onErrorRef = useRef(onError);

  // Update refs when callbacks change
  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    onConnectionChangeRef.current = onConnectionChange;
  }, [onConnectionChange]);

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  /**
   * Establish WebSocket connection.
   * [From]: specs/004-ai-chatbot/research.md - Section 5
   */
  const connect = useCallback(() => {
    // Prevent duplicate connections
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    // Clean up any existing connection before creating a new one
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnecting(true);

    // Construct WebSocket URL
    // Note: The WebSocket route is at /api/ws/{userId}/chat
    // [From]: specs/004-ai-chatbot/research.md - Section 5
    const wsUrl = `${baseUrl}/api/ws/${userId}/chat`;

    console.log('[WebSocket] Connecting to:', wsUrl);
    console.log('[WebSocket] userId:', userId);

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        if (!mountedRef.current) return;

        console.log('[WebSocket] Connected');
        setIsConnected(true);
        setIsConnecting(false);
        onConnectionChangeRef.current?.(true);
      };

      ws.onclose = (event) => {
        if (!mountedRef.current) return;

        console.log('[WebSocket] Closed:', event.code, event.reason);
        setIsConnected(false);
        setIsConnecting(false);
        onConnectionChangeRef.current?.(false);

        // Auto-reconnect after delay (unless intentionally closed)
        if (event.code !== 1000) {
          reconnectTimeoutRef.current = setTimeout(() => {
            if (mountedRef.current) {
              connect();
            }
          }, reconnectDelay);
        }
      };

      ws.onerror = (error) => {
        if (!mountedRef.current) return;

        console.error('[WebSocket] Error:', {
          type: error.type,
          target: { url: (error.target as any).url, readyState: (error.target as any).readyState }
        });
        setIsConnecting(false);
        onErrorRef.current?.(error);
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;

        try {
          const parsed = JSON.parse(event.data) as ToolProgressEvent;
          console.log('[WebSocket] Message:', parsed);
          setLastEvent(parsed);
          onEventRef.current(parsed);
        } catch (err) {
          console.error("Failed to parse WebSocket message:", err);
        }
      };

      wsRef.current = ws;
    } catch (err) {
      console.error("Failed to create WebSocket:", err);
      setIsConnecting(false);
    }
  }, [userId, baseUrl, reconnectDelay]);

  /**
   * Disconnect WebSocket and clear reconnect timeout.
   * [From]: specs/004-ai-chatbot/research.md - Section 5
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, "Component unmounted");
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
  }, []);

  /**
   * Manually trigger reconnection.
   */
  const reconnect = useCallback(() => {
    disconnect();
    // Small delay before reconnecting
    setTimeout(() => {
      if (mountedRef.current) {
        connect();
      }
    }, 100);
  }, [disconnect, connect]);

  /**
   * Auto-connect on mount and cleanup on unmount.
   * [From]: specs/004-ai-chatbot/research.md - Section 5
   */
  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [connect, disconnect]);

  // Reconnect when userId changes
  const prevUserIdRef = useRef<string>();
  useEffect(() => {
    if (prevUserIdRef.current !== undefined && prevUserIdRef.current !== userId) {
      // User ID changed, reconnect with new user ID
      reconnect();
    }
    prevUserIdRef.current = userId;
  }, [userId, reconnect]);

  return {
    isConnected,
    isConnecting,
    lastEvent,
    disconnect,
    reconnect,
  };
}
