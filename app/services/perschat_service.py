import os
import json
import logging
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from langchain_core.messages import HumanMessage, AIMessage

from app.services.chathistory_service import ChatHistoryService

# 환경 변수 로드 및 로깅 설정
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersChatService:
    def __init__(self):
        # 프롬프트 파일 로드
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../resources"))
        prompt_path = os.path.join(base_path, "pers_prompt.json")

        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt_data = json.load(file)
        self.system_prompt = prompt_data["system"]
        self.examples = prompt_data.get("examples", [])

        # 초기 프롬프트 텍스트 구성
        self.few_shot_text = self.system_prompt + "\n\n"
        for example in self.examples:
            self.few_shot_text += f"사용자: {example['input']}\n챗봇: {example['output']}\n\n"

        # Ollama 모델 설정
        self.llm = OllamaLLM(
            base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "cornsoup_9b")
        )

        # 메모리 기반 히스토리
        self.history: list = []

        # 챗봇 첫 인사
        self.history.append(AIMessage(content="안녕하세요! 오늘 기분은 어떠세요?"))

        # 대화 기록 저장 서비스 초기화
        self.chat_saver = ChatHistoryService()

        # 체인 구성
        self.chain = RunnableSequence([
            lambda input: self._build_messages(input["user_input"]),
            self.llm,
            StrOutputParser()
        ])

    def _build_messages(self, user_input: str):
        """LangChain 메시지 형식으로 시스템 + 히스토리 + 사용자 입력 구성"""
        messages = [{"role": "system", "content": self.few_shot_text}]
        for msg in self.history:
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({"role": "assistant", "content": msg.content})
        messages.append({"role": "user", "content": user_input})
        return messages

    def generate_chat_response(self, user_input: str) -> str:
        """사용자 입력에 대한 챗봇 응답 생성 및 기록 저장"""
        try:
            response = self.chain.invoke({"user_input": user_input})
            user_msg = HumanMessage(content=user_input)
            ai_msg = AIMessage(content=response)

            # 메모리 히스토리 저장
            self.history.append(user_msg)
            self.history.append(ai_msg)

            # 파일로 기록 저장
            self.chat_saver.save(user_input, response)

            return response
        except Exception as e:
            logger.error(f"챗봇 응답 생성 중 오류: {e}")
            return "챗봇 응답 생성 중 오류가 발생했어요."
