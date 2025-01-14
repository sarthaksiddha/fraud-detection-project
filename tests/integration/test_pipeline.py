import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.data_ingestion.kafka_consumer import TransactionConsumer
from src.feature_engineering.feature_processor import FeatureProcessor
from src.models.fraud_detector import FraudDetector
from src.monitoring.metrics_collector import MetricsCollector

class TestEndToEndPipeline:
    @pytest.fixture
    def sample_transaction(self):
        return {
            'transaction_id': 'TX123',
            'user_id': 1,
            'amount': 1000.0,
            'currency': 'USD',
            'merchant_category': 'retail',
            'timestamp': datetime.now().isoformat(),
            'location': {
                'latitude': 40.7128,
                'longitude': -74.0060
            }
        }

    @pytest.fixture
    def feature_processor(self):
        return FeatureProcessor(lookback_days=30)

    @pytest.fixture
    def fraud_detector(self):
        return FraudDetector()

    @pytest.fixture
    def metrics_collector(self):
        return MetricsCollector()

    def test_feature_generation(self, sample_transaction, feature_processor):
        """Test feature generation process."""
        features = feature_processor.process_transaction(sample_transaction)

        # Verify features structure
        assert isinstance(features, dict)
        assert 'amount' in features
        assert 'hour_of_day' in features
        assert 'is_weekend' in features
        assert 'transaction_frequency' in features

        # Verify feature values
        assert features['amount'] == sample_transaction['amount']
        assert 0 <= features['hour_of_day'] <= 23
        assert isinstance(features['is_weekend'], bool)

    def test_model_prediction(self, sample_transaction, feature_processor,
                            fraud_detector):
        """Test model prediction pipeline."""
        # Generate features
        features = feature_processor.process_transaction(sample_transaction)

        # Get prediction
        prediction = fraud_detector.predict(features)

        # Verify prediction structure
        assert isinstance(prediction, dict)
        assert 'is_fraud' in prediction
        assert 'fraud_probability' in prediction
        assert 'anomaly_score' in prediction

        # Verify prediction values
        assert isinstance(prediction['is_fraud'], bool)
        assert 0 <= prediction['fraud_probability'] <= 1
        assert isinstance(prediction['anomaly_score'], float)

    def test_metrics_collection(self, sample_transaction, feature_processor,
                              fraud_detector, metrics_collector):
        """Test metrics collection process."""
        # Process transaction
        features = feature_processor.process_transaction(sample_transaction)
        prediction = fraud_detector.predict(features)

        # Record metrics
        metrics_collector.record_prediction(
            latency=0.1,
            score=prediction['fraud_probability']
        )

        # Get current metrics
        current_metrics = metrics_collector.get_current_metrics()

        # Verify metrics
        assert isinstance(current_metrics, dict)
        assert 'cpu_usage' in current_metrics
        assert 'memory_usage' in current_metrics
        assert 'active_transactions' in current_metrics

    def test_error_handling(self, sample_transaction, feature_processor,
                           fraud_detector):
        """Test error handling in pipeline."""
        # Test with invalid transaction
        invalid_transaction = sample_transaction.copy()
        invalid_transaction.pop('amount')

        with pytest.raises(Exception):
            feature_processor.process_transaction(invalid_transaction)

        # Test with invalid features
        invalid_features = {
            'amount': 'invalid_amount',
            'hour_of_day': 25
        }

        with pytest.raises(Exception):
            fraud_detector.predict(invalid_features)

    def test_performance_benchmarks(self, sample_transaction, feature_processor,
                                  fraud_detector):
        """Test performance benchmarks."""
        import time

        # Measure feature generation time
        start_time = time.time()
        features = feature_processor.process_transaction(sample_transaction)
        feature_time = time.time() - start_time

        # Measure prediction time
        start_time = time.time()
        prediction = fraud_detector.predict(features)
        prediction_time = time.time() - start_time

        # Verify performance
        assert feature_time < 1.0  # Feature generation should take less than 1 second
        assert prediction_time < 0.5  # Prediction should take less than 0.5 seconds