import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from kafka import KafkaProducer
from infrastructure.kafka.consumer_config import get_kafka_broker

logger = logging.getLogger(__name__)

class KafkaMessageProducer:
    def __init__(self):
        self.producer = self._create_producer()

    def _create_producer(self) -> KafkaProducer:
        return KafkaProducer(
            bootstrap_servers=get_kafka_broker(),
            key_serializer=lambda k: k.encode("utf-8"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    def send_chat_response(self, memberId: str, message: str, timestamp: str):
        msg = {
            "memberId": memberId,
            "message": message,
            "timestamp": timestamp
        }
        self.producer.send("chat_output", key=memberId.encode("utf-8"), value=msg)
        self.producer.flush()
        logger.info(f"[{memberId}] chat_output 전송 완료: {msg}")

    def send_done_signal(self, memberId: str):
        timestamp = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
        done_msg = {
            "type": "done",
            "memberId": memberId,
            "timestamp": timestamp
        }
        self.producer.send("chat_output", key=memberId.encode("utf-8"), value=done_msg)
        self.producer.send("chat_score", key=memberId.encode("utf-8"), value=done_msg)
        self.producer.flush()
        logger.info(f"[{memberId}] done 메시지 전송 완료 (chat_output + chat_score)")

    def send_score_request(self, memberId: str):
        timestamp = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
        request_msg = {
            "type": "request_score",
            "memberId": memberId,
            "timestamp": timestamp
        }
        self.producer.send("chat_score", key=memberId.encode("utf-8"), value=request_msg)
        self.producer.flush()
        logger.info(f"[{memberId}] chat_score 요청 전송 완료 (request_score): {request_msg}")
