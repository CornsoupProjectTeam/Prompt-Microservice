from app.domain.prompt.prompt_generator import PromptGenerator
from langchain_core.messages import HumanMessage, AIMessage

class PersChatService:
    def __init__(self):
        self.history = []
        self.generator = PromptGenerator()
        self.start_message = "안녕하세요! 오늘 기분은 어떠세요?"
        self.history.append(AIMessage(content=self.start_message))

    def generate_response(self, user_input: str) -> str:
        self.history.append(HumanMessage(content=user_input))

        formatted_history = [
            {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
            for msg in self.history
        ]

        reply = self.generator.generate_reply(formatted_history)
        self.history.append(AIMessage(content=reply))
        return reply

if __name__ == "__main__":
    chat_service = PersChatService()
    print(f"챗봇: {chat_service.start_message}")

    for i in range(10):
        user_input = input(f"사용자: ")
        reply = chat_service.generate_response(user_input)
        print(f"챗봇: {reply}")
