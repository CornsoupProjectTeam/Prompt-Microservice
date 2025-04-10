#main.py
import logging
import json
from kafka import KafkaConsumer
from langchain_core.messages import HumanMessage, AIMessage
from application.prompt_service import PersChatService
from domain.prompt_generator import PromptGenerator
from infrastructure.kafka.producer import KafkaMessageProducer
from infrastructure.config import get_env




def safe_json_loads(v):
    if v:
        try:
            return json.loads(v.decode("utf-8"))
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError 발생: {e}")
            return None
    return None


def create_consumer(topic: str, bootstrap_servers: str) -> KafkaConsumer:
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=get_env("KAFKA_CONSUMER_GROUP", "prompt-consumer-group"),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda v: safe_json_loads(v)
    )


def consume_messages(consumer: KafkaConsumer, chat_service: PersChatService, producer: KafkaMessageProducer):
    logging.info("Kafka Consumer 대기 중...")

    for message in consumer:
        data = message.value

        if not data:
            logging.warning("빈 메시지 수신 - 무시")
            continue

        user_id = data.get("memberId", "unknown")
        msg_type = data.get("type")
        user_input = data.get("message", "")
        timestamp = data.get("timestamp")

        try:
            if msg_type == "chat" and user_input.strip():
                logging.info(f"[{user_id}] 사용자 입력 수신: {user_input}")
                reply = chat_service.generate_response(user_input)

                # Kafka에 응답 발행
                producer.send_chat_response(
                    memberId=user_id,
                    message=reply,
                    timestamp=timestamp
                )

            elif msg_type == "done":
                logging.info(f"[{user_id}] 세션 종료 요청 수신")
                # 세션 초기화 등 처리 가능

        except Exception as e:
            logging.error(f"[{user_id}] 처리 중 오류: {e}")


def main():
    logging.basicConfig(level=logging.INFO)

    topic = get_env("KAFKA_INPUT_TOPIC", "chat_input")
    broker = get_env("KAFKA_BROKER", "10.0.0.12:9092")

    consumer = create_consumer(topic, broker)
    producer = KafkaMessageProducer()
    chat_service = PersChatService()

    logging.info("Prompt-Microservice 시작됨")
    consume_messages(consumer, chat_service, producer)


if __name__ == "__main__":
    main()
