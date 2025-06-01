# application/auxiliary_prompt_service.py

from domain.prompt.prompt_loader import PromptLoader
import random

class AuxiliaryPromptService:
    def __init__(self, memberId: str):
        self.memberId = memberId
        self.support_prompts = PromptLoader.load_support_prompts()
        self.direct_prompts = PromptLoader.load_direct_prompts()

    def generate_support_question(self, trait: str) -> str:
        """
        자연스러운 보완 질문
        """
        prompts = self.support_prompts.get(trait, [])
        return random.choice(prompts) if prompts else f"{trait}에 대해 어떻게 생각하세요?"

    def generate_direct_question(self, trait: str) -> str:
        """
        설문형 직접 질문
        """
        return self.direct_prompts.get(trait, f"{trait} 성향에 대해 직접 말씀해주세요.")
