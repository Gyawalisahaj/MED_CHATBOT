from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.rag.qa_cache import get_cached_answer, save_to_cache
from app.rag.retriever import get_medical_retriever
from app.core.config import settings
from app.core.prompts import MEDICAL_PROMPT
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.logger import get_logger

logger = get_logger("chat_service")

_rag_chain = None


def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain():
    """
    Build a modern LCEL-based RAG chain (no deprecated APIs).
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


async def process_chat_message(request: ChatRequest) -> ChatResponse:
    """
    Process medical query with cache + RAG + Groq.
    """
    logger.info(f"Processing query: {request.message[:60]}")

    normalized_question = request.message.strip().lower()

    # 1️⃣ Cache lookup
    cached_answer = get_cached_answer(normalized_question)
    if cached_answer:
        logger.info("Cache hit")
        return ChatResponse(
            answer=cached_answer,
            sources=["Cached Knowledge Base"],
        )

    try:
        chain = build_rag_chain()

        # 2️⃣ Execute RAG
        answer = await chain.ainvoke(request.message)

        # 3️⃣ Cache result
        save_to_cache(normalized_question, answer)

        return ChatResponse(
            answer=answer,
            sources=["Medical Knowledge Base"],
        )

    except Exception as e:
        logger.exception("RAG pipeline failure")
        return ChatResponse(
            answer="Sorry, I couldn't process your medical question right now.",
            sources=["System Error"],
        )