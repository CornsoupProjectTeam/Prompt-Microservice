# main.py
import logging
import json
from kafka import KafkaConsumer
from application.prompt_service import PersChatService
from infrastructure.kafka.producer import KafkaMessageProducer
from infrastructure.config import get_env

# ✅ 안전하게 JSON 디코딩
def safe_json_loads(v):
    if v:
        try:
            return json.loads(v.decode("utf-8"))
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError 발생: {e}")
            return None
    return None

# ✅ Kafka Consumer 생성
def create_consumer(topic: str, bootstrap_servers: str) -> KafkaConsumer:
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=get_env("KAFKA_CONSUMER_GROUP", "prompt-microservice"),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda v: safe_json_loads(v)
    )

# ✅ 메시지 소비 및 처리
def consume_messages(consumer: KafkaConsumer, chat_service: PersChatService, producer: KafkaMessageProducer):
    logging.info("Kafka Consumer 대기 중...")

    for message in consumer:
        data = message.value
        if not data:
            logging.warning("빈 메시지 수신 - 무시")
            continue

        memberId = data.get("memberId", "unknown")
        msg_type = data.get("type")
        user_message = data.get("message", "")
        timestamp = data.get("timestamp")

        try:
            if msg_type == "chat" and user_message.strip():
                logging.info(f"[{memberId}] 사용자 입력 수신: {user_message}")

                # ✅ 응답 및 종료 여부 반환
                reply, is_done = chat_service.generate_response(user_message)

                # ✅ Kafka에 응답 전송
                producer.send_chat_response(
                    memberId=memberId,
                    message=reply,
                    timestamp=timestamp
                )

                # ✅ 대화 종료 시 done 발행
                if is_done:
                    producer.send_done_signal(memberId, timestamp)
                    logging.info(f"[{memberId}] chat_done 전송 완료")

            elif msg_type == "done":
                logging.info(f"[{memberId}] 세션 종료 요청 수신")
                # TODO: 필요한 세션 정리 로직이 있다면 여기에 작성

        except Exception as e:
            logging.error(f"[{memberId}] 처리 중 오류: {e}")

# ✅ 진입점
def main():
    logging.basicConfig(level=logging.INFO)

    topic = get_env("KAFKA_INPUT_TOPIC", "chat_input")
    broker = get_env("KAFKA_BROKER", "10.0.0.12:9092")

    consumer = create_consumer(topic, broker)
    producer = KafkaMessageProducer()
    chat_service = PersChatService()

    logging.info("✅ Prompt-Microservice 시작됨")
    consume_messages(consumer, chat_service, producer)

if __name__ == "__main__":
    main()
