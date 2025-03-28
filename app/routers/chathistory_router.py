from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chathistory_service import ChatHistoryService

router = APIRouter(prefix="/history", tags=["Chat History"])
history_service = ChatHistoryService()

class ChatRequest(BaseModel):
    user_input: str
    bot_response: str

@router.post("/")
def save_chat(request: ChatRequest):
    history_service.save_chat(request.user_input, request.bot_response)
    return {"message": "대화가 저장되었습니다."}
