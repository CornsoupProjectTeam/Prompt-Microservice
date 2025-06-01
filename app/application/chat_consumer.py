import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from infrastructure.kafka import create_consumer, KafkaMessageProducer
from application.session_manager import SessionManager

logger = logging.getLogger(__name__)

class ChatConsumer:
    def __init__(self):
        self.consumer = create_consumer("chat_input")
        self.producer = KafkaMessageProducer()
        self.session_manager = SessionManager()

    def start(self):
        logger.info("Kafka Consumer 시작 (chat_input 구독 중)")
        for message in self.consumer:
            try:
                data = json.loads(message.value)
                msg_type = data.get("type")
                member_id = data.get("memberId")

                if not member_id:
                    logger.warning("memberId가 누락된 메시지")
                    continue

                if msg_type == "chat":
                    user_message = data.get("message", "").strip()
                    if not user_message:
                        logger.warning("공백 메시지 수신")
                        continue

                    session = self.session_manager.get_or_create_session(member_id)
                    reply, is_done = session.generate_response(user_message)
                    timestamp = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()

                    self.producer.send_chat_response(member_id, reply, timestamp)

                    if session.turn_count in [3, 6, 9, 12, 15, 18, 20]:
                        self.producer.send_score_request(member_id)

                    if is_done:
                        self.producer.send_done_signal(member_id)
                        self.session_manager.remove_session(member_id)
                        logger.info(f"대화 종료됨 (자동): {member_id}")

                elif msg_type == "done":
                    self.session_manager.remove_session(member_id)
                    logger.info(f"세션 종료됨: {member_id}")

                else:
                    logger.warning(f"알 수 없는 type: {msg_type}")

            except Exception as e:
                logger.error(f"메시지 처리 오류: {e}")
