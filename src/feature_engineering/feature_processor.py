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
        """Calculate statistical features for a user based on their transaction history.
        
        Args:
            user_id (int): User identifier
            current_timestamp (datetime): Current transaction timestamp
            
        Returns:
            Dict[str, float]: Dictionary of calculated features
        """
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
            
        # Calculate features
        return {
            'avg_amount': user_history['amount'].mean(),
            'max_amount': user_history['amount'].max(),
            'transaction_frequency': len(user_history) / self.lookback_days,
            'std_amount': user_history['amount'].std()
        }
        
    def _calculate_location_features(self, transaction: Dict[str, Any]) -> Dict[str, float]:
        """Calculate location-based features for transaction.
        
        Args:
            transaction (Dict[str, Any]): Current transaction data
            
        Returns:
            Dict[str, float]: Location-based features
        """
        if not self.historical_transactions.empty:
            # Get user's last transaction location
            user_last_tx = self.historical_transactions[
                self.historical_transactions['user_id'] == transaction['user_id']
            ].sort_values('timestamp').iloc[-1]
            
            # Calculate distance from last transaction
            distance = np.sqrt(
                (transaction['location']['latitude'] - user_last_tx['latitude'])**2 +
                (transaction['location']['longitude'] - user_last_tx['longitude'])**2
            )
        else:
            distance = 0.0
            
        return {
            'distance_from_last_tx': distance
        }
        
    def _calculate_velocity_features(self, transaction: Dict[str, Any]) -> Dict[str, float]:
        """Calculate velocity-based features (transaction frequency patterns).
        
        Args:
            transaction (Dict[str, Any]): Current transaction data
            
        Returns:
            Dict[str, float]: Velocity-based features
        """
        current_timestamp = pd.to_datetime(transaction['timestamp'])
        
        # Calculate transactions in last hour, day, week
        user_history = self.historical_transactions[
            self.historical_transactions['user_id'] == transaction['user_id']
        ]
        
        if user_history.empty:
            return {
                'tx_count_1h': 0,
                'tx_count_24h': 0,
                'tx_count_7d': 0
            }
            
        time_windows = {
            'tx_count_1h': timedelta(hours=1),
            'tx_count_24h': timedelta(days=1),
            'tx_count_7d': timedelta(days=7)
        }
        
        counts = {}
        for feature, time_window in time_windows.items():
            counts[feature] = len(
                user_history[user_history['timestamp'] >= current_timestamp - time_window]
            )
            
        return counts
    
    def update_historical_data(self, transaction: Dict[str, Any]):
        """Update historical transaction database with new transaction.
        
        Args:
            transaction (Dict[str, Any]): New transaction data
        """
        tx_df = pd.DataFrame([{
            'user_id': transaction['user_id'],
            'amount': transaction['amount'],
            'timestamp': pd.to_datetime(transaction['timestamp']),
            'latitude': transaction['location']['latitude'],
            'longitude': transaction['location']['longitude'],
            'merchant_category': transaction['merchant_category']
        }])
        
        self.historical_transactions = pd.concat(
            [self.historical_transactions, tx_df]
        ).reset_index(drop=True)
        
        # Remove transactions older than lookback period
        cutoff_date = pd.to_datetime('now') - timedelta(days=self.lookback_days)
        self.historical_transactions = self.historical_transactions[
            self.historical_transactions['timestamp'] >= cutoff_date
        ]
    
    def process_transaction(self, transaction: Dict[str, Any]) -> Dict[str, float]:
        """Process a single transaction and generate features.
        
        Args:
            transaction (Dict[str, Any]): Transaction data
            
        Returns:
            Dict[str, float]: Calculated features for the transaction
        """
        # Update historical data first
        self.update_historical_data(transaction)
        
        # Calculate all features
        features = {}
        
        # Basic transaction features
        features.update({
            'amount': transaction['amount'],
            'hour_of_day': pd.to_datetime(transaction['timestamp']).hour,
            'is_weekend': pd.to_datetime(transaction['timestamp']).weekday() >= 5
        })
        
        # Add statistical features
        features.update(
            self._calculate_user_statistics(
                transaction['user_id'],
                pd.to_datetime(transaction['timestamp'])
            )
        )
        
        # Add location features
        features.update(
            self._calculate_location_features(transaction)
        )
        
        # Add velocity features
        features.update(
            self._calculate_velocity_features(transaction)
        )
        
        return features