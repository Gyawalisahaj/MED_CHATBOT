# Minimal vector store implementation using sentence-transformer embeddings
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.rag.embeddings import get_embeddings_model

class SimpleDocument:
    def __init__(self, page_content: str, metadata: Optional[Dict[str, Any]] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

class SimpleVectorStore:
    def __init__(self):
        self.documents: List[SimpleDocument] = []
        self.embeddings: np.ndarray = np.array([], dtype=np.float32)
        self.embeddings_model = get_embeddings_model()
        self.index_path = os.path.join(settings.VECTOR_STORE_PATH or "./vector_store", "simple_index.json")
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self.load_index()

    def load_index(self):
        """Load index from disk if available."""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "r") as f:
                    data = json.load(f)
                    self.documents = [SimpleDocument(**doc) for doc in data.get("documents", [])]
                embeddings = data.get("embeddings", [])
                self.embeddings = np.array(embeddings, dtype=np.float32)
                if self.embeddings.size == 0:
                    self.embeddings = np.array([], dtype=np.float32)
                elif self.embeddings.ndim == 1:
                    self.embeddings = np.atleast_2d(self.embeddings)
                print(f"Loaded {len(self.documents)} documents from index")
            except Exception as e:
                print(f"Could not load index: {e}")
                self.documents = []
                self.embeddings = np.array([], dtype=np.float32)

    def save_index(self):
        """Save index to disk."""
        data = {
            "documents": [
                {"page_content": doc.page_content, "metadata": doc.metadata}
                for doc in self.documents
            ],
            "embeddings": self.embeddings.tolist() if self.embeddings.size else [],
        }
        with open(self.index_path, "w") as f:
            json.dump(data, f)
        print(f"Saved {len(self.documents)} documents to index")

    def add_documents(self, documents: List[SimpleDocument]):
        """Add documents to the vector store and update the index."""
        if not documents:
            return

        texts = [doc.page_content for doc in documents]
        embeddings = np.array(self.embeddings_model.embed_documents(texts), dtype=np.float32)
        if self.embeddings.size == 0:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])

        self.documents.extend(documents)
        self.save_index()

    def similarity_search(self, query: str, k: int = 5) -> List[SimpleDocument]:
        """Return the top-k most similar documents for the query."""
        if len(self.documents) == 0:
            return []

        query_embedding = np.array(self.embeddings_model.embed_query(query), dtype=np.float32)
        query_norm = np.linalg.norm(query_embedding) + 1e-10
        doc_norms = np.linalg.norm(self.embeddings, axis=1) + 1e-10
        similarities = np.dot(self.embeddings, query_embedding) / (doc_norms * query_norm)
        top_indices = np.argsort(similarities)[-k:][::-1]
        return [self.documents[i] for i in top_indices]


# Module-level singleton — load the 234 MB index only once at startup.
_vector_store_instance: Optional[SimpleVectorStore] = None


def get_vector_store() -> SimpleVectorStore:
    """Return the singleton vector store, initialising it on first call."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = SimpleVectorStore()
    return _vector_store_instance