"""Chat API endpoint for AI-powered task management.

[Task]: T015, T071
[From]: specs/004-ai-chatbot/tasks.md

This endpoint provides a conversational interface for task management.
Users can create, list, update, complete, and delete tasks through natural language.

Also includes WebSocket endpoint for real-time progress streaming.
"""
import uuid
import logging
import asyncio
from datetime import datetime
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, status, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel, Field, field_validator, ValidationError
from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError

from core.database import get_db
from core.validators import validate_message_length
from core.security import decode_access_token
from models.message import Message, MessageRole
from services.security import sanitize_message
from models.conversation import Conversation
from ai_agent import run_agent_with_streaming, is_gemini_configured
from services.conversation import (
    get_or_create_conversation,
    load_conversation_history,
    update_conversation_timestamp
)
from services.rate_limiter import check_rate_limit
from ws_manager.manager import manager


# Configure error logger
error_logger = logging.getLogger("api.errors")
error_logger.setLevel(logging.ERROR)


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint.

    [From]: specs/004-ai-chatbot/plan.md - API Contract
    """
    message: str = Field(
        ...,
        description="User message content",
        min_length=1,
        max_length=10000  # FR-042
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Optional conversation ID to continue existing conversation"
    )

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message content."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        if len(v) > 10000:
            raise ValueError("Message content exceeds maximum length of 10,000 characters")
        return v.strip()


class TaskReference(BaseModel):
    """Reference to a task created or modified by AI."""
    id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    completed: bool = False


class ChatResponse(BaseModel):
    """Response model for chat endpoint.

    [From]: specs/004-ai-chatbot/plan.md - API Contract
    """
    response: str = Field(
        ...,
        description="AI assistant's text response"
    )
    conversation_id: str = Field(
        ...,
        description="Conversation ID (new or existing)"
    )
    tasks: list[TaskReference] = Field(
        default_factory=list,
        description="List of tasks created or modified in this interaction"
    )


# Create API router
router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    user_id: str,
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Process user message through AI agent and return response.

    [From]: specs/004-ai-chatbot/spec.md - US1

    This endpoint:
    1. Validates user input and rate limits
    2. Gets or creates conversation
    3. Runs AI agent with WebSocket progress streaming
    4. Returns AI response immediately
    5. Saves messages to DB in background (non-blocking)

    Args:
        user_id: User ID (UUID string from path)
        request: Chat request with message and optional conversation_id
        background_tasks: FastAPI background tasks for non-blocking DB saves
        db: Database session

    Returns:
        ChatResponse with AI response, conversation_id, and task references

    Raises:
        HTTPException 400: Invalid message content
        HTTPException 503: AI service unavailable
    """
    # Check if Gemini API is configured
    # [From]: specs/004-ai-chatbot/tasks.md - T022
    # [From]: T060 - Add comprehensive error messages for edge cases
    if not is_gemini_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "AI service unavailable",
                "message": "The AI service is currently not configured. Please ensure GEMINI_API_KEY is set in the environment.",
                "suggestion": "Contact your administrator or check your API key configuration."
            }
        )

    # Validate user_id format
    # [From]: T060 - Add comprehensive error messages for edge cases
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid user ID",
                "message": f"User ID '{user_id}' is not a valid UUID format.",
                "expected_format": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "suggestion": "Ensure you are using a valid UUID for the user_id path parameter."
            }
        )

    # Validate message content
    # [From]: T060 - Add comprehensive error messages for edge cases
    try:
        validated_message = validate_message_length(request.message)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Message validation failed",
                "message": str(e),
                "max_length": 10000,
                "suggestion": "Keep your message under 10,000 characters and ensure it contains meaningful content."
            }
        )

    # Sanitize message to prevent prompt injection
    # [From]: T057 - Implement prompt injection sanitization
    # [From]: T060 - Add comprehensive error messages for edge cases
    try:
        sanitized_message = sanitize_message(validated_message)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Message content blocked",
                "message": str(e),
                "suggestion": "Please rephrase your message without attempting to manipulate system instructions."
            }
        )

    # Check rate limit
    # [From]: specs/004-ai-chatbot/spec.md - NFR-011
    # [From]: T021 - Implement daily message limit enforcement (100/day)
    # [From]: T060 - Add comprehensive error messages for edge cases
    try:
        allowed, remaining, reset_time = check_rate_limit(db, user_uuid)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": "You have reached the daily message limit. Please try again later.",
                    "limit": 100,
                    "resets_at": reset_time.isoformat() if reset_time else None,
                    "suggestion": "Free tier accounts are limited to 100 messages per day. Upgrade for unlimited access."
                }
            )
    except HTTPException:
        # Re-raise HTTP exceptions (rate limit errors)
        raise
    except Exception as e:
        # Log unexpected errors but don't block the request
        error_logger.error(f"Rate limit check failed for user {user_id}: {e}")
        # Continue processing - fail open for rate limit errors

    # Get or create conversation
    # [From]: T016 - Implement conversation history loading
    # [From]: T035 - Handle auto-deleted conversations gracefully
    # [From]: T060 - Add comprehensive error messages for edge cases
    conversation_id: uuid.UUID

    if request.conversation_id:
        # Load existing conversation using service
        try:
            conv_uuid = uuid.UUID(request.conversation_id)
        except ValueError:
            # Invalid conversation_id format
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid conversation ID",
                    "message": f"Conversation ID '{request.conversation_id}' is not a valid UUID format.",
                    "suggestion": "Provide a valid UUID or omit the conversation_id to start a new conversation."
                }
            )

        try:
            conversation = get_or_create_conversation(
                db=db,
                user_id=user_uuid,
                conversation_id=conv_uuid
            )
            conversation_id = conversation.id
        except (KeyError, ValueError) as e:
            # Conversation may have been auto-deleted (90-day policy) or otherwise not found
            # [From]: T035 - Handle auto-deleted conversations gracefully
            # Create a new conversation instead of failing
            conversation = get_or_create_conversation(
                db=db,
                user_id=user_uuid
            )
            conversation_id = conversation.id
    else:
        # Create new conversation using service
        conversation = get_or_create_conversation(
            db=db,
            user_id=user_uuid
        )
        conversation_id = conversation.id

    # Load conversation history using service
    # [From]: T016 - Implement conversation history loading
    # [From]: T060 - Add comprehensive error messages for edge cases
    try:
        conversation_history = load_conversation_history(
            db=db,
            conversation_id=conversation_id
        )
    except SQLAlchemyError as e:
        error_logger.error(f"Database error loading conversation history for {conversation_id}: {e}")
        # Continue with empty history if load fails
        conversation_history = []

    # Prepare user message for background save
    user_message_id = uuid.uuid4()
    user_message_data = {
        "id": user_message_id,
        "conversation_id": conversation_id,
        "user_id": user_uuid,
        "role": MessageRole.USER,
        "content": sanitized_message,
        "created_at": datetime.utcnow()
    }

    # Run AI agent with streaming (broadcasts WebSocket events)
    # [From]: T014 - Initialize OpenAI Agents SDK with Gemini
    # [From]: T072 - Use streaming agent for real-time progress
    # [From]: T060 - Add comprehensive error messages for edge cases
    try:
        ai_response_text = await run_agent_with_streaming(
            messages=conversation_history,
            user_id=user_id
        )
    except ValueError as e:
        # Configuration errors (missing API key, invalid model)
        # [From]: T022 - Add error handling for Gemini API unavailability
        error_logger.error(f"AI configuration error for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "AI service configuration error",
                "message": str(e),
                "suggestion": "Verify GEMINI_API_KEY and GEMINI_MODEL are correctly configured."
            }
        )
    except ConnectionError as e:
        # Network/connection issues
        # [From]: T022 - Add error handling for Gemini API unavailability
        error_logger.error(f"AI connection error for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "AI service unreachable",
                "message": "Could not connect to the AI service. Please check your network connection.",
                "suggestion": "If the problem persists, the AI service may be temporarily down."
            }
        )
    except TimeoutError as e:
        # Timeout errors
        # [From]: T022 - Add error handling for Gemini API unavailability
        error_logger.error(f"AI timeout error for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "error": "AI service timeout",
                "message": "The AI service took too long to respond. Please try again.",
                "suggestion": "Your message may be too complex. Try breaking it into smaller requests."
            }
        )
    except Exception as e:
        # Other errors (rate limits, authentication, context, etc.)
        # [From]: T022 - Add error handling for Gemini API unavailability
        error_logger.error(f"Unexpected AI error for user {user_id}: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "AI service error",
                "message": f"An unexpected error occurred: {str(e)}",
                "suggestion": "Please try again later or contact support if the problem persists."
            }
        )

    # Prepare AI response for background save
    ai_message_data = {
        "id": uuid.uuid4(),
        "conversation_id": conversation_id,
        "user_id": user_uuid,
        "role": MessageRole.ASSISTANT,
        "content": ai_response_text,
        "created_at": datetime.utcnow()
    }

    # Save messages to DB in background (non-blocking)
    # This significantly improves response time
    def save_messages_to_db():
        """Background task to save messages to database."""
        try:
            from core.database import engine
            from sqlmodel import Session

            # Create a new session for background task
            bg_db = Session(engine)

            try:
                # Save user message
                user_msg = Message(**user_message_data)
                bg_db.add(user_msg)

                # Save AI response
                ai_msg = Message(**ai_message_data)
                bg_db.add(ai_msg)

                bg_db.commit()

                # Update conversation timestamp
                try:
                    update_conversation_timestamp(db=bg_db, conversation_id=conversation_id)
                except SQLAlchemyError as e:
                    error_logger.error(f"Database error updating conversation timestamp for {conversation_id}: {e}")

            except SQLAlchemyError as e:
                error_logger.error(f"Background task: Database error saving messages for user {user_id}: {e}")
                bg_db.rollback()
            finally:
                bg_db.close()
        except Exception as e:
            error_logger.error(f"Background task: Unexpected error saving messages for user {user_id}: {e}")

    background_tasks.add_task(save_messages_to_db)

    # TODO: Parse AI response for task references
    # This will be enhanced in future tasks to extract task IDs from AI responses
    task_references: list[TaskReference] = []

    return ChatResponse(
        response=ai_response_text,
        conversation_id=str(conversation_id),
        tasks=task_references
    )


@router.websocket("/ws/{user_id}/chat")
async def websocket_chat(
    websocket: WebSocket,
    user_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat progress updates.

    [From]: specs/004-ai-chatbot/research.md - Section 4
    [Task]: T071

    This endpoint provides a WebSocket connection for receiving real-time
    progress events during AI agent execution. Events include:
    - connection_established: Confirmation of successful connection
    - agent_thinking: AI agent is processing
    - tool_starting: A tool is about to execute
    - tool_progress: Tool execution progress (e.g., "Found 3 tasks")
    - tool_complete: Tool finished successfully
    - tool_error: Tool execution failed
    - agent_done: AI agent finished processing

    Note: Authentication is handled implicitly by the frontend - users must
    be logged in to access the chat page. The WebSocket only broadcasts
    progress updates (not sensitive data), so strict auth is bypassed here.

    Connection URL format:
        ws://localhost:8000/ws/{user_id}/chat

    Args:
        websocket: The WebSocket connection instance
        user_id: User ID from URL path (used to route progress events)
        db: Database session (for any future DB operations)

    The connection is kept alive and can receive messages from the client,
    though currently it's primarily used for server-to-client progress updates.
    """
    # Connect the WebSocket (manager handles accept)
    # [From]: specs/004-ai-chatbot/research.md - Section 4
    await manager.connect(user_id, websocket)

    try:
        # Keep connection alive and listen for client messages
        # Currently, we don't expect many client messages, but we
        # maintain the connection to receive any control messages
        while True:
            # Wait for message from client (with timeout)
            data = await websocket.receive_text()

            # Handle client messages if needed
            # For now, we just acknowledge receipt
            # Future: could handle ping/pong for connection health
            if data:
                # Echo back a simple acknowledgment
                # (optional - mainly for debugging)
                pass

    except WebSocketDisconnect:
        # Normal disconnect - clean up
        manager.disconnect(user_id, websocket)
        error_logger.info(f"WebSocket disconnected normally for user {user_id}")

    except Exception as e:
        # Unexpected error - clean up and log
        error_logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id, websocket)

    finally:
        # Ensure disconnect is always called
        manager.disconnect(user_id, websocket)
