"""
Structured logging configuration for BudgetBliss.

Replaces ad-hoc print() statements with a proper logging setup
that includes timestamps, log levels, and module context.
"""

import logging
import sys


def setup_logging(log_level='INFO'):
    """
    Configure the root logger with a consistent format.

    Args:
        log_level: Minimum log level to capture (DEBUG, INFO, WARNING, ERROR).
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Avoid adding duplicate handlers on re-initialization
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
