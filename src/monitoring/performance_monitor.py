from typing import Dict, Any, List, Optional
import time
import logging
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    latency_p50: float
    latency_p90: float
    latency_p99: float
    throughput: float
    error_rate: float
    resource_utilization: Dict[str, float]
    timestamp: datetime

class PerformanceMonitor:
    """Monitor and optimize system performance."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize performance monitor.
        
        Args:
            config (Dict[str, Any]): Monitor configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.latencies: List[float] = []
        self.errors: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
        # Performance thresholds
        self.thresholds = config.get('thresholds', {
            'max_latency_p99': 1.0,  # seconds
            'max_error_rate': 0.01,   # 1%
            'max_cpu_usage': 80.0,    # percentage
            'max_memory_usage': 85.0  # percentage
        })
    
    def record_request(self, latency: float, error: Optional[str] = None):
        """Record a request's performance metrics.
        
        Args:
            latency (float): Request latency in seconds
            error (Optional[str]): Error message if request failed
        """
        self.latencies.append(latency)
        
        if error:
            self.errors.append({
                'error': error,
                'timestamp': datetime.utcnow()
            })
            
        # Clean up old data
        self._cleanup_old_data()
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics.
        
        Returns:
            PerformanceMetrics: Current performance metrics
        """
        try:
            recent_latencies = self._get_recent_latencies()
            recent_errors = self._get_recent_errors()
            
            return PerformanceMetrics(
                latency_p50=np.percentile(recent_latencies, 50) 
                    if recent_latencies else 0.0,
                latency_p90=np.percentile(recent_latencies, 90) 
                    if recent_latencies else 0.0,
                latency_p99=np.percentile(recent_latencies, 99) 
                    if recent_latencies else 0.0,
                throughput=self._calculate_throughput(),
                error_rate=len(recent_errors) / len(recent_latencies) 
                    if recent_latencies else 0.0,
                resource_utilization=self._get_resource_utilization(),
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {str(e)}")
            raise
    
    def check_performance(self) -> Dict[str, Any]:
        """Check if performance meets thresholds.
        
        Returns:
            Dict[str, Any]: Performance check results
        """
        metrics = self.get_current_metrics()
        issues = []
        
        # Check latency
        if metrics.latency_p99 > self.thresholds['max_latency_p99']:
            issues.append({
                'type': 'high_latency',
                'value': metrics.latency_p99,
                'threshold': self.thresholds['max_latency_p99']
            })
        
        # Check error rate
        if metrics.error_rate > self.thresholds['max_error_rate']:
            issues.append({
                'type': 'high_error_rate',
                'value': metrics.error_rate,
                'threshold': self.thresholds['max_error_rate']
            })
        
        # Check resource utilization
        for resource, usage in metrics.resource_utilization.items():
            threshold_key = f'max_{resource}_usage'
            if threshold_key in self.thresholds and \
               usage > self.thresholds[threshold_key]:
                issues.append({
                    'type': f'high_{resource}_usage',
                    'value': usage,
                    'threshold': self.thresholds[threshold_key]
                })
        
        return {
            'status': 'healthy' if not issues else 'degraded',
            'issues': issues,
            'metrics': metrics.__dict__,
            'timestamp': datetime.utcnow()
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report.
        
        Returns:
            Dict[str, Any]: Performance report
        """
        metrics = self.get_current_metrics()
        
        return {
            'summary': {
                'status': 'healthy' if metrics.error_rate < 
                    self.thresholds['max_error_rate'] else 'degraded',
                'latency_p99': metrics.latency_p99,
                'error_rate': metrics.error_rate,
                'throughput': metrics.throughput
            },
            'latency_distribution': {
                'p50': metrics.latency_p50,
                'p90': metrics.latency_p90,
                'p99': metrics.latency_p99
            },
            'resource_utilization': metrics.resource_utilization,
            'recent_errors': self._get_recent_errors(),
            'timestamp': datetime.utcnow()
        }
    
    def _get_recent_latencies(self, minutes: int = 5) -> List[float]:
        """Get latencies from recent timeframe.
        
        Args:
            minutes (int): Minutes of data to include
            
        Returns:
            List[float]: Recent latencies
        """
        cutoff_time = time.time() - (minutes * 60)
        return [l for l, t in zip(self.latencies, self.timestamps) 
                if t > cutoff_time]
    
    def _get_recent_errors(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get errors from recent timeframe.
        
        Args:
            minutes (int): Minutes of data to include
            
        Returns:
            List[Dict[str, Any]]: Recent errors
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [e for e in self.errors 
                if e['timestamp'] > cutoff_time]
    
    def _calculate_throughput(self, minutes: int = 1) -> float:
        """Calculate recent throughput.
        
        Args:
            minutes (int): Minutes to calculate throughput over
            
        Returns:
            float: Requests per second
        """
        recent_latencies = self._get_recent_latencies(minutes)
        return len(recent_latencies) / (minutes * 60) if recent_latencies else 0.0
    
    def _get_resource_utilization(self) -> Dict[str, float]:
        """Get current resource utilization.
        
        Returns:
            Dict[str, float]: Resource utilization metrics
        """
        # Implement resource utilization monitoring
        return {
            'cpu': 0.0,
            'memory': 0.0,
            'disk': 0.0
        }
    
    def _cleanup_old_data(self):
        """Clean up old performance data."""
        retention_minutes = self.config.get('data_retention_minutes', 60)
        cutoff_time = time.time() - (retention_minutes * 60)
        
        self.latencies = [l for l, t in zip(self.latencies, self.timestamps) 
                         if t > cutoff_time]
        self.timestamps = [t for t in self.timestamps if t > cutoff_time]
        
        cutoff_datetime = datetime.utcnow() - \
            timedelta(minutes=retention_minutes)
        self.errors = [e for e in self.errors 
                      if e['timestamp'] > cutoff_datetime]