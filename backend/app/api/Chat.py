from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_chat_message

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        return await process_chat_message(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
