# Simple vector store implementation without LangChain dependencies
import os
import json
import numpy as np
from typing import List, Dict, Any
from app.core.config import settings
from app.rag.embeddings import get_embeddings_model

class SimpleDocument:
    def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

class SimpleVectorStore:
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.embeddings_model = get_embeddings_model()
        self.index_path = os.path.join(settings.VECTOR_STORE_PATH or "./vector_store", "simple_index.json")
        self.load_index()

    def load_index(self):
        """Load existing index if available"""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r') as f:
                    data = json.load(f)
                    self.documents = [SimpleDocument(**doc) for doc in data.get('documents', [])]
                    self.embeddings = np.array(data.get('embeddings', []))
                print(f"Loaded {len(self.documents)} documents from index")
            except Exception as e:
                print(f"Could not load index: {e}")
                self.documents = []
                self.embeddings = np.array([])

    def save_index(self):
        """Save current index to disk"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        data = {
            'documents': [{'page_content': doc.page_content, 'metadata': doc.metadata} for doc in self.documents],
            'embeddings': self.embeddings.tolist() if len(self.embeddings) > 0 else []
        }
        with open(self.index_path, 'w') as f:
            json.dump(data, f)
        print(f"Saved {len(self.documents)} documents to index")

    def add_documents(self, documents: List[SimpleDocument]):
        """Add documents to the vector store"""
        for doc in documents:
            self.documents.append(doc)
            # Generate embedding
            embedding = self.embeddings_model.embed_query(doc.page_content)
            self.embeddings = np.vstack([self.embeddings, embedding]) if len(self.embeddings) > 0 else np.array([embedding])
        self.save_index()

    def similarity_search(self, query: str, k: int = 5) -> List[SimpleDocument]:
        """Find most similar documents"""
        if len(self.documents) == 0:
            return []

        # Generate query embedding
        query_embedding = np.array(self.embeddings_model.embed_query(query))

        # Calculate cosine similarities
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )

        # Get top k indices
        top_indices = np.argsort(similarities)[-k:][::-1]

        # Return top documents
        return [self.documents[i] for i in top_indices]

_vectorstore = None

def get_vector_store():
    """Get singleton vector store instance"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = SimpleVectorStore()
    return _vectorstore

def save_vector_store():
    """Save the vector store"""
    global _vectorstore
    if _vectorstore:
        _vectorstore.save_index()