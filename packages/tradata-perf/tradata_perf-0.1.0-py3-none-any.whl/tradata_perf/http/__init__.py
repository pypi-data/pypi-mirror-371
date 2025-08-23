"""
High-performance HTTP client module.
"""

from .optimized_client import OptimizedHTTPClient, get_http_client, close_http_client

__all__ = ["OptimizedHTTPClient", "get_http_client", "close_http_client"]
