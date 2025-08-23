"""
Simple logging implementation for tradata_perf package.
Provides basic logging functionality to replace the missing tradata_logger dependency.
"""

import logging
import uuid
from typing import Optional, Any, Dict
from contextvars import ContextVar

# Context variables for trace ID and client info
_trace_id: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
_client_info: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "client_info", default=None
)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: The name of the logger (usually __name__)

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)

    # Configure logger if it hasn't been configured yet
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def set_trace_id(trace_id: str) -> None:
    """
    Set the current trace ID for logging context.

    Args:
        trace_id: The trace ID to set
    """
    _trace_id.set(trace_id)


def get_trace_id() -> Optional[str]:
    """
    Get the current trace ID.

    Returns:
        The current trace ID or None if not set
    """
    return _trace_id.get()


def set_client(client_info: Dict[str, Any]) -> None:
    """
    Set client information for logging context.

    Args:
        client_info: Dictionary containing client information
    """
    _client_info.set(client_info)


def get_client() -> Optional[Dict[str, Any]]:
    """
    Get the current client information.

    Returns:
        The current client information or None if not set
    """
    return _client_info.get()


def generate_trace_id() -> str:
    """
    Generate a new trace ID.

    Returns:
        A new unique trace ID
    """
    return str(uuid.uuid4())


# Create a default logger for the package
default_logger = get_logger(__name__)
