from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "chat_output",
    bootstrap_servers="210.110.103.135:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="test-output-group"
)

print("chat_output 수신 대기 중... (Ctrl+C로 종료)")

for msg in consumer:
    print("받은 메시지:", msg.value)
