import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings

print("🔄 Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL,
    model_kwargs={'device': settings.EMBEDDING_DEVICE}
)

print(f"📂 Loading FAISS index from: {settings.VECTOR_STORE_PATH}")
try:
    db = FAISS.load_local(
        settings.VECTOR_STORE_PATH, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    print("✅ Vector store loaded successfully!")
    
    # Test a dummy search
    test_query = "symptoms"
    print(f"🔍 Testing similarity search for query: '{test_query}'...")
    docs = db.similarity_search(test_query, k=2)
    
    print(f"🎉 Found {len(docs)} matching document chunks!")
    for i, doc in enumerate(docs):
        print(f"\n--- Chunk {i+1} Hint ---")
        print(doc.page_content[:150] + "...")
        
except Exception as e:
    print(f"❌ Failed! Vector store error: {e}")