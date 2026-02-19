from typing import List
# Simple document type for splitting operations (only attributes needed are
# `page_content` and `metadata`).
class Document:
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}

# Dummy splitter that returns documents unchanged.  The original
# implementation used RecursiveCharacterTextSplitter from langchain_text_splitters
# which pulled in incompatible dependencies.


def split_medical_documents(documents: List[Document]) -> List[Document]:
    """
    Dummy splitter; returns documents unchanged.
    """
    return documents

