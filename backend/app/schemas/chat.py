"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """
    Incoming chat message from user.
    """
    message: str = Field(..., min_length=1, max_length=2000, description="The medical query from the user.")
    session_id: str = Field(
        default="default_session",
        description="Unique identifier for the chat session to track history in SQL."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "What are the symptoms of diabetes?",
                "session_id": "user_123_session"
            }
        }
    )


class ChatResponse(BaseModel):
    """
    Outgoing chat response with answer and sources.
    """
    answer: str = Field(..., description="The AI-generated medical answer")
    sources: List[str] = Field(default_factory=list, description="List of source documents")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")

    model_config = ConfigDict(from_attributes=True)


class ChatHistoryItem(BaseModel):
    """
    Single chat interaction from history.
    """
    id: int
    session_id: str
    message: str
    response: str
    sources: List[str] = Field(default_factory=list)
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


 