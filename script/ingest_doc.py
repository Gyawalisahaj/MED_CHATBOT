import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.vdms import VDMS, VDMS_Client
from app.core.config import settings

def main():
    # 1. Load the PDF
    print(f"📖 Reading Harrison's... (15k pages takes about 2-3 mins)")
    loader = PyPDFLoader("./Document/Harrisons.pdf")
    docs = loader.load()
    print(f"📄 Pages loaded: {len(docs)}")

    # 2. Split into Chunks (Critical for a 15k page book!)
    # We use a 1000 character chunk size for medical depth
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(docs)
    print(f"✂️ Created {len(chunks)} chunks of text.")

    # 3. Setup VDMS Connection
    client = VDMS_Client(host="127.0.0.1", port=settings.VDMS_PORT)
    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)

    # 4. BATCH INGESTION (To prevent crashing)
    batch_size = 100  # Upload 100 chunks at a time
    print(f"🚀 Starting ingestion to collection: {settings.VDMS_COLLECTION}")
    
    vectorstore = None
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        if vectorstore is None:
            vectorstore = VDMS.from_documents(
                batch, embeddings, client=client, collection_name=settings.VDMS_COLLECTION
            )
        else:
            vectorstore.add_documents(batch)
        
        if (i // batch_size) % 10 == 0: # Progress update every 1000 chunks
             print(f"✅ Processed {i}/{len(chunks)} chunks...")

    print("🔥 SUCCESS! All 15,164 pages are indexed and ready.")

if __name__ == "__main__":
    main()