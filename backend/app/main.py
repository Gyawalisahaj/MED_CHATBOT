from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.core.config import settings
from app.utils.logger import get_logger

# --- FIX 1: Import Database requirements ---
from app.db.session import engine, Base 
from app.models.history import ChatHistory  # Must import to register tables

logger = get_logger("main")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Medical RAG Chatbot powered by Intel VDMS"
    )

    # --- FIX 2: Move Table Creation inside Startup ---
    @app.on_event("startup")
    def on_startup():
        logger.info("Verifying SQL Database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database is ready.")

    # CORS configuration remains exactly as you had it
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
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

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI Server...")
    # Using app instance directly for reliability
    uvicorn.run(app, host="0.0.0.0", port=8000)