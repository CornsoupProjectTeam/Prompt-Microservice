import json
import logging
from kafka import KafkaProducer
from infrastructure.kafka.consumer_config import get_kafka_broker

logger = logging.getLogger(__name__)

class KafkaMessageProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=get_kafka_broker(),
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    def send_chat_response(self, member_id: str, response: str, timestamp: str):
        """Kafka에 chat_output 토픽으로 응답 발행"""
        message = {
            "member_id": member_id,
            "message": response,
            "timestamp": timestamp
        }

        self.producer.send("chat_output", value=message)
        self.producer.flush()
        logger.info(f"[{member_id}] chat_output 전송 완료")
