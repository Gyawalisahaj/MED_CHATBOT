"""
PDF Ingestion Script (disabled)
This simplified environment does not support the original LangChain-based
ingestion due to compatibility issues with pydantic/third-party libraries.

Usage:
    python ingest_doc.py

When running in a proper development environment with all dependencies
installed, use the upstream version of this script.
"""

print("🚫 PDF ingestion disabled in minimal mode. No action taken.")
import sys
sys.exit(0)

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Define a basic document class for typing; PyPDFLoader already returns
# objects with `page_content` and `metadata` attributes, so this is only used
# for clarity and for operations below.
class Document:
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}

from backend.app.core.config import settings
from backend.app.utils.logger import get_logger
from backend.app.db.session import SessionLocal
from backend.app.models.history import DocumentMetadata

logger = get_logger("ingest_doc")


class MedicalPDFIngester:
    """
    Handles PDF ingestion, chunking, and FAISS vector store indexing.
    """
    
    def __init__(self):
        self.pdf_folder = settings.PDF_FOLDER
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": settings.EMBEDDING_DEVICE}
        )
        self.vectorstore = None
        self.total_chunks = 0
        self.db = SessionLocal()
        self.vector_store_path = "./vector_store/faiss_index"
    
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
                
                # Add source metadata
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
        
        # Save the index
        if self.vectorstore is not None:
            os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
            self.vectorstore.save_local(self.vector_store_path)
            logger.info(f"💾 FAISS index saved to {self.vector_store_path}")
    
    def save_metadata(self, documents: List[Document]) -> None:
        """
        Save document metadata to SQLite for tracking and analytics.
        """
        logger.info("💾 Saving document metadata to database...")
        
        try:
            # Group documents by source
            sources = {}
            for doc in documents:
                source = doc.metadata.get("source", "unknown")
                if source not in sources:
                    sources[source] = {
                        "pages": 0,
                        "chunks": 0,
                        "path": doc.metadata.get("source_path", "")
                    }
                sources[source]["pages"] = max(
                    sources[source]["pages"],
                    doc.metadata.get("page", 0) + 1
                )
                sources[source]["chunks"] += 1
            
            # Store in database
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
    
    def run(self):
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
            
            # 2. Split documents
            chunks = self.split_documents(documents)
            
            # 3. Ingest to FAISS
            self.ingest_to_faiss(chunks)
            
            # 4. Save metadata
            self.save_metadata(documents)
            
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

