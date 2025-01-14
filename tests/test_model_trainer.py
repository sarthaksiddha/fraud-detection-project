import pytest
import pandas as pd
import numpy as np
from src.training.model_trainer import ModelTrainer

@pytest.fixture
def sample_config():
    return {
        'mlflow_uri': 'sqlite:///mlflow.db',
        'experiment_name': 'fraud_detection_test',
        'model_params': {
            'n_estimators': 100,
            'contamination': 0.1,
            'random_state': 42
        }
    }

@pytest.fixture
def sample_data():
    np.random.seed(42)
    n_samples = 1000
    
    return pd.DataFrame({
        'amount': np.random.lognormal(mean=4, sigma=1, size=n_samples),
        'transaction_freq': np.random.poisson(lam=5, size=n_samples),
        'distance': np.random.exponential(scale=50, size=n_samples)
    })

def test_model_training(sample_config, sample_data):
    """Test model training pipeline."""
    trainer = ModelTrainer(sample_config)
    
    # Test data preparation
    processed_data = trainer.prepare_training_data(sample_data)
    assert isinstance(processed_data, pd.DataFrame)
    assert not processed_data.empty
    
    # Test model training
    results = trainer.train_model(sample_data)
    assert 'model' in results
    assert 'metrics' in results
    assert 'model_path' in results
    
    # Check metrics
    metrics = results['metrics']
    assert 'mean_anomaly_score' in metrics
    assert 'std_anomaly_score' in metrics
    
    # Test model evaluation
    eval_metrics = trainer.evaluate_model(results['model'], sample_data)
    assert 'anomaly_rate' in eval_metrics
    assert 0 <= eval_metrics['anomaly_rate'] <= 1