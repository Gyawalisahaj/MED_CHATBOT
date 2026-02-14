import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document


SUPPORTED_EXTENSIONS = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
}


def load_medical_documents(directory_path: str) -> List[Document]:
    """
    Load all supported medical documents from a directory.
    Supported formats: PDF, TXT
    """
    documents: List[Document] = []

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in SUPPORTED_EXTENSIONS:
            continue

        loader_class = SUPPORTED_EXTENSIONS[ext]
        loader = loader_class(file_path)

        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = filename  # critical for citations

        documents.extend(docs)

    return documents
