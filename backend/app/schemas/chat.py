from pydantic import BaseModel
from typing import List, Optional, Dict


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
