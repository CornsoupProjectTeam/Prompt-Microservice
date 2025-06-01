# main.py

import logging
from multiprocessing import Process
from app.application.chat_consumer import ChatConsumer
from app.application.monitor_service import MonitorService

logging.basicConfig(level=logging.INFO)

def start_chat_consumer():
    """
    주감지 체인을 실행하는 함수
    """
    logging.info("주감지 체인 시작")
    ChatConsumer().start()  # ← 실행 메서드 호출 추가

def start_monitor_chain():
    """
    감시 체인을 실행하는 함수
    """
    logging.info("감시 체인 시작")
    MonitorService().listen_for_scores()  # ← 실행 메서드 호출 추가

if __name__ == "__main__":
    # 멀티 프로세싱을 이용하여 병렬로 실행
    process1 = Process(target=start_chat_consumer)
    process2 = Process(target=start_monitor_chain)

    process1.start()
    process2.start()

    process1.join()
    process2.join()
