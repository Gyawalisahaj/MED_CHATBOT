import os
import sys
from contextlib import contextmanager

# Ensure backend directory is in sys.path so 'app' imports resolve on CI/CD
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# 🎯 FIXED: Stripped the 'backend.' prefix so paths match app/main.py internal architecture
# 🎯 FIX: Remove "backend." from the front of these imports
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
# 4. DB Session Context Manager Test
def test_db_session():
    # 🎯 FIXED: Removed the double-wrapping since get_db is already a context manager!
    with get_db() as db:
        assert isinstance(db, Session)
        # Verify db is active/open
        assert db.is_active