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


class SearchRequest(BaseModel):
    """
    Advanced medical search with structured fields.
    """
    query: str = Field(..., description="Main search query")
    topic: Optional[str] = Field(None, description="Medical topic (e.g., cardiology)")
    symptoms: Optional[List[str]] = Field(None, description="Symptoms to search for")
    causes: Optional[bool] = Field(False, description="Include causes in search")
    treatment: Optional[bool] = Field(False, description="Include treatment options")
    drugs: Optional[bool] = Field(False, description="Include recommended drugs")
    session_id: str = Field(default="default_session")


class AdvancedSearchResponse(BaseModel):
    """
    Response for advanced medical search.
    """
    answer: str
    topic_info: Optional[str] = None
    symptoms_found: Optional[List[str]] = None
    causes_info: Optional[str] = None
    treatment_options: Optional[List[str]] = None
    recommended_drugs: Optional[List[str]] = None
    sources: List[str] = Field(default_factory=list)
    session_id: Optional[str] = None

    