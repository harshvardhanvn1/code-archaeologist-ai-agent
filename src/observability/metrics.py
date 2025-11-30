"""Performance metrics collection and reporting."""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import time
import statistics


@dataclass
class MetricPoint:
    """Single metric measurement."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Collects and aggregates performance metrics.
    
    Usage:
        metrics = MetricsCollector()
        metrics.record("agent.execution_time", 1.5, {"agent": "git_analyzer"})
        summary = metrics.get_summary()
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: List[MetricPoint] = []
        self.counters: Dict[str, int] = {}
        self.timers: Dict[str, List[float]] = {}
    
    def record(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for categorization
        """
        metric = MetricPoint(
            name=metric_name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.metrics.append(metric)
    
    def increment(self, counter_name: str, count: int = 1) -> None:
        """
        Increment a counter.
        
        Args:
            counter_name: Name of the counter
            count: Amount to increment (default: 1)
        """
        self.counters[counter_name] = self.counters.get(counter_name, 0) + count
    
    def record_duration(self, timer_name: str, duration: float) -> None:
        """
        Record a duration measurement.
        
        Args:
            timer_name: Name of the timer
            duration: Duration in seconds
        """
        if timer_name not in self.timers:
            self.timers[timer_name] = []
        self.timers[timer_name].append(duration)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all collected metrics.
        
        Returns:
            Dictionary containing metric summaries
        """
        summary = {
            "total_metrics": len(self.metrics),
            "counters": self.counters.copy(),
            "timers": {}
        }
        
        # Aggregate timer statistics
        for timer_name, durations in self.timers.items():
            if durations:
                summary["timers"][timer_name] = {
                    "count": len(durations),
                    "total": sum(durations),
                    "mean": statistics.mean(durations),
                    "median": statistics.median(durations),
                    "min": min(durations),
                    "max": max(durations),
                    "p95": statistics.quantiles(durations, n=20)[18] if len(durations) > 1 else durations[0]
                }
        
        return summary
    
    def get_metrics_by_name(self, metric_name: str) -> List[MetricPoint]:
        """
        Get all metrics with a specific name.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            List of matching metric points
        """
        return [m for m in self.metrics if m.name == metric_name]
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.timers.clear()


class MetricsMixin:
    """
    Mixin class to add metrics collection to agents.
    
    Usage:
        class MyAgent(MetricsMixin):
            def run(self):
                with self.measure_time("agent_run"):
                    # do work
                    pass
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = MetricsCollector()
    
    def measure_time(self, operation_name: str):
        """
        Context manager to measure operation time.
        
        Args:
            operation_name: Name of the operation being measured
            
        Returns:
            Context manager that records duration
        """
        return TimerContext(self.metrics, operation_name)


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, metrics: MetricsCollector, name: str):
        """
        Initialize timer context.
        
        Args:
            metrics: MetricsCollector instance
            name: Name of the operation
        """
        self.metrics = metrics
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record duration."""
        duration = time.time() - self.start_time
        self.metrics.record_duration(self.name, duration)
        
        # Also increment success/error counters
        if exc_type is None:
            self.metrics.increment(f"{self.name}.success")
        else:
            self.metrics.increment(f"{self.name}.error")


# Global metrics instance
_global_metrics = MetricsCollector()


def get_global_metrics() -> MetricsCollector:
    """
    Get the global metrics collector.
    
    Returns:
        Global MetricsCollector instance
    """
    return _global_metrics