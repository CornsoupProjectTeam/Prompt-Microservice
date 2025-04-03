import logging
from application.chat_consumer import ChatMessageConsumer

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer = ChatMessageConsumer()
    consumer.consume_messages()
