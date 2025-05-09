#application/prompt_service.py
import re
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

    def clean_reply(self, text: str) -> str:
            """
            불필요한 접두어, 이스케이프 문자, 따옴표 등을 제거하여 정제된 답변 반환
            """
            text = text.strip()  # 양 끝 공백 제거
            text = re.sub(r'^["\']?|["\']?$', '', text)  # 양쪽 따옴표 제거
            text = re.sub(r'^(AI|Assistant|챗봇)\s*:\s*', '', text, flags=re.IGNORECASE)  # AI: 제거
            text = re.sub(r'[\n\r\t]+', ' ', text)
            text = text.replace("\\", "")

            # ✅ 이모지 제거
            emoji_pattern = re.compile(
                "[" "\U0001F600-\U0001F64F"
                "\U0001F300-\U0001F5FF"
                "\U0001F680-\U0001F6FF"
                "\U0001F1E0-\U0001F1FF"
                "\U00002700-\U000027BF"
                "\U000024C2-\U0001F251"
                "]+", flags=re.UNICODE
            )
            text = emoji_pattern.sub(r'', text)
            return text.strip()


    def generate_response(self, user_input: str) -> str:
        logger.info(f"[{self.turn_count}] 사용자 입력 수신됨: {user_input}")
        """
        사용자 입력을 받아 응답을 생성하고,
        종료 조건이 충족되면 done 상태를 함께 반환합니다.

        Returns:
            - reply: 챗봇 응답
            - is_done: 대화 종료 여부 (True면 done 발행 필요)
        """
        try:
            self.turn_count += 1
            logger.info(f"[{self.turn_count}] 사용자 입력 수신됨: {user_input}")
            self.history.append(HumanMessage(content=user_input))

            # 메시지 포맷 구성
            formatted_history = [
                {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
                for msg in self.history
            ]

            # 마지막 응답 처리
            if self.turn_count >= 3:
                final_reply = "아쉽지만 대화는 여기까지에요.."
                self.history.append(AIMessage(content=final_reply))
                return final_reply, True  # 종료 상태

            # 일반 응답 처리
            raw_reply = self.generator.generate_reply(formatted_history)
            reply = self.clean_reply(raw_reply)
            self.history.append(AIMessage(content=reply))
            return reply, False

        except Exception as e:
            logger.error(f"응답 생성 실패: {e}")
            return "챗봇 응답 생성 중 오류가 발생했어요.", False
