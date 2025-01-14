import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta

class FeatureProcessor:
    """Process raw transaction data into features for fraud detection."""
    
    def __init__(self, lookback_days: int = 30):
        """Initialize the feature processor.
        
        Args:
            lookback_days (int): Number of days to look back for historical patterns
        """
        self.lookback_days = lookback_days
        self.historical_transactions = pd.DataFrame()
        
    def _calculate_user_statistics(self, user_id: int, current_timestamp: datetime) -> Dict[str, float]:
        """Calculate statistical features for a user."""
        # Filter user's transactions within lookback period
        lookback_date = current_timestamp - timedelta(days=self.lookback_days)
        user_history = self.historical_transactions[
            (self.historical_transactions['user_id'] == user_id) &
            (self.historical_transactions['timestamp'] >= lookback_date)
        ]
        
        if user_history.empty:
            return {
                'avg_amount': 0.0,
                'max_amount': 0.0,
                'transaction_frequency': 0.0,
                'std_amount': 0.0
            }
            
        return {
            'avg_amount': user_history['amount'].mean(),
            'max_amount': user_history['amount'].max(),
            'transaction_frequency': len(user_history) / self.lookback_days,
            'std_amount': user_history['amount'].std()
        }