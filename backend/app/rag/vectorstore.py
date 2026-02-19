# vectorstore stub - external dependencies removed
from app.core.config import settings

_vectorstore = None
VECTOR_STORE_PATH = "./vector_store"

def get_vector_store() -> FAISS:
    """
    Returns a singleton FAISS vector store instance.
    """
    global _vectorstore

    if _vectorstore is None:
        embeddings = get_embeddings_model()

        # Create vector store directory if needed
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

        index_path = os.path.join(VECTOR_STORE_PATH, "faiss_index")

        # Try to load existing index
        if os.path.exists(index_path):
            try:
                _vectorstore = FAISS.load_local(
                    index_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"Loaded existing FAISS index from {index_path}")
            except Exception as e:
                print(f"Could not load existing index: {e}. Creating new one.")
                _vectorstore = FAISS.from_documents([], embeddings)
        else:
            # Create new empty index
            _vectorstore = FAISS.from_documents([], embeddings)
            print(f"Created new FAISS index at {index_path}")

    return _vectorstore


def save_vector_store() -> None:
    """
    Saves the current vector store to disk.
    """
    global _vectorstore
    if _vectorstore is not None:
        index_path = os.path.join(VECTOR_STORE_PATH, "faiss_index")
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
        _vectorstore.save_local(index_path)
        print(f"Saved FAISS index to {index_path}")