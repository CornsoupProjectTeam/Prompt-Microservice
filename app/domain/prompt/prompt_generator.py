# domain/prompt/prompt_generator.py

"""
프롬프트를 기반으로 대화 응답을 생성하는 모듈입니다.
- Ollama LLM을 사용하여 LangChain 기반 응답을 생성합니다.
- 일반 대화와 보조 질문을 생성합니다.
- 응답을 정제하여 자연스럽게 표현합니다.
"""

# from langchain_ollama import OllamaLLM
from openai import OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from domain.prompt.prompt_loader import PromptLoader
import os, logging, random, re
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

class PromptGenerator:
    def __init__(self):
        # 프롬프트 로드
        prompt_data = PromptLoader.load_pers_prompts()
        self.support_prompts = PromptLoader.load_support_prompts()

        self.system_prompt = prompt_data.get("system", "")
        self.examples = prompt_data.get("examples", [])

        # Few-shot 학습 텍스트 구성
        self.few_shot_text = self.system_prompt + "\n\n"
        for example in self.examples:
            self.few_shot_text += f"사용자: {example['input']}\n챗봇: {example['output']}\n\n"

        # # Ollama LLM 설정
        # self.llm = OllamaLLM(
        #     base_url="http://210.110.103.64:11434", 
        #     model="cornsoup_9b" 
        # )
        # self.llm = ChatOpenAI(
        #     model="mistral-medium-latest",
        #     base_url="https://api.mistral.ai/v1",
        #     api_key="J2O2tZ3fYyVq32kBxtnipevdhA9kOprN", 
        #     temperature=0.4,
        # )

        #GPT-4o llm 설정
        self.llm = ChatOpenAI(temperature=0.7,
                              openai_api_key=api_key,
                              model="gpt-4o")

        self.chain = (
            RunnableLambda(self._build_messages)
            .pipe(self.llm)
            .pipe(StrOutputParser())
        )

        logger.warning(f"[PromptGenerator] LLM 객체 생성됨 → {self.llm}")
        logger.warning(f"[PromptGenerator] 호출 주소 → {getattr(self.llm, 'openai_api_base', '알 수 없음')}")


    def _build_messages(self, history):
        messages = [SystemMessage(content=self.few_shot_text)]
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        return messages
    
    def generate_initial_greeting(self) -> str:
        greetings = [
            "안녕하세요! 오늘 하루는 어떠셨나요?",
            "반가워요! 요즘 기분은 어떠세요?",
            "안녕하세요! 최근에 어떤 일이 있었나요?"
        ]
        return random.choice(greetings)

    def generate_reply(self, history: list) -> str:
        try:
            response = self.chain.invoke(history)
            return self.clean_reply(response)
        except Exception as e:
            logger.error(f"LLM 응답 생성 실패: {e}")
            return "죄송합니다. 지금은 응답할 수 없어요."

    def clean_reply(self, text: str) -> str:
        import re
        text = text.strip()
        text = re.sub(r'^["\']?|["\']?$', '', text)
        text = re.sub(r'^(AI|Assistant|챗봇)\s*:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'[\n\r\t]+', ' ', text)
        text = text.replace("<eot_id>", "")
        text = text.replace("\\", "")

        analysis_patterns = [
            r"이건.*(성향|특성).*관련(된|된 것|이야).*",                   # 이건 외향성 성향과 관련된 질문이에요
            r".*(점수|지표)를 (파악|측정)하려고.*",                       # 외향성 점수를 파악하려고 물어봤어요
            r".*(성향|특성) 분석.*질문이에요.*",                          # 신경증 성향 분석 질문이에요
            r"이번 질문은.*(신경증|외향성|성실성|친화성|개방성).*",       # 이번 질문은 신경증에 대한 질문이에요
            r"^이번 질문은 .*",                                          # 이번 질문은 ~~ 시작 멘트들
            r"(당신의 성격을 파악|성향을 확인)하기 위해.*"                # 당신의 성향을 확인하기 위해 물어봤어요
        ]
        for pattern in analysis_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        return text.strip()

    
