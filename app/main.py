#main.py
import logging
import json
import re
from kafka import KafkaConsumer
from langchain_core.messages import HumanMessage, AIMessage
from collections import defaultdict
from domain.prompt_generator import PromptGenerator
from infrastructure.kafka.producer import KafkaMessageProducer
from infrastructure.config import get_env

logger = logging.getLogger(__name__)

class PersChatService:
    def __init__(self):
        self.histories = defaultdict(list)       # memberId별 대화 히스토리
        self.turn_counts = defaultdict(int)
        self.turn_count = 0
        self.generator = PromptGenerator()
        self.start_message = "안녕하세요! 오늘 기분은 어떠세요?"

    def clean_reply(self, text: str) -> str:
            """
            불필요한 접두어, 이스케이프 문자, 따옴표 등을 제거하여 정제된 답변 반환
            """
            text = text.strip()  # 양 끝 공백 제거
            text = re.sub(r'^["\']?|["\']?$', '', text)  # 양쪽 따옴표 제거
            text = re.sub(r'^(AI|Assistant|챗봇)\s*:\s*', '', text, flags=re.IGNORECASE)  # AI: 제거
            text = re.sub(r'[\n\r\t]+', ' ', text)
            text = text.replace("\\", "")
            
            return text.strip()

    def generate_response(self, member_id: str, user_input: str) -> tuple[str, bool]:
            self.turn_counts[member_id] += 1
            turn = self.turn_counts[member_id]
            logger.info(f"[{member_id} / turn {turn}] 사용자 입력 수신됨: {user_input}")

            # history 초기화 및 시작 메시지 세팅
            if turn == 1:
                self.histories[member_id].append(AIMessage(content=self.start_message))

            self.histories[member_id].append(HumanMessage(content=user_input))

            formatted_history = [
                {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
                for msg in self.histories[member_id]
            ]

            if turn >= 10:
                final_reply = "아쉽지만 대화는 여기까지에요.."
                self.histories[member_id].append(AIMessage(content=final_reply))
                return final_reply, True

            try:
                raw_reply = self.generator.generate_reply(formatted_history)

                reply = self.clean_reply(raw_reply)
                self.histories[member_id].append(AIMessage(content=reply))
                return reply, False

            except Exception as e:
                logger.error(f"[{member_id}] 응답 생성 실패: {e}")
                return "챗봇 응답 생성 중 오류가 발생했어요.", False

    # def generate_response(self, user_input: str) -> str:
    #     logger.info(f"[{self.turn_count}] 사용자 입력 수신됨: {user_input}")
    #     """
    #     사용자 입력을 받아 응답을 생성하고,
    #     종료 조건이 충족되면 done 상태를 함께 반환합니다.

    #     Returns:
    #         - reply: 챗봇 응답
    #         - is_done: 대화 종료 여부 (True면 done 발행 필요)
    #     """
    #     try:
    #         self.turn_count += 1
    #         logger.info(f"[{self.turn_count}] 사용자 입력 수신됨: {user_input}")
    #         self.history.append(HumanMessage(content=user_input))

    #         # 메시지 포맷 구성
    #         formatted_history = [
    #             {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
    #             for msg in self.history
    #         ]

    #         # 마지막 응답 처리
    #         if self.turn_count >= 3:
    #             final_reply = "아쉽지만 대화는 여기까지에요.."
    #             self.history.append(AIMessage(content=final_reply))
    #             return final_reply, True  # 종료 상태

    #         # 일반 응답 처리
    #         raw_reply = self.generator.generate_reply(formatted_history)
    #         reply = self.clean_reply(raw_reply)
    #         self.history.append(AIMessage(content=reply))
    #         return reply, False

    #     except Exception as e:
    #         logger.error(f"응답 생성 실패: {e}")
    #         return "챗봇 응답 생성 중 오류가 발생했어요.", False


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
        group_id=get_env("KAFKA_CONSUMER_GROUP", "prompt-microservice"),
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
                reply, is_done = chat_service.generate_response(member_id=user_id, user_input=user_input)

                # Kafka에 응답 발행
                producer.send_chat_response(
                    memberId=user_id,
                    message=reply,
                    timestamp=timestamp
                )

            if is_done:
                producer.send_done_signal(user_id)

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
