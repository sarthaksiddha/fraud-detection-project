import numpy as np
from typing import Dict, Any, Optional
from sklearn.ensemble import IsolationForest
import joblib
import logging

class FraudDetector:
    """Real-time fraud detection model using Isolation Forest."""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the fraud detector.
        
        Args:
            model_path (str, optional): Path to saved model file
        """
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.feature_names = [
            'amount', 'hour_of_day', 'is_weekend',
            'avg_amount', 'max_amount', 'transaction_frequency', 'std_amount',
            'distance_from_last_tx',
            'tx_count_1h', 'tx_count_24h', 'tx_count_7d'
        ]
        
        if model_path:
            self.load_model(model_path)
        else:
            self.model = IsolationForest(
                contamination=0.1,
                random_state=42
            )