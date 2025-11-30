"""Distributed tracing for agent workflow visibility."""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
from typing import Optional, Dict, Any
import functools
import time


# Global tracer provider
_tracer_provider: Optional[TracerProvider] = None
_tracer: Optional[trace.Tracer] = None


def setup_tracing(service_name: str = "code-archaeologist") -> None:
    """
    Initialize distributed tracing.
    
    Args:
        service_name: Name of the service for trace identification
    """
    global _tracer_provider, _tracer
    
    # Create resource with service name
    resource = Resource.create({"service.name": service_name})
    
    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)
    
    # Add console exporter for development
    console_exporter = ConsoleSpanExporter()
    span_processor = SimpleSpanProcessor(console_exporter)
    _tracer_provider.add_span_processor(span_processor)
    
    # Set as global tracer provider
    trace.set_tracer_provider(_tracer_provider)
    
    # Get tracer
    _tracer = trace.get_tracer(__name__)


def get_tracer() -> trace.Tracer:
    """
    Get the global tracer instance.
    
    Returns:
        OpenTelemetry tracer
    """
    global _tracer
    
    if _tracer is None:
        setup_tracing()
    
    return _tracer


def trace_function(span_name: Optional[str] = None):
    """
    Decorator to trace function execution.
    
    Args:
        span_name: Optional custom span name (defaults to function name)
        
    Usage:
        @trace_function("my_operation")
        def my_func():
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            name = span_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(name) as span:
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                # Record start time
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("status", "success")
                    return result
                except Exception as e:
                    span.set_attribute("status", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise
                finally:
                    # Record duration
                    duration = time.time() - start_time
                    span.set_attribute("duration_ms", duration * 1000)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            name = span_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(name) as span:
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                # Record start time
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("status", "success")
                    return result
                except Exception as e:
                    span.set_attribute("status", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise
                finally:
                    # Record duration
                    duration = time.time() - start_time
                    span.set_attribute("duration_ms", duration * 1000)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class TracerMixin:
    """
    Mixin class to add tracing capabilities to agents.
    
    Usage:
        class MyAgent(TracerMixin):
            def run(self):
                with self.start_span("agent_run"):
                    # do work
                    pass
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracer = get_tracer()
    
    def start_span(self, span_name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Start a new tracing span.
        
        Args:
            span_name: Name of the span
            attributes: Optional attributes to add to span
            
        Returns:
            Context manager for the span
        """
        span = self.tracer.start_as_current_span(span_name)
        
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        
        return span


# Initialize tracing on module import
setup_tracing()