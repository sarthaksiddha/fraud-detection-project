from typing import Dict, Any, Optional
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from src.data_ingestion.kafka_consumer import TransactionConsumer
from src.feature_engineering.feature_processor import FeatureProcessor
from src.models.fraud_detector import FraudDetector
from src.monitoring.metrics_collector import MetricsCollector

@dataclass
class PipelineResult:
    transaction_id: str
    features: Dict[str, float]
    prediction: Dict[str, Any]
    processing_time: float
    status: str
    error: Optional[str] = None

class PipelineOrchestrator:
    """Orchestrate the fraud detection pipeline."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize pipeline orchestrator.
        
        Args:
            config (Dict[str, Any]): Pipeline configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.feature_processor = FeatureProcessor()
        self.fraud_detector = FraudDetector()
        self.metrics_collector = MetricsCollector()
        
        # Initialize thread pool
        self.executor = ThreadPoolExecutor(
            max_workers=config.get('max_workers', 4)
        )
    
    def process_transaction(self, transaction: Dict[str, Any]) -> PipelineResult:
        """Process a single transaction through the pipeline.
        
        Args:
            transaction (Dict[str, Any]): Transaction data
            
        Returns:
            PipelineResult: Pipeline processing result
        """
        start_time = datetime.now()
        
        try:
            # Record start of processing
            self.metrics_collector.record_transaction_start()
            
            # Generate features
            features = self.feature_processor.process_transaction(transaction)
            
            # Get prediction
            prediction = self.fraud_detector.predict(features)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Record metrics
            self.metrics_collector.record_transaction_end(processing_time)
            self.metrics_collector.record_prediction(
                processing_time,
                prediction['fraud_probability']
            )
            
            return PipelineResult(
                transaction_id=transaction['transaction_id'],
                features=features,
                prediction=prediction,
                processing_time=processing_time,
                status='success'
            )
            
        except Exception as e:
            error_msg = f"Error processing transaction: {str(e)}"
            self.logger.error(error_msg)
            
            # Record error
            self.metrics_collector.record_error('pipeline_error')
            
            return PipelineResult(
                transaction_id=transaction['transaction_id'],
                features={},
                prediction={},
                processing_time=(datetime.now() - start_time).total_seconds(),
                status='error',
                error=error_msg
            )
    
    def process_batch(self, transactions: List[Dict[str, Any]]) -> \
            List[PipelineResult]:
        """Process a batch of transactions in parallel.
        
        Args:
            transactions (List[Dict[str, Any]]): List of transactions
            
        Returns:
            List[PipelineResult]: Processing results
        """
        try:
            # Submit transactions for parallel processing
            futures = [
                self.executor.submit(self.process_transaction, tx)
                for tx in transactions
            ]
            
            # Collect results
            results = [future.result() for future in futures]
            
            # Log batch statistics
            success_count = sum(
                1 for r in results if r.status == 'success'
            )
            self.logger.info(
                f"Processed batch of {len(transactions)} transactions. "
                f"Success: {success_count}, "
                f"Failed: {len(transactions) - success_count}"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing batch: {str(e)}")
            raise
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics.
        
        Returns:
            Dict[str, Any]: Pipeline statistics
        """
        return {
            'metrics': self.metrics_collector.get_current_metrics(),
            'feature_stats': self.feature_processor.get_statistics(),
            'model_stats': self.fraud_detector.get_statistics()
        }
    
    def shutdown(self):
        """Shutdown the pipeline."""
        try:
            self.executor.shutdown(wait=True)
        except Exception as e:
            self.logger.error(f"Error shutting down pipeline: {str(e)}")