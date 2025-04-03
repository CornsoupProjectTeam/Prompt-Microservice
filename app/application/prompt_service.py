import logging
from langchain_core.messages import HumanMessage, AIMessage
from domain.prompt_generator import PromptGenerator

logger = logging.getLogger(__name__)

class PersChatService:
    def __init__(self):
        self.history = []
        self.history.append(AIMessage(content="안녕하세요! 오늘 기분은 어떠세요?"))
        self.generator = PromptGenerator()

    def generate_response(self, user_input: str) -> str:
        try:
            self.history.append(HumanMessage(content=user_input))

            # LangChain에 맞게 메시지 포맷 구성
            formatted_history = [
                {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
                for msg in self.history
            ]

            reply = self.generator.generate_reply(formatted_history)
            self.history.append(AIMessage(content=reply))
            return reply
        except Exception as e:
            logger.error(f"응답 생성 실패: {e}")
            return "챗봇 응답 생성 중 오류가 발생했어요."
