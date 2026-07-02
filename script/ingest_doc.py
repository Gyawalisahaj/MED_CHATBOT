import os
import sys
from pathlib import Path
from typing import List

# 1. FIX: Add the 'backend' directory to sys.path so Python can find 'app'
root_path = Path(__file__).resolve().parent.parent
backend_path = root_path / "backend"

if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# 2. FIX: Import directly from 'app' (matching your internal backend files)
from app.core.config import settings
from app.utils.logger import get_logger
from app.db.session import SessionLocal
from app.models.history import DocumentMetadata

# 3. Third-party LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

logger = get_logger("ingest_doc")

class MedicalPDFIngester:
    """
    Handles PDF ingestion, chunking, and FAISS vector store indexing.
    """
    
    def __init__(self):
        # Fallback to relative paths if settings variables are unassigned
        self.pdf_folder = settings.PDF_FOLDER or "./Document"
        self.chunk_size = getattr(settings, "CHUNK_SIZE", 500)
        self.chunk_overlap = getattr(settings, "CHUNK_OVERLAP", 50)
        
        embedding_model = getattr(settings, "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        embedding_device = getattr(settings, "EMBEDDING_DEVICE", "cpu")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": embedding_device}
        )
        self.vectorstore = None
        self.db = SessionLocal()
        
        # FIX: Point directly to backend/vector_store as indicated in your folder tree
        self.vector_store_path = str(root_path / "backend" / "vector_store" / "faiss_index")
    
    def load_pdfs(self) -> List[Document]:
        """
        Load all PDF files from the configured folder.
        """
        logger.info(f"📂 Loading PDFs from: {self.pdf_folder}")
        
        documents = []
        pdf_files = list(Path(self.pdf_folder).glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"⚠️  No PDF files found in {self.pdf_folder}")
            return documents
        
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        for pdf_path in pdf_files:
            try:
                logger.info(f"📖 Loading: {pdf_path.name}...")
                loader = PyPDFLoader(str(pdf_path))
                docs = loader.load()
                
                # Add source metadata details cleanly
                for doc in docs:
                    doc.metadata["source"] = pdf_path.name
                    doc.metadata["source_path"] = str(pdf_path)
                
                documents.extend(docs)
                logger.info(f"✅ {pdf_path.name}: {len(docs)} pages loaded")
                
            except Exception as e:
                logger.error(f"❌ Failed to load {pdf_path.name}: {str(e)}")
                continue
        
        logger.info(f"📊 Total pages loaded: {len(documents)}")
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into overlapping chunks optimized for medical text.
        """
        logger.info(f"✂️  Splitting {len(documents)} documents into chunks...")
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        chunks = splitter.split_documents(documents)
        logger.info(f"📦 Created {len(chunks)} text chunks")
        
        return chunks
    
    def ingest_to_faiss(self, chunks: List[Document]) -> None:
        """
        Ingest chunks into FAISS vector store in batches.
        """
        logger.info(f"🚀 Starting FAISS ingestion...")
        
        batch_size = 100
        self.vectorstore = None
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(chunks) + batch_size - 1) // batch_size
            
            try:
                if self.vectorstore is None:
                    # Create new vector store with first batch
                    self.vectorstore = FAISS.from_documents(
                        batch,
                        self.embeddings
                    )
                    logger.info(f"✅ FAISS vector store created")
                else:
                    # Add to existing vector store
                    self.vectorstore.add_documents(batch)
                
                processed = min(i + batch_size, len(chunks))
                logger.info(f"📦 Batch {batch_num}/{total_batches}: Processed {processed}/{len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"❌ Batch {batch_num} failed: {str(e)}")
                raise
        
        logger.info(f"✨ All {len(chunks)} chunks successfully indexed!")
        
        # Save the index locally to disk
        if self.vectorstore is not None:
            os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
            self.vectorstore.save_local(self.vector_store_path)
            logger.info(f"💾 FAISS index saved to {self.vector_store_path}")
    
    def save_metadata(self, documents: List[Document], chunks: List[Document]) -> None:
        """
        Save document metadata to SQLite for tracking and analytics.
        """
        logger.info("💾 Saving document metadata to database...")
        
        try:
            sources = {}
            
            # Count total pages from raw documents
            for doc in documents:
                source = doc.metadata.get("source", "unknown")
                if source not in sources:
                    sources[source] = {"pages": 0, "chunks": 0, "path": doc.metadata.get("source_path", "")}
                # page is 0-indexed from PyPDFLoader, add 1 for max page number count
                sources[source]["pages"] = max(sources[source]["pages"], doc.metadata.get("page", 0) + 1)
            
            # Count total chunks generated from splitting
            for chunk in chunks:
                source = chunk.metadata.get("source", "unknown")
                if source in sources:
                    sources[source]["chunks"] += 1
            
            # Sync metadata profiles to database
            for filename, info in sources.items():
                existing = self.db.query(DocumentMetadata).filter(
                    DocumentMetadata.filename == filename
                ).first()
                
                if existing:
                    existing.total_pages = info["pages"]
                    existing.total_chunks = info["chunks"]
                else:
                    doc_meta = DocumentMetadata(
                        filename=filename,
                        file_path=info["path"],
                        total_pages=info["pages"],
                        total_chunks=info["chunks"]
                    )
                    self.db.add(doc_meta)
            
            self.db.commit()
            logger.info(f"✅ Metadata saved for {len(sources)} documents")
            
        except Exception as e:
            logger.error(f"❌ Failed to save metadata: {str(e)}")
            self.db.rollback()
        finally:
            self.db.close()
    
    def run(self) -> bool:
        """
        Execute the complete ingestion pipeline.
        """
        logger.info("=" * 60)
        logger.info("🏥 MEDICAL PDF INGESTION PIPELINE")
        logger.info("=" * 60)
        
        try:
            # 1. Load PDFs
            documents = self.load_pdfs()
            if not documents:
                logger.error("No documents loaded. Exiting.")
                return False
            
            # 2. Split documents into chunks
            chunks = self.split_documents(documents)
            if not chunks:
                logger.error("Splitting resulted in 0 text chunks. Exiting.")
                return False
            
            # 3. Ingest chunks into FAISS vector database
            self.ingest_to_faiss(chunks)
            
            # 4. Save metadata records to SQLite
            self.save_metadata(documents, chunks)
            
            logger.info("=" * 60)
            logger.info("✨ INGESTION COMPLETE!")
            logger.info(f"   📄 Documents: {len(set(d.metadata.get('source') for d in documents))}")
            logger.info(f"   📖 Total Pages: {len(documents)}")
            logger.info(f"   📦 Total Chunks: {len(chunks)}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {str(e)}")
            return False

def main():
    """Main entry point."""
    ingester = MedicalPDFIngester()
    success = ingester.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()