import json
import logging
from datetime import datetime
from kafka import KafkaProducer
from infrastructure.kafka.consumer_config import get_kafka_broker

logger = logging.getLogger(__name__)

class KafkaMessageProducer:
    def __init__(self):
        self.producer = self._create_producer()

    def _create_producer(self) -> KafkaProducer:
        return KafkaProducer(
            bootstrap_servers=get_kafka_broker(),
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    def send_chat_response(self, memberId: str, message: str, timestamp: str):
        """
        Kafka에 chat_output 토픽으로 응답 메시지를 전송
        """
        message = {
            "memberId": memberId,
            "message": message,
            "timestamp": timestamp
        }

        self.producer.send("chat_output", value=message)
        self.producer.flush()  # 메시지를 즉시 전송
        logger.info(f"[{memberId}] chat_output 전송 완료: {message}")

    def send_done_signal(self, memberId: str):
        message = {
            "type": "done",
            "memberId": memberId,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self.producer.send("chat_output", value=message)
        self.producer.flush()
        logger.info(f"[{memberId}] done 신호 전송 완료")
