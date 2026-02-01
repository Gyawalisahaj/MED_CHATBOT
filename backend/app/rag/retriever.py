from app.rag.vectorstore import get_vector_store
from app.core.config import settings


def get_medical_retriever():
    """
    Configures retriever using Maximum Marginal Relevance (MMR)
    to improve diversity and reduce redundancy.
    """
    vectorstore = get_vector_store()

    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": settings.TOP_K,
            "fetch_k": settings.TOP_K * 2
        }
    )
