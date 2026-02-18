"""
SQLAlchemy ORM models for storing chat history and metadata.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.session import Base


class ChatHistory(Base):
    """
    Stores chat interactions for persistence and analytics.
    Tracks questions, responses, and citation sources.
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)  # Links messages to a specific user/chat session
    message = Column(Text)                        # What the user asked
    response = Column(Text)                       # What the AI answered
    sources = Column(String(1000), nullable=True) # Citation sources (pipe-separated)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, session_id={self.session_id}, timestamp={self.timestamp})>"


class DocumentMetadata(Base):
    """
    Stores metadata about ingested PDF documents.
    Useful for analytics and source tracking.
    """
    __tablename__ = "document_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), unique=True, index=True)
    file_path = Column(String(512))
    total_pages = Column(Integer)
    total_chunks = Column(Integer)
    ingest_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DocumentMetadata(filename={self.filename}, pages={self.total_pages})>"
