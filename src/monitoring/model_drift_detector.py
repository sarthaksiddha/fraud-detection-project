import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
from scipy import stats
from dataclasses import dataclass
import logging

@dataclass
class DriftMetrics:
    feature_drifts: Dict[str, float]
    overall_drift_score: float
    p_values: Dict[str, float]
    timestamp: datetime

class ModelDriftDetector:
    """Detect data drift in model inputs and predictions."""
    
    def __init__(self, reference_data: pd.DataFrame):
        """Initialize drift detector with reference data.
        
        Args:
            reference_data (pd.DataFrame): Baseline data for drift comparison
        """
        self.reference_data = reference_data
        self.reference_stats = self._calculate_reference_statistics()
        self.logger = logging.getLogger(__name__)
    
    def _calculate_reference_statistics(self) -> Dict[str, Dict[str, float]]:
        """Calculate reference statistics for each feature.
        
        Returns:
            Dict[str, Dict[str, float]]: Statistics for each feature
        """
        stats_dict = {}
        
        for column in self.reference_data.columns:
            stats_dict[column] = {
                'mean': self.reference_data[column].mean(),
                'std': self.reference_data[column].std(),
                'median': self.reference_data[column].median(),
                'q1': self.reference_data[column].quantile(0.25),
                'q3': self.reference_data[column].quantile(0.75)
            }
        
        return stats_dict
    
    def calculate_drift(self, current_data: pd.DataFrame) -> DriftMetrics:
        """Calculate drift metrics between current data and reference data.
        
        Args:
            current_data (pd.DataFrame): Current data to check for drift
            
        Returns:
            DriftMetrics: Calculated drift metrics
        """
        feature_drifts = {}
        p_values = {}
        
        for column in self.reference_data.columns:
            try:
                # Perform Kolmogorov-Smirnov test
                ks_statistic, p_value = stats.ks_2samp(
                    self.reference_data[column],
                    current_data[column]
                )
                
                feature_drifts[column] = ks_statistic
                p_values[column] = p_value
                
            except Exception as e:
                self.logger.error(f"Error calculating drift for {column}: {str(e)}")
                feature_drifts[column] = None
                p_values[column] = None
        
        # Calculate overall drift score
        valid_drifts = [d for d in feature_drifts.values() if d is not None]
        overall_drift = np.mean(valid_drifts) if valid_drifts else 1.0
        
        return DriftMetrics(
            feature_drifts=feature_drifts,
            overall_drift_score=overall_drift,
            p_values=p_values,
            timestamp=datetime.now()
        )
    
    def check_drift_thresholds(self, drift_metrics: DriftMetrics) -> List[str]:
        """Check if drift metrics exceed thresholds.
        
        Args:
            drift_metrics (DriftMetrics): Calculated drift metrics
            
        Returns:
            List[str]: List of alerts for features exceeding thresholds
        """
        alerts = []
        
        # Threshold for significant drift (p-value < 0.05)
        for feature, p_value in drift_metrics.p_values.items():
            if p_value is not None and p_value < 0.05:
                alerts.append(
                    f"Significant drift detected in feature {feature} "
                    f"(p-value: {p_value:.4f})"
                )
        
        # Check overall drift score
        if drift_metrics.overall_drift_score > 0.3:
            alerts.append(
                f"High overall drift score: {drift_metrics.overall_drift_score:.4f}"
            )
        
        return alerts
    
    def update_reference_data(self, new_data: pd.DataFrame):
        """Update reference data with new data.
        
        Args:
            new_data (pd.DataFrame): New data to update reference with
        """
        self.reference_data = pd.concat([self.reference_data, new_data])
        self.reference_stats = self._calculate_reference_statistics()