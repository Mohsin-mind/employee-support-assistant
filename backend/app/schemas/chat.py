from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from backend.app.core.constants import MessageRole


class ConversationCreate(BaseModel):
    """Payload to initiate a new conversation session."""
    employee_id: Optional[int] = Field(None, description="Associated employee ID if authenticated")
    title: Optional[str] = Field(default="New Conversation", max_length=255, description="Chat topic title")


class ConversationUpdate(BaseModel):
    """Payload to update conversation title."""
    title: str = Field(..., min_length=1, max_length=255)


class ConversationMessageCreate(BaseModel):
    """Payload to append a new message turn into a conversation."""
    role: MessageRole = Field(..., description="Message author role: system, user, assistant, tool")
    content: str = Field(..., min_length=1, description="Message text content")
    token_count: Optional[int] = Field(None, ge=0, description="Estimated token count")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Turn-specific metadata or tool call details")


class ConversationMessageResponse(BaseModel):
    """Response representation of a chat message."""
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    token_count: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    """Response representation of a conversation session without messages."""
    id: str
    employee_id: Optional[int] = None
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationDetailResponse(ConversationResponse):
    """Detailed conversation response including message history."""
    messages: List[ConversationMessageResponse] = []
