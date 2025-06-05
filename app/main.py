# main.py

import os
import logging
from multiprocessing import Process
from dotenv import load_dotenv

# .env 파일 명시적 로딩
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from app.application.chat_consumer import ChatConsumer
from app.application.monitor_service import MonitorService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def start_chat_consumer():
    """
    주감지 체인을 실행하는 함수
    """
    logging.info("주감지 체인 시작")
    ChatConsumer().start()

def start_monitor_chain():
    """
    감시 체인을 실행하는 함수
    """
    logging.info("감시 체인 시작")
    MonitorService().listen_for_scores()

if __name__ == "__main__":
    process1 = Process(target=start_chat_consumer)
    process2 = Process(target=start_monitor_chain)

    process1.start()
    process2.start()

    process1.join()
    process2.join()
