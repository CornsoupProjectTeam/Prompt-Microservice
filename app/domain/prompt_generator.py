# domain/prompt_generator.py
import os, json, logging
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()
logger = logging.getLogger(__name__)

class PromptGenerator:
    def __init__(self):
        # 프롬프트 로드
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../domain/prompt"))
        prompt_path = os.path.join(base_path, "pers_prompt.json")

        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt_data = json.load(file)

        self.system_prompt = prompt_data["system"]
        self.examples = prompt_data.get("examples", [])

        self.few_shot_text = self.system_prompt + "\n\n"
        for example in self.examples:
            self.few_shot_text += f"사용자: {example['input']}\n챗봇: {example['output']}\n\n"

        self.llm = OllamaLLM(
            base_url="http://210.110.103.64:11434",
            model="cornsoup_9b"
        )
        self.chain = (
            RunnableLambda(self._build_messages)
            .pipe(self.llm)
            .pipe(StrOutputParser())
        )
            

    def _build_messages(self, history):
        messages = [{"role": "system", "content": self.few_shot_text}]
        messages.extend(history)
        return messages

    def generate_reply(self, history: list) -> str:
        try:
            return self.chain.invoke({"messages": history})
        except Exception as e:
            logger.error(f"LLM 응답 생성 실패: {e}")
            return "죄송합니다. 지금은 응답할 수 없어요."
