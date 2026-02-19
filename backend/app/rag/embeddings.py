# Dummy embeddings implementation to avoid external dependency
from app.core.config import settings

class DummyEmbeddings:
    def embed_documents(self, texts):
        # return zero vectors
        return [[0.0] * 768 for _ in texts]
    def embed_query(self, text):
        return [0.0] * 768


def get_embeddings_model():
    """Return a simple placeholder embeddings model."""
    return DummyEmbeddings()
