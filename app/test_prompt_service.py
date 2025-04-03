from application.prompt_service import PersChatService

service = PersChatService()

print("챗봇과 대화를 시작해보세요! (종료하려면 'exit' 입력)")

# 👉 첫 메시지 출력
first_message = service.history[0].content
print(f"🤖 챗봇: {first_message}")

while True:
    user_input = input("👤 사용자: ")
    if user_input.lower() == "exit":
        break
    response = service.generate_response(user_input)
    print(f"🤖 챗봇: {response}")
