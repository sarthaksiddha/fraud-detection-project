from prometheus_client import Counter, Gauge, Histogram
import time
from typing import Dict, Any
from datetime import datetime
import logging
from dataclasses import dataclass
import threading
import psutil
import numpy as np

class MetricsCollector:
    """Collect and store system metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.logger = logging.getLogger(__name__)
        
        # System metrics
        self.cpu_usage = Gauge('system_cpu_usage', 'CPU usage percentage')
        self.memory_usage = Gauge('system_memory_usage', 'Memory usage percentage')
        self.disk_usage = Gauge('system_disk_usage', 'Disk usage percentage')
        
        # Application metrics
        self.active_transactions = Gauge(
            'active_transactions',
            'Number of transactions being processed'
        )
        self.transaction_duration = Histogram(
            'transaction_duration_seconds',
            'Time taken to process transactions',
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
        )
        
        # Model metrics
        self.prediction_latency = Histogram(
            'model_prediction_latency',
            'Time taken for model predictions',
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0)
        )
        self.prediction_scores = Histogram(
            'model_prediction_scores',
            'Distribution of fraud prediction scores',
            buckets=np.linspace(0, 1, 11).tolist()
        )
        
        # Error metrics
        self.error_counter = Counter('errors_total', 'Total number of errors')
        self.error_types = Counter(
            'error_types_total',
            'Total errors by type',
            ['error_type']
        )
        
        # Start collection thread
        self.start_collection()
    
    def start_collection(self):
        """Start background metrics collection."""
        def collect_metrics():
            while True:
                try:
                    self._update_system_metrics()
                    time.sleep(15)  # Collect every 15 seconds
                except Exception as e:
                    self.logger.error(f"Error collecting metrics: {e}")
        
        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
    
    def _update_system_metrics(self):
        """Update system resource metrics."""
        # CPU usage
        self.cpu_usage.set(psutil.cpu_percent())
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.memory_usage.set(memory.percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.disk_usage.set(disk.percent)
    
    def record_transaction_start(self):
        """Record start of transaction processing."""
        self.active_transactions.inc()
    
    def record_transaction_end(self, duration: float):
        """Record end of transaction processing."""
        self.active_transactions.dec()
        self.transaction_duration.observe(duration)
    
    def record_prediction(self, latency: float, score: float):
        """Record model prediction metrics."""
        self.prediction_latency.observe(latency)
        self.prediction_scores.observe(score)
    
    def record_error(self, error_type: str):
        """Record error occurrence."""
        self.error_counter.inc()
        self.error_types.labels(error_type=error_type).inc()
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current metric values.
        
        Returns:
            Dict[str, float]: Current metrics
        """
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'active_transactions': float(self.active_transactions._value.get()),
        }
