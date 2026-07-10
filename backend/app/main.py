from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.core.config import settings
from app.utils.logger import get_logger
from app.db.session import engine, Base 
from app.models.history import ChatHistory 

from app.api.auth import router as auth_router     
from app.db.postgres_session import pg_engine, AuthBase  
from app.models.users import User                    


# app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])  

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Verifying SQL Database tables...")
    Base.metadata.create_all(bind=engine)
    # inside lifespan(), after Base.metadata.create_all(bind=engine):
    try:
        AuthBase.metadata.create_all(bind=pg_engine)
        logger.info("PostgreSQL auth tables ready.")
    except Exception as pg_err:
        logger.warning(f"PostgreSQL not available: {pg_err}")


    logger.info("Database is ready.")
    
    logger.info("Pre-loading vector store index (this may take a moment)...")
    try:
        from app.rag.vectorstore import get_vector_store
        vs = get_vector_store()
        logger.info(f"Vector store ready — {len(vs.documents)} documents loaded.")
        
        # Issue 7: On-demand indexing moved to startup to avoid blocking live requests
        if len(vs.documents) == 0:
            logger.info("Vector store index is empty. Running initial PDF ingestion...")
            try:
                from app.rag.loader import load_medical_documents
                from app.rag.vectorstore import SimpleDocument
                loaded_docs = load_medical_documents(settings.PDF_FOLDER)
                if loaded_docs:
                    vs.add_documents([
                        SimpleDocument(page_content=doc.page_content, metadata=doc.metadata)
                        for doc in loaded_docs
                    ])
                    logger.info(f"Successfully loaded and indexed {len(loaded_docs)} documents on startup.")
                else:
                    logger.warning("No PDF documents found to index during startup.")
            except Exception as load_error:
                logger.error(f"Failed to auto-load documents on startup: {str(load_error)}")
    except Exception as e:
        logger.warning(f"Vector store pre-load failed: {e}")
    
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Medical RAG Chatbot powered by Intel VDMS",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include the chat router
    app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])

    # Feature: Your specific root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "project": settings.PROJECT_NAME,
            "status": "online",
            "environment": settings.ENVIRONMENT,
            "message": "Medical Chatbot Online"
        }

    return app

# Initialize the application instance

app = create_app()

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])  

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI Server...")
    # Using app instance directly for reliability
    uvicorn.run(app, host="0.0.0.0", port=8000)