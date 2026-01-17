"""Chat API endpoint for AI-powered task management.

[Task]: T015
[From]: specs/004-ai-chatbot/tasks.md

This endpoint provides a conversational interface for task management.
Users can create, list, update, complete, and delete tasks through natural language.
"""
import uuid
from datetime import datetime
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session

from core.database import get_db
from core.validators import validate_message_length
from models.message import Message, MessageRole
from models.conversation import Conversation
from ai_agent import run_agent, is_gemini_configured
from services.conversation import (
    get_or_create_conversation,
    load_conversation_history,
    update_conversation_timestamp
)
from services.rate_limiter import check_rate_limit


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
    db: Session = Depends(get_db)
):
    """Process user message through AI agent and return response.

    [From]: specs/004-ai-chatbot/spec.md - US1

    This endpoint:
    1. Persists user message to database
    2. Loads conversation history if conversation_id provided
    3. Creates new conversation if conversation_id not provided
    4. Sends conversation history to AI agent
    5. Persists AI response to database
    6. Returns AI response with any task modifications

    Args:
        user_id: User ID (UUID string from path)
        request: Chat request with message and optional conversation_id
        db: Database session

    Returns:
        ChatResponse with AI response, conversation_id, and task references

    Raises:
        HTTPException 400: Invalid message content
        HTTPException 503: AI service unavailable
    """
    # Check if Gemini API is configured
    # [From]: specs/004-ai-chatbot/tasks.md - T022
    if not is_gemini_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured. Please contact administrator."
        )

    # Validate user_id format
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # Validate message content
    try:
        validated_message = validate_message_length(request.message)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Check rate limit
    # [From]: specs/004-ai-chatbot/spec.md - NFR-011
    # [From]: T021 - Implement daily message limit enforcement (100/day)
    allowed, remaining, reset_time = check_rate_limit(db, user_uuid)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Daily message limit exceeded",
                "limit": 100,
                "resets_at": reset_time.isoformat() if reset_time else None
            }
        )

    # Get or create conversation
    # [From]: T016 - Implement conversation history loading
    # [From]: T035 - Handle auto-deleted conversations gracefully
    conversation_id: uuid.UUID

    if request.conversation_id:
        # Load existing conversation using service
        try:
            conv_uuid = uuid.UUID(request.conversation_id)
            conversation = get_or_create_conversation(
                db=db,
                user_id=user_uuid,
                conversation_id=conv_uuid
            )
            conversation_id = conversation.id
        except (ValueError, KeyError) as e:
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

    # Persist user message before AI processing
    # [From]: T017 - Add user message persistence before AI processing
    user_message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        user_id=user_uuid,
        role=MessageRole.USER,
        content=validated_message,
        created_at=datetime.utcnow()
    )
    db.add(user_message)
    db.commit()

    # Load conversation history using service
    # [From]: T016 - Implement conversation history loading
    conversation_history = load_conversation_history(
        db=db,
        conversation_id=conversation_id
    )

    # Run AI agent
    # [From]: T014 - Initialize OpenAI Agents SDK with Gemini
    try:
        ai_response_text = await run_agent(
            messages=conversation_history,
            user_id=user_id
        )
    except ValueError as e:
        # Configuration errors (missing API key, invalid model)
        # [From]: T022 - Add error handling for Gemini API unavailability
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "AI service configuration error", "message": str(e)}
        )
    except ConnectionError as e:
        # Network/connection issues
        # [From]: T022 - Add error handling for Gemini API unavailability
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "AI service unreachable", "message": str(e)}
        )
    except TimeoutError as e:
        # Timeout errors
        # [From]: T022 - Add error handling for Gemini API unavailability
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"error": "AI service timeout", "message": str(e)}
        )
    except Exception as e:
        # Other errors (rate limits, authentication, context, etc.)
        # [From]: T022 - Add error handling for Gemini API unavailability
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "AI service error", "message": str(e)}
        )

    # Persist AI response
    # [From]: T018 - Add AI response persistence after processing
    ai_message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        user_id=user_uuid,
        role=MessageRole.ASSISTANT,
        content=ai_response_text,
        created_at=datetime.utcnow()
    )
    db.add(ai_message)
    db.commit()

    # Update conversation timestamp using service
    update_conversation_timestamp(db=db, conversation_id=conversation_id)

    # TODO: Parse AI response for task references
    # This will be enhanced in future tasks to extract task IDs from AI responses
    task_references: list[TaskReference] = []

    return ChatResponse(
        response=ai_response_text,
        conversation_id=str(conversation_id),
        tasks=task_references
    )
