# application/pers_chat_service.py

from domain.prompt.prompt_generator import PromptGenerator

class PersChatService:
    def __init__(self, memberId: str):
        self.memberId = memberId
        self.generator = PromptGenerator()
        self.turn_count = 0

    def generate_response(self, user_input: str):
        self.turn_count += 1

        # 1턴에는 인사 응답
        if self.turn_count == 1:
            greeting = self.generator.generate_initial_greeting()
            return self.generator.clean_reply(greeting), False

        # 2턴부터는 일반 대화 응답
        history = [
            {"role": "user", "content": user_input}
        ]
        reply = self.generator.generate_reply(history)
        return reply, False
