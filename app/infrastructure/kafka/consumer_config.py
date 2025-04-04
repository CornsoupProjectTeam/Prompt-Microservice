import os
from dotenv import load_dotenv

load_dotenv()

def get_kafka_broker():
    return os.getenv("KAFKA_BROKER", "localhost:9092")

def get_kafka_consumer_config():
    return {
        "bootstrap_servers": get_kafka_broker(),
        "group_id": "prompt-consumer-group",
        "auto_offset_reset": "latest",
        "enable_auto_commit": True
    }
