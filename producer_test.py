# receive_test.py
import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "chat_output",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id="test-cli-group",
    auto_offset_reset="earliest",
    enable_auto_commit=True
)

print("📡 chat_output 메시지 수신 대기 중...")
for msg in consumer:
    print("📩 받은 메시지:", msg.value)
