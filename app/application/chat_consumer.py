# application/chat_consumer.py

import json
import logging
from kafka import KafkaConsumer
from domain.prompt_generator import PersChatService
from application.session_manager import SessionManager
from infrastructure.kafka.producer import send_chat_output_message
from infrastructure.kafka.consumer_config import get_kafka_config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 세션 관리 객체 (member_id별 서비스 인스턴스 유지)
session_manager = SessionManager()

def start_consumer():
    consumer = KafkaConsumer(
        "chat_input",
        **get_kafka_config()
    )
    logger.info("Kafka Consumer 시작 (chat_input)")

    for message in consumer:
        try:
            data = json.loads(message.value.decode("utf-8"))
            msg_type = data.get("type")  # "chat" 또는 "done"
            member_id = data.get("member_id")

            if not member_id:
                logger.warning("member_id가 누락된 메시지")
                continue

            # (1) 채팅 메시지 도착
            if msg_type == "chat":
                user_message = data.get("message", "")
                if not user_message.strip():
                    logger.warning("공백 메시지 수신")
                    continue

                # 세션 객체 가져오기 (없으면 생성)
                session = session_manager.get_or_create_session(member_id)

                # 응답 생성
                ai_response = session.generate_response(user_message)

                # 응답 Kafka로 발행
                response_message = {
                    "member_id": member_id,
                    "message": ai_response,
                    "timestamp": data.get("timestamp")
                }
                send_chat_output_message(response_message)

            # (2) 채팅 종료 시그널
            elif msg_type == "done":
                session_manager.remove_session(member_id)
                logger.info(f"세션 종료됨: {member_id}")

            else:
                logger.warning(f"알 수 없는 type: {msg_type}")

        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")
