from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging
import json
from datetime import datetime
from typing import Dict, Any, List
import queue
import threading
import time

class ElasticsearchHandler(logging.Handler):
    """Custom logging handler for Elasticsearch."""
    
    def __init__(self, host: str, index_prefix: str, batch_size: int = 100):
        """Initialize Elasticsearch handler.
        
        Args:
            host (str): Elasticsearch host URL
            index_prefix (str): Prefix for log indices
            batch_size (int): Number of logs to batch before sending
        """
        super().__init__()
        self.host = host
        self.index_prefix = index_prefix
        self.batch_size = batch_size
        
        self.es = Elasticsearch([host])
        self.log_queue = queue.Queue()
        self.running = True