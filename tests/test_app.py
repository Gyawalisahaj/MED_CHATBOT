import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest
from app.rag.qa_cache import get_cached_answer, save_to_cache
from app.api.chat import get_db
from app.main import app


# 1. Schema Validation Test
def test_schema_validation():
    # Valid schema setup
    req = ChatRequest(message="What are the symptoms of flu?", session_id="session_123")
    assert req.message == "What are the symptoms of flu?"
    assert req.session_id == "session_123"

    # Message too short (min_length=1)
    with pytest.raises(ValidationError):
        ChatRequest(message="", session_id="session_123")


# 2. Cache Functionality Test
def test_cache():
    # Initial state should be None
    assert get_cached_answer("what is water?") is None
    
    # Save to cache
    save_to_cache("what is water?", "Water is H2O.")
    
    # Verify cached answer is returned
    assert get_cached_answer("what is water?") == "Water is H2O."


# 3. Health Endpoint Test
def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/chat/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "Medical RAG Chatbot"}


# 4. DB Session Context Manager Test
def test_db_session():
    with get_db() as db:
        assert isinstance(db, Session)
        # Verify db is active/open
        assert db.is_active
