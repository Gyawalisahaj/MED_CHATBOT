from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("main")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Medical RAG Chatbot powered by Intel VDMS"
    )

    # CORS configuration is required so the Streamlit frontend can communicate with the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For production, replace with specific frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include the chat router
    app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "project": settings.PROJECT_NAME,
            "status": "online",
            "environment": settings.ENVIRONMENT
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)