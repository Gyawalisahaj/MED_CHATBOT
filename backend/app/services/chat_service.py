"""
Chat Service: Core RAG pipeline with caching, source tracking, and medical guardrails.
"""
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from app.rag.qa_cache import get_cached_answer, save_to_cache
from app.rag.retriever import get_medical_retriever
from app.core.config import settings
from app.core.prompts import MEDICAL_PROMPT
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.logger import get_logger
from app.db.session import SessionLocal
from app.models.history import ChatHistory
from datetime import datetime

logger = get_logger("chat_service")

_rag_chain = None
_retriever = None


def _format_docs(docs: List[Document]) -> str:
    """Format retrieved documents with source attribution."""
    return "\n\n".join(doc.page_content for doc in docs)


def _extract_sources(docs: List[Document]) -> List[str]:
    """Extract unique sources from documents."""
    sources = set()
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "")
        if page:
            sources.add(f"{source} (Page {page})")
        else:
            sources.add(source)
    return sorted(list(sources))


def build_rag_chain():
    """
    Build a LCEL-based RAG chain with proper source tracking.
    Uses HyDE (Hypothetical Document Embeddings) for better retrieval.
    """
    global _rag_chain

    if _rag_chain is None:
        llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE,
        )

        retriever = get_medical_retriever()

        prompt = ChatPromptTemplate.from_messages([
            ("system", MEDICAL_PROMPT),
            ("human", "{question}")
        ])

        # LCEL chain: retrieves docs, formats them, and passes to LLM
        _rag_chain = (
            {
                "context": retriever | _format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

    return _rag_chain


def save_chat_history(session_id: str, message: str, response: str, sources: List[str]):
    """
    Save chat interaction to SQLite database for persistence and analytics.
    """
    try:
        db = SessionLocal()
        chat_record = ChatHistory(
            session_id=session_id,
            message=message,
            response=response,
            sources="|".join(sources),  # Store as pipe-separated string
            timestamp=datetime.utcnow()
        )
        db.add(chat_record)
        db.commit()
        db.close()
        logger.info(f"Chat history saved for session: {session_id}")
    except Exception as e:
        logger.error(f"Failed to save chat history: {str(e)}")


async def process_chat_message(request: ChatRequest) -> ChatResponse:
    """
    Process medical query with:
    1. Query normalization and cache lookup
    2. Vector retrieval with source tracking
    3. LLM-based answer generation
    4. Source attribution
    5. Database persistence
    """
    logger.info(f"Processing query: {request.message[:60]}... (Session: {request.session_id})")

    normalized_question = request.message.strip().lower()

    # 1️⃣ CACHE LOOKUP - Fast retrieval for repeated questions
    cached_answer = get_cached_answer(normalized_question)
    if cached_answer:
        logger.info("✅ Cache hit!")
        response = ChatResponse(
            answer=cached_answer,
            sources=["Cached from Vector DB"],
            session_id=request.session_id
        )
        save_chat_history(request.session_id, request.message, cached_answer, ["Cached"])
        return response

    try:
        chain = build_rag_chain()
        retriever = get_medical_retriever()
        
        # 2️⃣ RETRIEVE CONTEXT - Get relevant medical documents
        retrieved_docs = retriever.invoke(request.message)
        logger.info(f"🔍 Retrieved {len(retrieved_docs)} relevant documents")
        
        # 3️⃣ GENERATE ANSWER - LLM processes context + question
        answer = await chain.ainvoke(request.message)
        
        # 4️⃣ EXTRACT SOURCES - Track citation sources
        sources = _extract_sources(retrieved_docs)
        
        # 5️⃣ CACHE RESULT - Store for future similar queries
        save_to_cache(normalized_question, answer)
        
        # 6️⃣ PERSIST TO DATABASE - Store interaction history
        save_chat_history(request.session_id, request.message, answer, sources)
        
        response = ChatResponse(
            answer=answer,
            sources=sources,
            session_id=request.session_id
        )
        logger.info(f"✅ Query processed successfully with {len(sources)} sources")
        return response

    except Exception as e:
        logger.exception(f"❌ RAG pipeline failure: {str(e)}")
        error_msg = "Sorry, I couldn't process your medical question right now. Please try again."
        save_chat_history(request.session_id, request.message, error_msg, ["System Error"])
        return ChatResponse(
            answer=error_msg,
            sources=["System Error"],
            session_id=request.session_id
        )
