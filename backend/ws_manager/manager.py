"""WebSocket ConnectionManager for multi-client broadcasting.

[Task]: T068
[From]: specs/004-ai-chatbot/tasks.md

This module provides connection management for WebSocket connections,
supporting multiple concurrent connections per user (e.g., multiple browser tabs).
"""
import asyncio
import logging
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger("websockets.manager")


class ConnectionManager:
    """Manages WebSocket connections for broadcasting progress events.

    [From]: specs/004-ai-chatbot/research.md - Section 4

    This manager:
    - Tracks multiple WebSocket connections per user_id
    - Supports broadcasting to all connections for a user
    - Handles connection lifecycle (connect, disconnect, cleanup)
    - Provides graceful handling of connection errors

    Attributes:
        active_connections: Mapping of user_id to list of WebSocket connections
    """

    def __init__(self) -> None:
        """Initialize the connection manager with empty connection tracking."""
        # user_id -> list of WebSocket connections
        # Supports multiple tabs per user
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection.

        [From]: specs/004-ai-chatbot/research.md - Section 4

        Args:
            user_id: The user's unique identifier (UUID string)
            websocket: The WebSocket connection to register

        Sends a connection_established event to the client upon successful connection.
        """
        await websocket.accept()

        # Initialize connection list for new users
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        # Add this connection to the user's list
        self.active_connections[user_id].append(websocket)

        logger.info(f"WebSocket connected for user {user_id}. "
                    f"Total connections for user: {len(self.active_connections[user_id])}")

        # Send confirmation event to client
        await self.send_personal({
            "event_type": "connection_established",
            "message": "Connected to real-time updates",
            "user_id": user_id,
        }, websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        """Remove a WebSocket connection from tracking.

        [From]: specs/004-ai-chatbot/research.md - Section 4

        Args:
            user_id: The user's unique identifier
            websocket: The WebSocket connection to remove

        Cleans up empty connection lists to prevent memory leaks.
        """
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"WebSocket disconnected for user {user_id}. "
                            f"Remaining connections: {len(self.active_connections[user_id])}")

                # Clean up empty connection lists
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    logger.debug(f"Removed empty connection list for user {user_id}")
            except ValueError:
                # Connection already removed
                logger.warning(f"Attempted to remove non-existent connection for user {user_id}")

    async def send_personal(self, message: dict, websocket: WebSocket) -> None:
        """Send a message to a specific WebSocket connection.

        [From]: specs/004-ai-chatbot/research.md - Section 4

        Args:
            message: The message dictionary to send (will be JSON serialized)
            websocket: The target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message to WebSocket: {e}")
            # Don't raise - connection may be closing

    async def broadcast(self, user_id: str, message: dict) -> None:
        """Send a message to all active connections for a user.

        [From]: specs/004-ai-chatbot/research.md - Section 4

        This is the primary method for sending progress events to all
        browser tabs/devices a user has open.

        Args:
            user_id: The user's unique identifier
            message: The message dictionary to broadcast (will be JSON serialized)

        Handles connection errors gracefully - if a connection fails,
        it's removed but other connections continue to receive messages.
        """
        if user_id not in self.active_connections:
            logger.debug(f"No active connections for user {user_id}")
            return

        # Track failed connections for cleanup
        failed_connections: List[WebSocket] = []

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to connection for user {user_id}: {e}")
                failed_connections.append(connection)

        # Clean up failed connections
        for failed in failed_connections:
            self.disconnect(user_id, failed)

    def get_connection_count(self, user_id: str) -> int:
        """Get the number of active connections for a user.

        [From]: specs/004-ai-chatbot/research.md - Section 4

        Args:
            user_id: The user's unique identifier

        Returns:
            The number of active WebSocket connections for this user
        """
        return len(self.active_connections.get(user_id, []))

    async def broadcast_to_all(self, message: dict) -> None:
        """Broadcast a message to all connected users.

        [From]: specs/004-ai-chatbot/research.md - Section 4

        This is useful for system-wide announcements or maintenance notices.

        Args:
            message: The message dictionary to broadcast
        """
        for user_id in list(self.active_connections.keys()):
            await self.broadcast(user_id, message)

    async def close_all_connections(self) -> None:
        """Close all active WebSocket connections.

        Useful for server shutdown or maintenance.
        """
        for user_id, connections in list(self.active_connections.items()):
            for connection in connections:
                try:
                    await connection.close()
                except Exception:
                    pass  # Connection may already be closed
        self.active_connections.clear()
        logger.info("All WebSocket connections closed")


# Global singleton instance
# [From]: specs/004-ai-chatbot/research.md - Section 4
# Import this instance in other modules to use the connection manager
manager = ConnectionManager()


async def get_manager() -> ConnectionManager:
    """Dependency injection helper for FastAPI routes.

    Returns:
        The global ConnectionManager instance
    """
    return manager
