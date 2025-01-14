from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
import joblib
import mlflow
import logging
from datetime import datetime
from src.monitoring.model_drift_detector import ModelDriftDetector

class ModelTrainer:
    """Train and evaluate fraud detection models."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize model trainer.
        
        Args:
            config (Dict[str, Any]): Training configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Set up MLflow tracking
        mlflow.set_tracking_uri(config['mlflow_uri'])
        mlflow.set_experiment(config['experiment_name'])
        
        # Initialize drift detector
        self.drift_detector = ModelDriftDetector()
    
    def train_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Train a new fraud detection model.
        
        Args:
            training_data (pd.DataFrame): Training data
            
        Returns:
            Dict[str, Any]: Training results and metrics
        """
        try:
            with mlflow.start_run():
                # Log training parameters
                mlflow.log_params(self.config['model_params'])
                
                # Prepare data
                X_train, X_val = train_test_split(
                    training_data,
                    test_size=0.2,
                    random_state=42
                )
                
                # Train model
                model = IsolationForest(**self.config['model_params'])
                model.fit(X_train)
                
                # Calculate metrics
                train_scores = model.score_samples(X_train)
                val_scores = model.score_samples(X_val)
                
                metrics = {
                    'train_mean_score': float(np.mean(train_scores)),
                    'train_std_score': float(np.std(train_scores)),
                    'val_mean_score': float(np.mean(val_scores)),
                    'val_std_score': float(np.std(val_scores))
                }
                
                # Log metrics
                mlflow.log_metrics(metrics)
                
                # Save model
                model_path = self._save_model(model)
                mlflow.log_artifact(model_path)
                
                return {
                    'model': model,
                    'metrics': metrics,
                    'model_path': model_path
                }
                
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            raise
    
    def evaluate_model(self, model: IsolationForest,
                       data: pd.DataFrame) -> Dict[str, float]:
        """Evaluate model performance.
        
        Args:
            model (IsolationForest): Trained model
            data (pd.DataFrame): Evaluation data
            
        Returns:
            Dict[str, float]: Evaluation metrics
        """
        try:
            # Get predictions and scores
            predictions = model.predict(data)
            scores = model.score_samples(data)
            
            # Calculate metrics
            metrics = {
                'anomaly_rate': float(np.mean(predictions == -1)),
                'mean_score': float(np.mean(scores)),
                'std_score': float(np.std(scores))
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {str(e)}")
            raise
    
    def check_model_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Check for model drift using current data.
        
        Args:
            current_data (pd.DataFrame): Current production data
            
        Returns:
            Dict[str, Any]: Drift metrics and analysis
        """
        try:
            drift_metrics = self.drift_detector.calculate_drift(current_data)
            
            return {
                'drift_detected': drift_metrics.overall_drift_score > 
                    self.config['drift_threshold'],
                'drift_score': drift_metrics.overall_drift_score,
                'feature_drifts': drift_metrics.feature_drifts,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking model drift: {str(e)}")
            raise
    
    def _save_model(self, model: IsolationForest) -> str:
        """Save trained model to disk.
        
        Args:
            model (IsolationForest): Trained model
            
        Returns:
            str: Path to saved model
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_path = f"models/fraud_detector_{timestamp}.joblib"
        
        joblib.dump(model, model_path)
        return model_path