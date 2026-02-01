from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings


def get_embeddings_model():
    """
    Returns an embedding model optimized for CPU workloads.
    Suitable for Intel architectures.
    """
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}  # can be changed to 'ipex'
    )
