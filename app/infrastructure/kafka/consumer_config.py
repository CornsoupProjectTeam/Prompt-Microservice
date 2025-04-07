import os
from dotenv import load_dotenv
from kafka import KafkaConsumer

load_dotenv()

def get_kafka_broker():
    return os.getenv("KAFKA_BROKER", "210.110.103.135:9092")

def create_consumer(topic: str) -> KafkaConsumer:
    return KafkaConsumer(
        topic,
        bootstrap_servers=get_kafka_broker(),
        group_id="prompt-consumer-group",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda m: m.decode('utf-8') 
    )

