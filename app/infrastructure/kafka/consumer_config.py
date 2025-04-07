import os
from dotenv import load_dotenv
from kafka import KafkaConsumer

load_dotenv()

def get_kafka_broker():
    return os.getenv("KAFKA_BROKER", "10.0.0.12:9092")

def create_consumer(topic: str) -> KafkaConsumer:
    return KafkaConsumer(
        topic,
        bootstrap_servers=get_kafka_broker(),
        group_id="prompt-microservice",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda m: m.decode('utf-8') 
    )

