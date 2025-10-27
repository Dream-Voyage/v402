"""
Structured logging for v402 client.

This module provides comprehensive logging with structured output,
context tracking, and performance monitoring.
"""

import json
import logging
import logging.handlers
import os
import structlog
import sys
import time
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class V402JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for v402 client logs.

    Provides structured logging with contextual information,
    performance metrics, and correlation IDs.
    """

    def __init__(self):
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""

        # Base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add process and thread info
        log_entry.update({
            "process_id": os.getpid(),
            "thread_id": record.thread,
            "thread_name": record.threadName,
        })

        # Add context variables
        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id

        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_entry["correlation_id"] = correlation_id

        # Add extra fields from log record
        if hasattr(record, "extra") and record.extra:
            log_entry["extra"] = record.extra

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add stack info if present
        if record.stack_info:
            log_entry["stack_info"] = record.stack_info

        return json.dumps(log_entry, default=str)


class V402TextFormatter(logging.Formatter):
    """
    Human-readable text formatter for v402 client logs.

    Provides colored output for development and debugging.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
        "RESET": "\033[0m",     # Reset
    }

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and hasattr(sys.stderr, "isatty") and sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as human-readable text."""

        # Color prefix
        color = ""
        reset = ""
        if self.use_colors:
            color = self.COLORS.get(record.levelname, "")
            reset = self.COLORS["RESET"]

        # Build message
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        message_parts = [
            f"{color}[{timestamp}]",
            f"[{record.levelname:8}]",
            f"[{record.name}]",
            f"{record.getMessage()}{reset}"
        ]

        # Add context if present
        request_id = request_id_var.get()
        if request_id:
            message_parts.insert(-1, f"[req:{request_id[:8]}]")

        # Add extra fields
        if hasattr(record, "extra") and record.extra:
            extra_str = " ".join([f"{k}={v}" for k, v in record.extra.items()])
            message_parts.append(f"({extra_str})")

        base_message = " ".join(message_parts)

        # Add exception info if present
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            base_message += "\n" + exc_text

        return base_message


class V402LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter that adds contextual information.

    Automatically includes request context, performance metrics,
    and v402-specific metadata in log records.
    """

    def process(self, msg: Any, kwargs: Dict[str, Any]) -> tuple[Any, Dict[str, Any]]:
        """Process log message and add contextual information."""

        # Get extra data
        extra = kwargs.get("extra", {})

        # Add v402 context
        extra.update({
            "service": "v402-client",
            "version": "1.0.0",
        })

        # Add timing information if available
        if hasattr(self.extra, "start_time"):
            duration = time.time() - self.extra["start_time"]
            extra["duration_ms"] = round(duration * 1000, 2)

        kwargs["extra"] = extra
        return msg, kwargs


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    output: str = "stdout",
    file_path: Optional[str] = None,
    max_file_size: int = 10485760,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Setup structured logging for v402 client.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type ("json" or "text")
        output: Output destination ("stdout", "stderr", or "file")
        file_path: File path for file output
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup files to keep
    """

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if format_type == "text" else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Setup standard logging
    root_logger = logging.getLogger("v402_client")
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    if format_type == "json":
        formatter = V402JsonFormatter()
    else:
        formatter = V402TextFormatter()

    # Create handler based on output
    if output == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    elif output == "stderr":
        handler = logging.StreamHandler(sys.stderr)
    elif output == "file":
        if not file_path:
            file_path = "v402_client.log"

        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # Use rotating file handler
        handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=max_file_size,
            backupCount=backup_count,
        )
    else:
        raise ValueError(f"Unknown output type: {output}")

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Suppress verbose logs from dependencies
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str, **extra: Any) -> V402LoggerAdapter:
    """
    Get a v402 logger with contextual information.

    Args:
        name: Logger name (usually __name__)
        **extra: Additional context to include in all log messages

    Returns:
        Configured logger adapter
    """
    logger = logging.getLogger(name)
    return V402LoggerAdapter(logger, extra)


def set_request_context(request_id: str, correlation_id: Optional[str] = None) -> None:
    """
    Set request context for logging.

    Args:
        request_id: Unique request identifier
        correlation_id: Optional correlation ID for tracing
    """
    request_id_var.set(request_id)
    if correlation_id:
        correlation_id_var.set(correlation_id)


def clear_request_context() -> None:
    """Clear request context."""
    request_id_var.set(None)
    correlation_id_var.set(None)


class LogContext:
    """
    Context manager for request-scoped logging.

    Automatically sets and clears request context for structured logging.

    Example:
        >>> with LogContext("req-123", "corr-456"):
        ...     logger.info("Processing request")  # Will include IDs
    """

    def __init__(self, request_id: str, correlation_id: Optional[str] = None):
        self.request_id = request_id
        self.correlation_id = correlation_id
        self.previous_request_id = None
        self.previous_correlation_id = None

    def __enter__(self):
        # Save previous context
        self.previous_request_id = request_id_var.get()
        self.previous_correlation_id = correlation_id_var.get()

        # Set new context
        set_request_context(self.request_id, self.correlation_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous context
        request_id_var.set(self.previous_request_id)
        correlation_id_var.set(self.previous_correlation_id)


def timed_operation(operation_name: str):
    """
    Decorator to log operation timing.

    Args:
        operation_name: Name of the operation being timed

    Example:
        >>> @timed_operation("payment_processing")
        ... def process_payment():
        ...     # processing logic
        ...     pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            start_time = time.time()

            try:
                logger.info(
                    f"Starting {operation_name}",
                    extra={"operation": operation_name}
                )

                result = func(*args, **kwargs)

                duration = time.time() - start_time
                logger.info(
                    f"Completed {operation_name}",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration * 1000, 2),
                        "success": True,
                    }
                )

                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Failed {operation_name}",
                    extra={
                        "operation": operation_name,
                        "duration_ms": round(duration * 1000, 2),
                        "success": False,
                        "error": str(e),
                    },
                    exc_info=True
                )
                raise

        return wrapper
    return decorator
