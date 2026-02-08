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
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Request
from pydantic import BaseModel, Field, field_validator, ValidationError
from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError

from core.database import get_db
from core.validators import validate_message_length
from core.security import decode_access_token
from models.message import Message, MessageRole
from services.security import sanitize_message
from models.conversation import Conversation
from ai_agent import run_agent, is_gemini_configured
from services.conversation import (
    get_or_create_conversation,
    load_conversation_history,
    update_conversation_timestamp
)
from services.rate_limiter import check_rate_limit


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

    # Add current user message to conversation history for AI processing
    # This is critical - the agent needs the user's current message in context
    messages_for_agent = conversation_history + [
        {"role": "user", "content": sanitized_message}
    ]

    # Run AI agent (non-streaming for legacy endpoint)
    # [From]: T014 - Initialize OpenAI Agents SDK with Gemini
    # NOTE: Streaming is now handled by ChatKit SSE endpoint
    # [From]: T060 - Add comprehensive error messages for edge cases
    try:
        ai_response_text = await run_agent(
            messages=messages_for_agent,
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


# ============================================================================
# ChatKit SSE Endpoint (Phase 010-chatkit-migration)
# ============================================================================

@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,  # Starlette Request object for raw body access
    background_tasks: BackgroundTasks,
):
    """ChatKit SSE endpoint for streaming chat with Gemini LLM.

    [Task]: T011
    [From]: specs/010-chatkit-migration/contracts/backend.md - ChatKit SSE Endpoint

    This endpoint implements the ChatKit protocol using Server-Sent Events (SSE).
    It replaces the WebSocket-based streaming with a simpler HTTP-based approach.

    Endpoint: POST /api/chatkit
    Response: Server-Sent Events (text/event-stream)

    Authentication: JWT via httpOnly cookie (auth_token)

    Request Body (ChatKit protocol):
        {
          "event": "conversation_item_created",
          "conversation_id": "<thread_uuid>",
          "item": {
            "type": "message",
            "role": "user",
            "content": [{"type": "text", "text": "Your message here"}]
          }
        }

    SSE Event Types:
        - message_delta: Streaming text content
        - tool_call_created: Tool invocation started
        - tool_call_done: Tool execution completed
        - message_done: Message fully streamed
        - error: Error occurred

    [From]: specs/010-chatkit-migration/research.md - Section 4
    """
    from fastapi import Response
    from fastapi.responses import StreamingResponse
    from starlette.requests import Request as StarletteRequest

    # Import for authentication
    from core.security import get_current_user_id_from_cookie

    # Get authenticated user ID from JWT cookie
    # [From]: specs/010-chatkit-migration/contracts/backend.md - Authentication
    try:
        user_id = await get_current_user_id_from_cookie(request)
        if not user_id:
            # Return error as SSE event
            async def error_stream():
                yield "event: error\n"
                yield 'data: {"detail": "Invalid authentication"}\n\n'
            return StreamingResponse(
                error_stream(),
                media_type="text/event-stream",
                status_code=401
            )
    except Exception as e:
        error_logger.error(f"Auth error in ChatKit endpoint: {e}")
        async def error_stream():
            yield "event: error\n"
            yield f'data: {{"detail": "Authentication failed"}}\n\n'
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            status_code=401
        )

    # Check rate limit before processing
    # [From]: specs/010-chatkit-migration/tasks.md - T020
    # [From]: specs/010-chatkit-migration/spec.md - FR-015
    try:
        from uuid import UUID
        from core.database import engine
        from sqlmodel import Session

        # Create synchronous session for rate limit check
        with Session(engine) as db:
            allowed, remaining, reset_time = check_rate_limit(db, UUID(user_id))

            if not allowed:
                # Rate limit exceeded
                async def rate_limit_stream():
                    yield "event: error\n"
                    import json
                    yield f'data: {json.dumps({"detail": "Daily message limit reached", "limit": 100, "resets_at": reset_time.isoformat() if reset_time else None})}\n\n'
                return StreamingResponse(
                    rate_limit_stream(),
                    media_type="text/event-stream",
                    status_code=429
                )
    except HTTPException:
        # Re-raise HTTP exceptions (rate limit errors)
        raise
    except Exception as e:
        # Log unexpected errors but don't block the request
        error_logger.error(f"Rate limit check failed for ChatKit endpoint: {e}")
        # Continue processing - fail open for rate limit errors

    # Create ChatKit server with synchronous database operations
    # [From]: specs/010-chatkit-migration/contracts/backend.md - Store Interface Implementation
    import json

    # Parse request body
    try:
        body = await request.body()
    except Exception as e:
        error_logger.error(f"Failed to read ChatKit request body: {e}")
        async def error_stream():
            yield "event: error\n"
            yield f'data: {{"detail": "Invalid request format"}}\n\n'
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            status_code=400
        )

    # Parse ChatKit protocol request
    try:
        request_data = json.loads(body.decode('utf-8'))
    except Exception as e:
        error_logger.error(f"Failed to parse ChatKit request: {e}")
        async def error_stream():
            yield "event: error\n"
            yield f'data: {{"detail": "Invalid JSON format"}}\n\n'
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            status_code=400
        )

    # Extract thread ID and message content
    conversation_id = request_data.get("conversation_id")
    item = request_data.get("item", {})
    event_type = request_data.get("event", "conversation_item_created")

    # Extract user message
    def extract_message_content(item_dict):
        content_array = item_dict.get("content", [])
        for content_block in content_array:
            if content_block.get("type") == "text":
                return content_block.get("text", "")
        return ""

    user_message = extract_message_content(item)
    if not user_message:
        async def error_stream():
            yield "event: error\n"
            yield f'data: {{"detail": "No message content provided"}}\n\n'
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            status_code=400
        )

    # Use synchronous database session for thread/message operations
    from core.database import engine
    from sqlmodel import Session

    # Get or create thread
    thread_id = conversation_id
    if not thread_id:
        # Create new thread for first message
        with Session(engine) as db:
            from models.thread import Thread
            import uuid
            new_thread = Thread(
                user_id=UUID(user_id),
                title=None,
                thread_metadata={}
            )
            db.add(new_thread)
            db.commit()
            db.refresh(new_thread)
            thread_id = str(new_thread.id)
            error_logger.info(f"Created new thread: {thread_id}")

    # Save user message to database
    with Session(engine) as db:
        from models.message import Message, MessageRole
        import uuid
        user_msg = Message(
            thread_id=UUID(thread_id) if thread_id else None,
            user_id=UUID(user_id),
            role=MessageRole.USER,
            content=user_message,
        )
        db.add(user_msg)
        db.commit()

    # Run AI agent and stream response
    # [Task]: T033 - Add SSE error handling for connection drops
    async def stream_chat_response():
        """Stream ChatKit events as SSE with timeout protection.

        [Task]: T034 - Timeout handling for long-running tool executions
        """
        try:
            # Import agent components
            from ai_agent import run_agent

            # Run agent with timeout protection
            async with asyncio.timeout(120):
                ai_response = await run_agent(
                    messages=[{"role": "user", "content": user_message}],
                    user_id=user_id
                )

            # Save assistant message to database
            with Session(engine) as db:
                from models.message import Message, MessageRole
                import uuid
                assistant_msg = Message(
                    thread_id=UUID(thread_id) if thread_id else None,
                    user_id=UUID(user_id),
                    role=MessageRole.ASSISTANT,
                    content=ai_response,
                )
                db.add(assistant_msg)
                db.commit()

            # Stream the response
            import json
            yield "event: message_delta\n"
            yield f'data: {json.dumps({"type": "text", "text": ai_response})}\n\n'

            # Send message done event
            yield "event: message_done\n"
            yield f'data: {json.dumps({"message_id": thread_id, "role": "assistant", "thread_id": thread_id})}\n\n'

        except TimeoutError:
            error_logger.error(f"Agent execution timeout for thread {thread_id}")
            import json
            yield "event: error\n"
            yield f'data: {json.dumps({"detail": "Request timed out", "message": "The AI assistant took too long to respond. Please try again."})}\n\n'
        except Exception as e:
            error_logger.error(f"Agent execution error: {e}", exc_info=True)
            import json
            yield "event: error\n"
            yield f'data: {json.dumps({"detail": "Processing error", "message": str(e)})}\n\n'

    # [Task]: T033 - Wrap with connection-aware streaming
    async def connection_aware_stream():
        """Stream SSE events with connection drop detection.

        [Task]: T033 - SSE error handling for connection drops
        """
        try:
            async for chunk in stream_chat_response():
                yield chunk
        except (ConnectionError, OSError) as e:
            # Client disconnected during streaming
            error_logger.info(f"Client disconnected during ChatKit streaming: {e}")
        except Exception as e:
            # Unexpected streaming error
            error_logger.error(f"Unexpected error during ChatKit streaming: {e}", exc_info=True)
            yield "event: error\n"
            yield f'data: {{"detail": "Streaming error", "message": str(e)}}\n\n'

    return StreamingResponse(
        connection_aware_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
