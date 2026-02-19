# Retriever stub: the full implementation relied on a FAISS vector store
# which transitively imported langchain_core and caused compatibility
# conflicts.  Here we return a dummy object with the minimal interface
# used by the rest of the application.

class DummyRetriever:
    def invoke(self, query: str):
        return []

    def get_relevant_documents(self, query: str):
        return []


def get_medical_retriever():
    """Return a dummy retriever that yields no documents."""
    return DummyRetriever()
