import logging
from langchain_core.messages import HumanMessage, AIMessage
from domain.prompt_generator import PromptGenerator

logger = logging.getLogger(__name__)

class PersChatService:
    def __init__(self):
        self.history = []
        self.turn_count = 0
        self.generator = PromptGenerator()

        self.start_message = "안녕하세요! 오늘 기분은 어떠세요?"
        self.history.append(AIMessage(content=self.start_message))

    def generate_response(self, user_input: str) -> tuple[str, bool]:
        """
        사용자 입력을 받아 응답을 생성하고,
        종료 조건이 충족되면 done 상태를 함께 반환합니다.

        Returns:
            - reply: 챗봇 응답
            - is_done: 대화 종료 여부 (True면 done 발행 필요)
        """
        try:
            self.turn_count += 1
            self.history.append(HumanMessage(content=user_input))

            # 메시지 포맷 구성
            formatted_history = [
                {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
                for msg in self.history
            ]

            # 마지막 응답 처리
            if self.turn_count >= 5:
                final_reply = "아쉽지만 대화는 여기까지에요.."
                self.history.append(AIMessage(content=final_reply))
                return final_reply, True  # 종료 상태

            # 일반 응답 처리
            reply = self.generator.generate_reply(formatted_history)
            self.history.append(AIMessage(content=reply))
            return reply, False

        except Exception as e:
            logger.error(f"응답 생성 실패: {e}")
            return "챗봇 응답 생성 중 오류가 발생했어요.", False
