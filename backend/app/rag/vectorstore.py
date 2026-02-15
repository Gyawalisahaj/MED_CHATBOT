from langchain_vdms import VDMS
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

        client = VDMS_Client(
            host=settings.VDMS_HOST,
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
