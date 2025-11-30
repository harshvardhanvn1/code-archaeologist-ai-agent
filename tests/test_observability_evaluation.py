"""Test observability and evaluation modules."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from observability.logger import get_logger, generate_correlation_id, setup_logging
from observability.tracer import get_tracer, trace_function
from observability.metrics import MetricsCollector, get_global_metrics
from evaluation.llm_judge import LLMJudge
from evaluation.metrics import EvaluationMetrics, MetricsAggregator
import time
from datetime import datetime


def test_logger():
    """Test structured logging."""
    setup_logging("INFO")
    logger = get_logger("test_logger")
    
    correlation_id = generate_correlation_id()
    assert correlation_id.startswith("req_")
    
    logger.info("Test log message", test_key="test_value")
    print("✓ Logger test passed")


def test_tracer():
    """Test distributed tracing."""
    tracer = get_tracer()
    assert tracer is not None
    
    with tracer.start_as_current_span("test_span") as span:
        span.set_attribute("test_attr", "test_value")
    
    print("✓ Tracer test passed")


def test_trace_decorator():
    """Test trace decorator."""
    @trace_function("test_operation")
    def sample_function():
        time.sleep(0.1)
        return "success"
    
    result = sample_function()
    assert result == "success"
    print("✓ Trace decorator test passed")


def test_metrics_collector():
    """Test metrics collection."""
    metrics = MetricsCollector()
    
    metrics.record("test_metric", 42.5, {"tag": "test"})
    metrics.increment("test_counter", 5)
    metrics.record_duration("test_operation", 1.5)
    
    summary = metrics.get_summary()
    assert summary["total_metrics"] == 1
    assert summary["counters"]["test_counter"] == 5
    assert "test_operation" in summary["timers"]
    
    print("✓ Metrics collector test passed")


def test_evaluation_metrics():
    """Test evaluation metrics."""
    metrics = EvaluationMetrics(
        analysis_id="test_001",
        timestamp=datetime.now(),
        overall_quality=85.0,
        completeness=90.0,
        accuracy=80.0
    )
    
    metrics_dict = metrics.to_dict()
    assert metrics_dict["analysis_id"] == "test_001"
    assert metrics_dict["quality"]["overall"] == 85.0
    
    print("✓ Evaluation metrics test passed")


def test_metrics_aggregator():
    """Test metrics aggregation."""
    aggregator = MetricsAggregator()
    
    metrics1 = EvaluationMetrics(
        analysis_id="test_001",
        timestamp=datetime.now(),
        overall_quality=85.0,
        total_duration=5.0
    )
    
    metrics2 = EvaluationMetrics(
        analysis_id="test_002",
        timestamp=datetime.now(),
        overall_quality=90.0,
        total_duration=3.0
    )
    
    aggregator.add_metrics(metrics1)
    aggregator.add_metrics(metrics2)
    
    avg_quality = aggregator.get_average_quality()
    assert avg_quality == 87.5
    
    summary = aggregator.get_summary()
    assert summary["total_analyses"] == 2
    
    print("✓ Metrics aggregator test passed")


if __name__ == "__main__":
    print("\nTesting Observability & Evaluation Modules...\n")
    
    test_logger()
    test_tracer()
    test_trace_decorator()
    test_metrics_collector()
    test_evaluation_metrics()
    test_metrics_aggregator()
    
    print("\n✓ All tests passed!\n")