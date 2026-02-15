from langchain_core.documents import Document
from app.rag.vectorstore import get_vector_store
from app.core.config import settings


CACHE_SCORE_THRESHOLD = 0.95  # High similarity = same question


def get_cached_answer(question: str):
    """
    Check if a very similar question was already answered.
    """
    vectorstore = get_vector_store()
    results = vectorstore.similarity_search_with_score(
        question, k=1
    )

    if not results:
        return None

    doc, score = results[0]

    # Lower score = more similar (L2 distance)
    if score <= CACHE_SCORE_THRESHOLD:
        return doc.metadata.get("answer")

    return None


def save_to_cache(question: str, answer: str):
    """
    Store question-answer pair in vector DB.
    """
    doc = Document(
        page_content=question,
        metadata={"answer": answer},
    )

    vectorstore = get_vector_store()
    vectorstore.add_documents([doc])
