from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time
from typing import Dict, Any
from datetime import datetime
import logging
from dataclasses import dataclass
import threading

@dataclass
class MetricsConfig:
    port: int = 8000
    update_interval: int = 60  # seconds
    percentile_buckets: list = (0.5, 0.75, 0.9, 0.95, 0.99)

class MetricsCollector:
    """Collect and expose metrics for Prometheus."""
    
    def __init__(self, config: MetricsConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Transaction metrics
        self.transaction_counter = Counter(
            'fraud_detection_transactions_total',
            'Total number of processed transactions'
        )
        self.transaction_amount = Histogram(
            'fraud_detection_transaction_amount',
            'Transaction amount distribution',
            buckets=[10, 50, 100, 500, 1000, 5000, 10000]
        )