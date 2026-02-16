from langchain_community.vectorstores.vdms import VDMS, VDMS_Client # Added VDMS_Client
from app.rag.embeddings import get_embeddings_model
from app.core.config import settings

_vectorstore = None

def get_vector_store() -> VDMS:
    """
    Returns a singleton Intel VDMS vector store instance.
    """
    global _vectorstore

    if _vectorstore is None:
        embeddings = get_embeddings_model()

        # Hardcoding '127.0.0.1' here ensures we bypass any localhost/IPv6 issues
        client = VDMS_Client(
            host="127.0.0.1", 
            port=settings.VDMS_PORT
        )

        _vectorstore = VDMS(
            client=client,
            collection_name=settings.VDMS_COLLECTION,
            embedding=embeddings,
            engine="FaissFlat",
            distance_strategy="L2"
        )

    return _vectorstore