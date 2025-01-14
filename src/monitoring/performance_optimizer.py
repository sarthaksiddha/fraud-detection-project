from typing import Dict, Any
import psutil
import logging
from dataclasses import dataclass

@dataclass
class ResourceLimits:
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 85.0
    max_disk_percent: float = 90.0
    max_batch_size: int = 1000
    min_batch_size: int = 10

class PerformanceOptimizer:
    """Optimize system performance based on resource usage."""
    
    def __init__(self, resource_limits: ResourceLimits):
        """Initialize performance optimizer.
        
        Args:
            resource_limits (ResourceLimits): Resource usage limits
        """
        self.resource_limits = resource_limits
        self.logger = logging.getLogger(__name__)
        self.current_batch_size = 100  # Default batch size
    
    def optimize_batch_size(self) -> int:
        """Optimize batch size based on current resource usage.
        
        Returns:
            int: Optimized batch size
        """
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        # Decrease batch size if resources are constrained
        if cpu_percent > self.resource_limits.max_cpu_percent or \
           memory_percent > self.resource_limits.max_memory_percent:
            self.current_batch_size = max(
                self.resource_limits.min_batch_size,
                int(self.current_batch_size * 0.8)
            )
            self.logger.info(
                f"Decreased batch size to {self.current_batch_size} due to "
                f"resource constraints (CPU: {cpu_percent}%, Mem: {memory_percent}%)"
            )
        
        # Increase batch size if resources are available
        elif cpu_percent < self.resource_limits.max_cpu_percent * 0.7 and \
             memory_percent < self.resource_limits.max_memory_percent * 0.7:
            self.current_batch_size = min(
                self.resource_limits.max_batch_size,
                int(self.current_batch_size * 1.2)
            )
            self.logger.info(
                f"Increased batch size to {self.current_batch_size} "
                f"(CPU: {cpu_percent}%, Mem: {memory_percent}%)"
            )
        
        return self.current_batch_size
    
    def get_resource_stats(self) -> Dict[str, float]:
        """Get current resource usage statistics.
        
        Returns:
            Dict[str, float]: Resource usage statistics
        """
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'current_batch_size': self.current_batch_size
        }
    
    def optimize_thread_count(self) -> int:
        """Optimize number of worker threads based on CPU cores and usage.
        
        Returns:
            int: Optimized thread count
        """
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent()
        
        if cpu_percent > self.resource_limits.max_cpu_percent:
            return max(1, cpu_count - 2)
        else:
            return cpu_count