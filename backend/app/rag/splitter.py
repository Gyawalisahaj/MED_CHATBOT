from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def split_medical_documents(documents: List[Document]) -> List[Document]:
    """
    Split medical documents into overlapping chunks
    optimized for clinical and educational text.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    return splitter.split_documents(documents)
