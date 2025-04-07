# send_test.py
import json
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

test_message = {
    "type": "chat",
    "memberId": "test123",
    "message": "안녕 챗봇!",
    "timestamp": "2025-04-07T12:00:00Z"
}

producer.send("chat_input", value=test_message)
producer.flush()

print("✅ 테스트 메시지 전송 완료")
