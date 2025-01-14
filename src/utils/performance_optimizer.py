import psutil
import threading
from typing import Dict, Any
import logging
from dataclasses import dataclass

@dataclass
class ResourceThresholds:
    cpu_threshold: float = 80.0  # percentage
    memory_threshold: float = 85.0  # percentage
    batch_size_min: int = 10
    batch_size_max: int = 1000
    thread_count_min: int = 2
    thread_count_max: int = 16

class PerformanceOptimizer:
    """Optimize system performance based on resource utilization."""
    
    def __init__(self, thresholds: ResourceThresholds):
        """Initialize performance optimizer.
        
        Args:
            thresholds (ResourceThresholds): Resource utilization thresholds
        """
        self.thresholds = thresholds
        self.logger = logging.getLogger(__name__)
        self.current_batch_size = 100
        self.current_thread_count = 4
        
        # Start monitoring thread
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start resource monitoring thread."""
        def monitor():
            while True:
                try:
                    self._optimize_resources()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    self.logger.error(f"Error in resource monitoring: {str(e)}")
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def _optimize_resources(self):
        """Optimize resource utilization."""
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        # Adjust batch size based on resource utilization
        if cpu_percent > self.thresholds.cpu_threshold or \
           memory_percent > self.thresholds.memory_threshold:
            self._decrease_batch_size()
        elif cpu_percent < self.thresholds.cpu_threshold * 0.7 and \
             memory_percent < self.thresholds.memory_threshold * 0.7:
            self._increase_batch_size()
        
        # Adjust thread count
        self._optimize_thread_count(cpu_percent)
    
    def _decrease_batch_size(self):
        """Decrease processing batch size."""
        new_size = max(
            self.thresholds.batch_size_min,
            int(self.current_batch_size * 0.8)
        )
        
        if new_size != self.current_batch_size:
            self.logger.info(
                f"Decreasing batch size from {self.current_batch_size} "
                f"to {new_size}"
            )
            self.current_batch_size = new_size
    
    def _increase_batch_size(self):
        """Increase processing batch size."""
        new_size = min(
            self.thresholds.batch_size_max,
            int(self.current_batch_size * 1.2)
        )
        
        if new_size != self.current_batch_size:
            self.logger.info(
                f"Increasing batch size from {self.current_batch_size} "
                f"to {new_size}"
            )
            self.current_batch_size = new_size
    
    def _optimize_thread_count(self, cpu_percent: float):
        """Optimize number of worker threads.
        
        Args:
            cpu_percent (float): Current CPU utilization
        """
        cpu_count = psutil.cpu_count()
        
        if cpu_percent > self.thresholds.cpu_threshold:
            # Decrease thread count
            new_count = max(
                self.thresholds.thread_count_min,
                min(self.current_thread_count - 1, cpu_count - 1)
            )
        elif cpu_percent < self.thresholds.cpu_threshold * 0.7:
            # Increase thread count
            new_count = min(
                self.thresholds.thread_count_max,
                min(self.current_thread_count + 1, cpu_count)
            )
        else:
            return
        
        if new_count != self.current_thread_count:
            self.logger.info(
                f"Adjusting thread count from {self.current_thread_count} "
                f"to {new_count}"
            )
            self.current_thread_count = new_count
    
    def get_optimal_batch_size(self) -> int:
        """Get current optimal batch size.
        
        Returns:
            int: Optimal batch size
        """
        return self.current_batch_size
    
    def get_optimal_thread_count(self) -> int:
        """Get current optimal thread count.
        
        Returns:
            int: Optimal thread count
        """
        return self.current_thread_count
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get current resource statistics.
        
        Returns:
            Dict[str, Any]: Resource statistics
        """
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'batch_size': self.current_batch_size,
            'thread_count': self.current_thread_count
        }