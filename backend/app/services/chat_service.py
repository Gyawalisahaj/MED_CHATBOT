"""
Chat Service: Core RAG pipeline with caching, source tracking, and medical guardrails.
"""
from typing import List, Dict, Any, Optional

# The original implementation relied heavily on LangChain core and Groq
# libraries which depend on pydantic v1. That conflicts with the project’s
# use of pydantic v2, leading to import errors during application startup.
# To allow the backend to run without those external dependencies we provide a
# minimal dummy implementation below and avoid importing langchain altogether.

# Optional import of ChatGroq – may fail if the underlying langchain packages
# are incompatible.  We only import it lazily when building the chain.
try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None

# Define a very small document-like object for use by the vector store cache.
class SimpleDocument:
    def __init__(self, page_content: str, metadata: Optional[Dict[str, Any]] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

# For type hints we can alias to the simple class
Document = SimpleDocument

from app.rag.qa_cache import get_cached_answer, save_to_cache
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.logger import get_logger
from app.db.session import SessionLocal
from app.models.history import ChatHistory
from datetime import datetime

logger = get_logger("chat_service")


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
        from app.rag.vectorstore import get_vector_store, SimpleDocument
        from app.rag.chain import get_rag_chain

        vectorstore = get_vector_store()

        if len(vectorstore.documents) == 0:
            try:
                from app.rag.loader import load_medical_documents
                loaded_docs = load_medical_documents(settings.PDF_FOLDER)
                if loaded_docs:
                    vectorstore.add_documents([
                        SimpleDocument(page_content=doc.page_content, metadata=doc.metadata)
                        for doc in loaded_docs
                    ])
                    logger.info(f"Loaded and indexed {len(loaded_docs)} documents")
            except Exception as load_error:
                logger.warning(f"Could not auto-load documents: {str(load_error)}")

        docs = vectorstore.similarity_search(request.message, k=settings.TOP_K)
        logger.info(f"Retrieved {len(docs)} relevant documents")

        sources = []
        for doc in docs:
            metadata = getattr(doc, "metadata", {}) or {}
            source = metadata.get("source", "Unknown")
            page = metadata.get("page", "N/A")
            sources.append(f"{source} (Page {page})")

        rag_chain = get_rag_chain()
        answer = rag_chain(request.message, docs)
        logger.info("✅ RAG pipeline completed successfully")

    except Exception as e:
        logger.error(f"RAG pipeline failed: {str(e)}. Falling back to direct answer.")
        try:
            from app.rag.chain import get_rag_chain
            rag_chain = get_rag_chain()
            answer = rag_chain(request.message, [])
            sources = []
            logger.info("✅ Fallback direct model response generated")
        except Exception as inner:
            logger.error(f"Fallback model call failed: {str(inner)}")
            answer = "I apologize, but I'm currently unable to access the medical knowledge base. Please try again later."
            sources = ["Error: Knowledge base unavailable"]

    save_to_cache(normalized_question, answer)
    save_chat_history(request.session_id, request.message, answer, sources)

    response = ChatResponse(
        answer=answer,
        sources=sources,
        session_id=request.session_id
    )
    return response
