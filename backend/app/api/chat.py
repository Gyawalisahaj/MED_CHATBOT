"""
Chat API endpoints for medical question-answering.
Handles query processing, history retrieval, and session management.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from sqlalchemy import desc

from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryItem
from app.services.chat_service import process_chat_message
from app.utils.logger import get_logger
from app.db.session import SessionLocal
from app.models.history import ChatHistory

logger = get_logger("chat_api")

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a medical query through the RAG pipeline.
    
    Args:
        request: ChatRequest with message and session_id
    
    Returns:
        ChatResponse with answer and sources
    """
    try:
        logger.info(f"📨 Received query: {request.message[:50]}...")
        response = await process_chat_message(request)
        logger.info(f"✅ Response generated with {len(response.sources)} sources")
        return response
    except Exception as e:
        logger.exception(f"❌ Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=List[ChatHistoryItem])
async def get_chat_history(session_id: str):
    """
    Retrieve chat history for a specific session.
    
    Args:
        session_id: Unique session identifier
    
    Returns:
        List of chat interactions sorted by timestamp
    """
    try:
        db = SessionLocal()
        history = db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id
        ).order_by(desc(ChatHistory.timestamp)).all()
        
        db.close()
        
        return [
            ChatHistoryItem(
                id=h.id,
                session_id=h.session_id,
                message=h.message,
                response=h.response,
                sources=h.sources.split("|") if h.sources else [],
                timestamp=h.timestamp
            )
            for h in history
        ]
    except Exception as e:
        logger.exception(f"History retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear chat history for a specific session.
    
    Args:
        session_id: Unique session identifier
    
    Returns:
        Success message
    """
    try:
        db = SessionLocal()
        db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id
        ).delete()
        db.commit()
        db.close()
        
        logger.info(f"🗑️ Cleared history for session: {session_id}")
        return {"message": f"History cleared for session {session_id}"}
    except Exception as e:
        logger.exception(f"History deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "Medical RAG Chatbot"}

