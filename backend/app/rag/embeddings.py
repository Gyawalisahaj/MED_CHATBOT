# Sentence Transformers embeddings implementation
from app.core.config import settings

try:
    from sentence_transformers import SentenceTransformer
    import torch

    class SentenceTransformerEmbeddings:
        def __init__(self, model_name: str = None):
            device = 'cuda' if torch.cuda.is_available() and settings.EMBEDDING_DEVICE == 'cuda' else 'cpu'
            self.model = SentenceTransformer(model_name or settings.EMBEDDING_MODEL, device=device)

        def embed_documents(self, texts):
            return self.model.encode(texts, convert_to_numpy=True).tolist()

        def embed_query(self, text):
            return self.model.encode([text], convert_to_numpy=True)[0].tolist()

    def get_embeddings_model():
        """Return sentence transformer embeddings model."""
        try:
            return SentenceTransformerEmbeddings()
        except Exception as e:
            print(f"Could not load sentence transformers: {e}. Using dummy embeddings.")
            return DummyEmbeddings()

except ImportError:
    print("sentence-transformers not available. Using dummy embeddings.")

    class DummyEmbeddings:
        def embed_documents(self, texts):
            # return zero vectors
            return [[0.0] * 768 for _ in texts]
        def embed_query(self, text):
            return [0.0] * 768

    def get_embeddings_model():
        """Return a simple placeholder embeddings model."""
        return DummyEmbeddings()
