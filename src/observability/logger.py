"""Structured logging with correlation IDs for agent tracing."""
import structlog
import logging
import sys
from typing import Optional
import uuid
from datetime import datetime


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str, correlation_id: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a logger instance with optional correlation ID.
    
    Args:
        name: Logger name (usually __name__)
        correlation_id: Optional correlation ID for request tracking
        
    Returns:
        Configured structlog logger
    """
    logger = structlog.get_logger(name)
    
    if correlation_id:
        logger = logger.bind(correlation_id=correlation_id)
    
    return logger


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID for tracking requests.
    
    Returns:
        UUID-based correlation ID
    """
    return f"req_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}"


class LoggerMixin:
    """
    Mixin class to add logging capabilities to agents.
    
    Usage:
        class MyAgent(LoggerMixin):
            def __init__(self):
                super().__init__()
                self.logger.info("Agent initialized")
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._correlation_id = generate_correlation_id()
        self.logger = get_logger(
            self.__class__.__name__,
            correlation_id=self._correlation_id
        )
    
    @property
    def correlation_id(self) -> str:
        """Get the correlation ID for this instance."""
        return self._correlation_id


# Initialize logging on module import
setup_logging()