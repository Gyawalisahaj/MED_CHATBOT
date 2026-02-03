from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from app.rag.qa_cache import get_cached_answer, save_to_cache


from app.core.config import settings
from app.core.prompts import MEDICAL_PROMPT, CONDENSE_PROMPT
from app.rag.retriever import get_medical_retriever
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.logger import get_logger

logger = get_logger("chat_service")


def build_rag_chain():
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model=settings.LLM_MODEL,
        temperature=settings.TEMPERATURE,
    )

    retriever = get_medical_retriever()

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        condense_question_prompt=CONDENSE_PROMPT,
        combine_docs_chain_kwargs={"prompt": MEDICAL_PROMPT},
        return_source_documents=True,
    )


async def process_chat_message(request: ChatRequest) -> ChatResponse:
    logger.info("Received medical query")

    # 1️⃣ Normalize question
    normalized_question = request.message.strip().lower()

    # 2️⃣ Check cache FIRST
    cached_answer = get_cached_answer(normalized_question)
    if cached_answer:
        logger.info("Returning cached response")
        return ChatResponse(
            answer=cached_answer,
            sources=["Cached Response"],
        )

    # 3️⃣ Call RAG + LLM
    chain = build_rag_chain()

    chat_history = [
        (item["user"], item["assistant"])
        for item in request.history
        if "user" in item and "assistant" in item
    ]

    result = chain.invoke({
        "question": request.message,
        "chat_history": chat_history,
    })

    answer = result["answer"]
    sources = list({
        doc.metadata.get("source", "Unknown")
        for doc in result.get("source_documents", [])
    })

    # 4️⃣ Save response to cache
    save_to_cache(normalized_question, answer)

    return ChatResponse(
        answer=answer,
        sources=sources,
    )
