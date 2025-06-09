# application/monitor_service.py

import json
import logging
from collections import defaultdict
from infrastructure.kafka.consumer_config import create_consumer
from infrastructure.kafka.producer import KafkaMessageProducer
from domain.prompt.prompt_generator import PromptGenerator
from application.auxiliary_prompt_service import AuxiliaryPromptService

logger = logging.getLogger(__name__)

class MonitorService:
    def __init__(self):
        self.consumer = create_consumer("chat_score")
        self.kafka_producer = KafkaMessageProducer()
        self.prompt_generator = PromptGenerator()
        self.scores = defaultdict(dict)
        self.turn_counts = defaultdict(int)

        self.required_traits = [
            "성실성", "친화성", "경험에 대한 개방성", "외향성", "신경증"
        ]
        self.check_turns = {2, 3, 4, 5, 6}

    def listen_for_scores(self):
        logger.info("MonitorService 시작 (chat_score 구독 중)")
        for message in self.consumer:
            try:
                data = json.loads(message.value)

                # ✅ 자기 자신이 보낸 메시지 무시
                if data.get("type") != "response_score":
                    continue

                memberId = data["memberId"]
                scores = data["scores"]

                self.scores[memberId].update(scores)
                self.turn_counts[memberId] += 1
                turn = self.turn_counts[memberId]

                logger.info(f"[{memberId}] 현재 턴: {turn}")
                logger.info(f"[{memberId}] 수집된 점수: {self.scores[memberId]}")
                logger.info(f"[{memberId}] 누락된 성향: {self.get_missing_traits(memberId)}")
                logger.info(f"[{memberId}] all_traits_present 결과: {self.all_traits_present(memberId)}")

                # ✅ 조기 종료 또는 보조 질문
                if turn in self.check_turns:
                    if self.all_traits_present(memberId):
                        final_msg = "아쉽지만 대화는 여기까지에요."
                        cleaned = self.prompt_generator.clean_reply(final_msg)
                        self.kafka_producer.send_chat_response(memberId, cleaned)
                        self.kafka_producer.send_done_signal(memberId)
                        logger.info(f"[{memberId}] (조기 종료) {turn}턴에 5성향 수집 완료 → chat_done 발행")
                        self.cleanup(memberId)
                        continue
                    else:
                        missing = self.get_missing_traits(memberId)
                        if missing:
                            support_q = self.prompt_generator.generate_support_reply(missing[0])
                            logger.info(f"[{memberId}] 보조 질문 내용: {support_q}")
                            cleaned = self.prompt_generator.clean_reply(support_q)
                            self.kafka_producer.send_chat_response(memberId, cleaned)
                            logger.info(f"[{memberId}] 보조 질문 전송: {missing[0]}")
                        continue

                # ✅ 20턴 도달 시 직접 질문 or 종료
                if turn >= 7:
                    if self.all_traits_present(memberId):
                        final_msg = "아쉽지만 대화는 여기까지에요."
                        cleaned = self.prompt_generator.clean_reply(final_msg)
                        self.kafka_producer.send_chat_response(memberId, cleaned)
                        self.kafka_producer.send_done_signal(memberId)
                        logger.info(f"[{memberId}] (정상 종료) 20턴에 5성향 완료 → chat_done 발행")
                    else:
                        prompt_service = AuxiliaryPromptService(memberId)
                        missing = self.get_missing_traits(memberId)
                        if missing:
                            direct_q = prompt_service.generate_direct_question(missing[0])
                            cleaned = self.prompt_generator.clean_reply(direct_q)
                            self.kafka_producer.send_chat_response(memberId, cleaned)
                            logger.info(f"[{memberId}] 직접 설문 질문 전송: {missing[0]}")
                    self.cleanup(memberId)

            except Exception as e:
                logger.error(f"MonitorService 처리 오류: {e}")

    def all_traits_present(self, memberId):
        return all(
            trait in self.scores[memberId]
            and self.scores[memberId][trait] is not None
            for trait in self.required_traits
        )

    def get_missing_traits(self, memberId):
        return [
            trait for trait in self.required_traits
            if trait not in self.scores[memberId] or self.scores[memberId][trait] is None
        ]

    def cleanup(self, memberId):
        self.scores.pop(memberId, None)
        self.turn_counts.pop(memberId, None)
