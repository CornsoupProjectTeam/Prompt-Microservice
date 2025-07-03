import sys
import os
sys.path.append(os.path.abspath("."))

from prompt_generator import PromptGenerator

pg = PromptGenerator()
print("LLM 객체:", pg.llm)
print("OpenAI 호출 URL:", getattr(pg.llm, "openai_api_base", "알 수 없음"))
