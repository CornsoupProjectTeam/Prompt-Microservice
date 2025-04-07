# app/main.py

import logging
import json
from kafka import KafkaConsumer
from app.application.chat_consumer import ChatConsumer
from app.infrastructure.config import get_env



def safe_json_loads(v):
    """안전하게 JSON 디코딩 처리"""
    if v:
        try:
            return json.loads(v.decode("utf-8"))
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError 발생: {e}")
            return None
    return None


def create_consumer(topic: str, bootstrap_servers: str) -> KafkaConsumer:
    """Kafka Consumer 생성"""
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=get_env("KAFKA_GROUP_ID", "prompt-consumer-group"),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda v: safe_json_loads(v)
    )


def consume_messages(consumer: KafkaConsumer, handler: ChatConsumer):
    """Kafka 메시지 수신 후 처리"""
    logging.info("Kafka Consumer 대기 중...")

    for message in consumer:
        json_value = message.value

        if not json_value:
            logging.warning(f"세션 {message.partition}-{message.offset}에서 빈 메시지를 수신했습니다. 무시합니다.")
            continue

        user_id = json_value.get("memberId", "unknown_session")
        logging.info(f"세션 {user_id} 메시지 수신: {json_value}")

        try:
            handler.handle_message(json_value)
        except Exception as e:
            logging.error(f"[Consumer Error] 세션 {user_id} 메시지 처리 중 오류 발생: {e}")


def main():
    """Kafka Consumer 실행"""
    topic = get_env("KAFKA_INPUT_TOPIC", "chat_input")
    bootstrap_servers = get_env("KAFKA_BROKER", "10.0.0.12:9092")

    consumer = create_consumer(topic, bootstrap_servers)
    handler = ChatConsumer()

    consume_messages(consumer, handler)


if __name__ == "__main__":
    main()

