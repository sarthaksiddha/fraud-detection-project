from typing import Dict, Any, List
import pandas as pd
from datetime import datetime, timedelta
import logging
from src.models.fraud_detector import FraudDetector
from src.feature_engineering.feature_processor import FeatureProcessor

class BatchProcessor:
    """Process historical transactions in batch mode."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize batch processor.
        
        Args:
            config (Dict[str, Any]): Batch processing configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.feature_processor = FeatureProcessor()
        self.model = FraudDetector()
    
    def process_historical_data(self, start_date: datetime,
                               end_date: datetime) -> Dict[str, Any]:
        """Process historical transaction data.
        
        Args:
            start_date (datetime): Start date for processing
            end_date (datetime): End date for processing
            
        Returns:
            Dict[str, Any]: Processing results and statistics
        """
        try:
            # Load historical data
            transactions = self._load_transactions(start_date, end_date)
            
            # Process in batches
            batch_size = self.config.get('batch_size', 1000)
            results = []
            
            for i in range(0, len(transactions), batch_size):
                batch = transactions[i:i + batch_size]
                batch_results = self._process_batch(batch)
                results.extend(batch_results)
            
            # Aggregate results
            return self._aggregate_results(results)
            
        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            raise
    
    def _load_transactions(self, start_date: datetime,
                          end_date: datetime) -> pd.DataFrame:
        """Load historical transactions from database.
        
        Args:
            start_date (datetime): Start date
            end_date (datetime): End date
            
        Returns:
            pd.DataFrame: Historical transactions
        """
        # Implement database loading logic here
        pass
    
    def _process_batch(self, batch: pd.DataFrame) -> List[Dict[str, Any]]:
        """Process a batch of transactions.
        
        Args:
            batch (pd.DataFrame): Batch of transactions
            
        Returns:
            List[Dict[str, Any]]: Processing results
        """
        results = []
        
        for _, transaction in batch.iterrows():
            try:
                # Generate features
                features = self.feature_processor.process_transaction(
                    transaction.to_dict()
                )
                
                # Get prediction
                prediction = self.model.predict(features)
                
                results.append({
                    'transaction_id': transaction['transaction_id'],
                    'features': features,
                    'prediction': prediction
                })
                
            except Exception as e:
                self.logger.error(
                    f"Error processing transaction {transaction['transaction_id']}: "
                    f"{str(e)}"
                )
        
        return results
    
    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate batch processing results.
        
        Args:
            results (List[Dict[str, Any]]): Individual results
            
        Returns:
            Dict[str, Any]: Aggregated statistics
        """
        total_transactions = len(results)
        fraud_predictions = sum(
            1 for r in results if r['prediction']['is_fraud']
        )
        
        return {
            'total_processed': total_transactions,
            'fraud_detected': fraud_predictions,
            'fraud_rate': fraud_predictions / total_transactions 
                if total_transactions > 0 else 0,
            'processing_time': datetime.utcnow()
        }