import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.rag.loader import load_medical_documents
from app.rag.splitter import get_text_chunks
from app.rag.vectorstore import get_vector_store

RAW_DOCS_PATH = "data/raw_docs"

def main():
    print("📥 Loading medical documents...")
    documents = load_medical_documents(RAW_DOCS_PATH)

    print(f"✅ Loaded {len(documents)} documents")

    print("✂️ Splitting into chunks...")
    chunks = get_text_chunks(documents)
    print(f"✅ Created {len(chunks)} chunks")

    print("📦 Connecting to vector database...")
    vectorstore = get_vector_store()

    print("🚀 Ingesting chunks into vector DB...")
    vectorstore.add_documents(chunks)

    print("🎉 Ingestion complete! Medical knowledge base is ready.")

if __name__ == "__main__":
    main()
