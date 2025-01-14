from confluent_kafka import Consumer, KafkaError
from typing import Dict, Any
import json
import logging

class TransactionConsumer:
    """Kafka consumer for processing real-time transaction data."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Kafka consumer with configuration.
        
        Args:
            config (Dict[str, Any]): Kafka configuration including bootstrap servers,
                                     group id, and other settings
        """
        self.consumer = Consumer(config)
        self.running = False
        self.logger = logging.getLogger(__name__)
    
    def subscribe(self, topics: list):
        """Subscribe to the specified Kafka topics."""
        self.consumer.subscribe(topics)
        self.logger.info(f'Subscribed to topics: {topics}')
    
    def process_message(self, message: Any):
        """Process a single message from Kafka."""
        try:
            if message is None:
                return None
                
            if message.error():
                if message.error().code() == KafkaError._PARTITION_EOF:
                    self.logger.info('Reached end of partition')
                else:
                    self.logger.error(f'Error: {message.error()}')
                return None
                
            # Decode the message value
            value = json.loads(message.value().decode('utf-8'))
            
            # Add processing timestamp
            value['processing_timestamp'] = message.timestamp()[1]
            
            return value
            
        except Exception as e:
            self.logger.error(f'Error processing message: {str(e)}')
            return None