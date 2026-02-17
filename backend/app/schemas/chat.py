from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class ChatRequest(BaseModel):
    """
    Schema for incoming chat messages.
    """
    message: str = Field(..., description="The medical query from the user.")
    
    # Critical for SQL History: Links the message to a specific user/session.
    # We use a session_id instead of a manual history list to query the DB.
    session_id: str = Field(
        default="default_session", 
        description="Unique identifier for the chat session to track history in SQL."
    )

class ChatResponse(BaseModel):
    """
    Schema for the chatbot's response.
    """
    answer: str
    sources: List[str] = Field(default_factory=list)
    session_id: Optional[str] = None

    # Pydantic V2 configuration to allow reading data from SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True)