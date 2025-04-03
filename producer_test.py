from kafka import KafkaProducer
import json
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers="210.110.103.135:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8")
)

message = {
    "type": "done",
    "member_id": "u123",
    "timestamp": "2025-03-30T14:36:00.000Z"
}

producer.send("chat_output", key=message["member_id"], value=message)
producer.flush()
print("chat_output 메시지 전송 완료")
