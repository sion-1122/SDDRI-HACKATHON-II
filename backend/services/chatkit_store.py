"""PostgreSQL Store implementation for ChatKit SDK.

[Task]: T009
[From]: specs/010-chatkit-migration/data-model.md - ChatKit SDK Interface Requirements
[From]: specs/010-chatkit-migration/contracts/backend.md - Store Interface Implementation

This module implements the ChatKit Store interface using SQLModel and PostgreSQL.
The Store interface is required by ChatKit's Python SDK for thread and message persistence.

ChatKit Store Protocol Methods:
- list_threads: List threads for a user with pagination
- get_thread: Get a specific thread by ID
- create_thread: Create a new thread
- update_thread: Update thread metadata
- delete_thread: Delete a thread
- list_messages: List messages in a thread
- get_message: Get a specific message
- create_message: Create a new message
- update_message: Update a message
- delete_message: Delete a message
"""
import uuid
from datetime import datetime
from typing import Any, Optional
from sqlmodel import Session, select, col
from sqlalchemy.ext.asyncio import AsyncSession

from models.thread import Thread
from models.message import Message, MessageRole


class PostgresChatKitStore:
    """PostgreSQL implementation of ChatKit Store interface.

    [From]: specs/010-chatkit-migration/data-model.md - Store Interface

    This store provides thread and message persistence for ChatKit using
    the existing SQLModel models and PostgreSQL database.

    Note: The ChatKit SDK uses a Protocol-based interface. The actual
    protocol types (ThreadMetadata, MessageItem, etc.) would be imported
    from the openai_chatkit package. For this implementation, we use
    dictionary-based representations until the SDK is installed.

    Usage:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from services.chatkit_store import PostgresChatKitStore

        engine = create_async_engine(database_url)
        async with AsyncSession(engine) as session:
            store = PostgresChatKitStore(session)
            thread = await store.create_thread(
                user_id="user-123",
                title="My Conversation",
                metadata={"tag": "important"}
            )
    """

    def __init__(self, session: AsyncSession):
        """Initialize the store with a database session.

        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session

    async def list_threads(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[dict]:
        """List threads for a user with pagination.

        [From]: specs/010-chatkit-migration/data-model.md - Retrieve User's Conversations

        Args:
            user_id: User ID to filter threads
            limit: Maximum number of threads to return (default: 50)
            offset: Number of threads to skip (default: 0)

        Returns:
            List of thread metadata dictionaries
        """
        stmt = (
            select(Thread)
            .where(Thread.user_id == uuid.UUID(user_id))
            .order_by(Thread.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        threads = result.scalars().all()

        return [
            {
                "id": str(thread.id),
                "user_id": str(thread.user_id),
                "title": thread.title,
                "metadata": thread.thread_metadata or {},
                "created_at": thread.created_at.isoformat(),
                "updated_at": thread.updated_at.isoformat(),
            }
            for thread in threads
        ]

    async def get_thread(self, thread_id: str) -> Optional[dict]:
        """Get a specific thread by ID.

        Args:
            thread_id: Thread UUID as string

        Returns:
            Thread metadata dictionary or None if not found
        """
        stmt = select(Thread).where(Thread.id == uuid.UUID(thread_id))
        result = await self.session.execute(stmt)
        thread = result.scalar_one_or_none()

        if thread is None:
            return None

        return {
            "id": str(thread.id),
            "user_id": str(thread.user_id),
            "title": thread.title,
            "metadata": thread.thread_metadata or {},
            "created_at": thread.created_at.isoformat(),
            "updated_at": thread.updated_at.isoformat(),
        }

    async def create_thread(
        self,
        user_id: str,
        title: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """Create a new thread.

        Args:
            user_id: User ID who owns the thread
            title: Optional thread title
            metadata: Optional thread metadata

        Returns:
            Created thread metadata dictionary
        """
        thread = Thread(
            user_id=uuid.UUID(user_id),
            title=title,
            thread_metadata=metadata or {},
        )
        self.session.add(thread)
        await self.session.commit()
        await self.session.refresh(thread)

        return {
            "id": str(thread.id),
            "user_id": str(thread.user_id),
            "title": thread.title,
            "metadata": thread.thread_metadata or {},
            "created_at": thread.created_at.isoformat(),
            "updated_at": thread.updated_at.isoformat(),
        }

    async def update_thread(
        self,
        thread_id: str,
        title: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[dict]:
        """Update a thread.

        Args:
            thread_id: Thread UUID as string
            title: New title (optional)
            metadata: New metadata (optional)

        Returns:
            Updated thread metadata dictionary or None if not found
        """
        stmt = select(Thread).where(Thread.id == uuid.UUID(thread_id))
        result = await self.session.execute(stmt)
        thread = result.scalar_one_or_none()

        if thread is None:
            return None

        if title is not None:
            thread.title = title
        if metadata is not None:
            thread.thread_metadata = metadata
        thread.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(thread)

        return {
            "id": str(thread.id),
            "user_id": str(thread.user_id),
            "title": thread.title,
            "metadata": thread.thread_metadata or {},
            "created_at": thread.created_at.isoformat(),
            "updated_at": thread.updated_at.isoformat(),
        }

    async def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread.

        Args:
            thread_id: Thread UUID as string

        Returns:
            True if deleted, False if not found
        """
        stmt = select(Thread).where(Thread.id == uuid.UUID(thread_id))
        result = await self.session.execute(stmt)
        thread = result.scalar_one_or_none()

        if thread is None:
            return False

        await self.session.delete(thread)
        await self.session.commit()
        return True

    async def list_messages(
        self,
        thread_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[dict]:
        """List messages in a thread.

        [From]: specs/010-chatkit-migration/data-model.md - Retrieve Conversation Messages

        Args:
            thread_id: Thread UUID as string
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of message item dictionaries
        """
        stmt = (
            select(Message)
            .where(Message.thread_id == uuid.UUID(thread_id))
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        messages = result.scalars().all()

        return [
            {
                "id": str(msg.id),
                "type": "message",
                "role": msg.role.value,
                "content": [{"type": "text", "text": msg.content}],
                "tool_calls": msg.tool_calls,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]

    async def get_message(self, message_id: str) -> Optional[dict]:
        """Get a specific message by ID.

        Args:
            message_id: Message UUID as string

        Returns:
            Message item dictionary or None if not found
        """
        stmt = select(Message).where(Message.id == uuid.UUID(message_id))
        result = await self.session.execute(stmt)
        message = result.scalar_one_or_none()

        if message is None:
            return None

        return {
            "id": str(message.id),
            "type": "message",
            "role": message.role.value,
            "content": [{"type": "text", "text": message.content}],
            "tool_calls": message.tool_calls,
            "created_at": message.created_at.isoformat(),
        }

    async def create_message(
        self,
        thread_id: str,
        item: dict
    ) -> dict:
        """Create a new message in a thread.

        Args:
            thread_id: Thread UUID as string
            item: Message item from ChatKit (UserMessageItem or ClientToolCallOutputItem)

        Returns:
            Created message item dictionary

        Raises:
            ValueError: If item format is invalid
        """
        # Extract content from ChatKit item format
        # ChatKit uses: {"type": "message", "role": "user", "content": [{"type": "text", "text": "..."}]}
        item_type = item.get("type", "message")
        role = item.get("role", "user")

        # Extract text content from content array
        content_array = item.get("content", [])
        text_content = ""
        for content_block in content_array:
            if content_block.get("type") == "text":
                text_content = content_block.get("text", "")
                break

        # Handle client tool output items
        if item_type == "client_tool_call_output":
            text_content = item.get("output", "")

        message = Message(
            thread_id=uuid.UUID(thread_id),
            role=MessageRole(role),
            content=text_content,
            tool_calls=item.get("tool_calls"),
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        # Update thread's updated_at timestamp
        thread_stmt = select(Thread).where(Thread.id == uuid.UUID(thread_id))
        thread_result = await self.session.execute(thread_stmt)
        thread = thread_result.scalar_one_or_none()
        if thread:
            thread.updated_at = datetime.utcnow()
            await self.session.commit()

        return {
            "id": str(message.id),
            "type": "message",
            "role": message.role.value,
            "content": [{"type": "text", "text": message.content}],
            "tool_calls": message.tool_calls,
            "created_at": message.created_at.isoformat(),
        }

    async def update_message(
        self,
        message_id: str,
        item: dict
    ) -> Optional[dict]:
        """Update a message.

        Args:
            message_id: Message UUID as string
            item: Updated message item

        Returns:
            Updated message item dictionary or None if not found
        """
        stmt = select(Message).where(Message.id == uuid.UUID(message_id))
        result = await self.session.execute(stmt)
        message = result.scalar_one_or_none()

        if message is None:
            return None

        # Update content if provided
        content_array = item.get("content", [])
        if content_array:
            for content_block in content_array:
                if content_block.get("type") == "text":
                    message.content = content_block.get("text", message.content)
                    break

        # Update tool_calls if provided
        if "tool_calls" in item:
            message.tool_calls = item["tool_calls"]

        await self.session.commit()
        await self.session.refresh(message)

        return {
            "id": str(message.id),
            "type": "message",
            "role": message.role.value,
            "content": [{"type": "text", "text": message.content}],
            "tool_calls": message.tool_calls,
            "created_at": message.created_at.isoformat(),
        }

    async def delete_message(self, message_id: str) -> bool:
        """Delete a message.

        Args:
            message_id: Message UUID as string

        Returns:
            True if deleted, False if not found
        """
        stmt = select(Message).where(Message.id == uuid.UUID(message_id))
        result = await self.session.execute(stmt)
        message = result.scalar_one_or_none()

        if message is None:
            return False

        await self.session.delete(message)
        await self.session.commit()
        return True
