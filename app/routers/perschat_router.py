from fastapi import APIRouter, Body, Query
from pydantic import BaseModel
from app.services.perschat_service import PersChatService

router = APIRouter(prefix="/chat", tags=["Personality Chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat_with_bot(request: ChatRequest):
    """
    사용자 메시지를 기반으로 챗봇 응답을 생성
    - 사용자별 히스토리를 기억하며 대화
    """
    chat_service = PersChatService()
    response = chat_service.generate_chat_response(request.message)
    return {"response": response}

