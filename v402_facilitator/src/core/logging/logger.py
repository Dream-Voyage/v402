"""
Centralized logging configuration for v402 Facilitator.

Provides structured logging with multiple handlers, log rotation,
and different log levels for different environments.
"""

import logging
import sys
from core.config import get_settings
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

settings = get_settings()


def setup_logging(log_level: str = "INFO", log_format: Optional[str] = None) -> None:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format. If None, uses default structured format.
    """
    # Default structured log format
    default_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(funcName)s:%(lineno)d | %(message)s"
    )
    log_format = log_format or default_format

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler for production (with rotation)
    if settings.monitoring.LOG_FILE:
        log_dir = Path(settings.monitoring.LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = TimedRotatingFileHandler(
            log_dir / settings.monitoring.LOG_FILE,
            when='midnight',
            interval=1,
            backupCount=settings.monitoring.LOG_RETENTION_DAYS,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # Error file handler
        error_file_handler = TimedRotatingFileHandler(
            log_dir / "error.log",
            when='midnight',
            interval=1,
            backupCount=settings.monitoring.LOG_RETENTION_DAYS,
            encoding='utf-8'
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

