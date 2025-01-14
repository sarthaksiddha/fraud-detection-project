import pytest
import numpy as np
from datetime import datetime, timedelta
from src.models.fraud_detector import FraudDetector
from src.feature_engineering.feature_processor import FeatureProcessor

@pytest.fixture
def sample_transaction():
    """Generate a sample transaction for testing."""
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
def feature_processor():
    """Initialize feature processor for testing."""
    return FeatureProcessor(lookback_days=30)

@pytest.fixture
def fraud_detector():
    """Initialize fraud detector for testing."""
    return FraudDetector()

def test_feature_generation(feature_processor, sample_transaction):
    """Test feature generation from transaction."""
    features = feature_processor.process_transaction(sample_transaction)
    
    # Check if all required features are present
    required_features = [
        'amount', 'hour_of_day', 'is_weekend',
        'avg_amount', 'max_amount', 'transaction_frequency',
        'distance_from_last_tx'
    ]
    
    for feature in required_features:
        assert feature in features
        
    # Check feature values
    assert features['amount'] == sample_transaction['amount']
    assert 0 <= features['hour_of_day'] <= 23
    assert isinstance(features['is_weekend'], bool)

def test_fraud_prediction(fraud_detector, feature_processor, sample_transaction):
    """Test fraud prediction pipeline."""
    # Generate features
    features = feature_processor.process_transaction(sample_transaction)
    
    # Get prediction
    prediction = fraud_detector.predict(features)
    
    # Check prediction structure
    assert 'is_fraud' in prediction
    assert 'fraud_probability' in prediction
    assert 'anomaly_score' in prediction
    
    # Check value ranges
    assert isinstance(prediction['is_fraud'], bool)
    assert 0 <= prediction['fraud_probability'] <= 1