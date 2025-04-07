# application/chat_consumer.py

import json
import logging
from application.session_manager import SessionManager
from infrastructure.kafka import create_consumer, KafkaMessageProducer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

session_manager = SessionManager()
producer = KafkaMessageProducer()

def ChatConsumer():
    consumer = create_consumer("chat_input")
    logger.info("Kafka Consumer 시작 (chat_input)")

    for message in consumer:
        try:
            data = json.loads(message.value)
            msg_type = data.get("type")
            memberId = data.get("memberId")

            if not memberId:
                logger.warning("memberId가 누락된 메시지")
                continue

            # (1) 채팅 메시지 처리
            if msg_type == "chat":
                user_message = data.get("message", "")
                if not user_message.strip():
                    logger.warning("공백 메시지 수신")
                    continue

                session = session_manager.get_or_create_session(memberId)
                reply, is_done = session.generate_response(user_message)

                # 응답 전송
                producer.send_chat_response(
                    memberId=memberId,
                    message=reply,
                    timestamp=data.get("timestamp")
                )

                # 대화 종료 처리
                if is_done:
                    producer.send_done_signal(memberId)
                    session_manager.remove_session(memberId)
                    logger.info(f"대화 종료됨 (자동): {memberId}")

            # (2) 종료 메시지
            elif msg_type == "done":
                session_manager.remove_session(memberId)
                logger.info(f"세션 종료됨: {memberId}")

            else:
                logger.warning(f"알 수 없는 type: {msg_type}")

        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")
