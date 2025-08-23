"""Tradata Performance - High-performance monitoring and optimization toolkit"""

from .monitoring import (
    PerformanceMonitor,
    MetricsCollector,
    HealthChecker,
    get_performance_monitor,
    get_metrics_collector,
    get_health_checker,
)

from .middleware import (
    PerformanceMonitoringMiddleware,
    RequestTimingMiddleware,
    PerformanceHeadersMiddleware,
    CacheMonitoringMiddleware,
    CacheMetricsMiddleware,
    CacheHealthMiddleware,
)

from .http import OptimizedHTTPClient, get_http_client, close_http_client

from .decorators import (
    timing,
    profile,
    monitor_performance,
    collect_metrics,
    track_calls,
    business_metrics,
    performance_counter,
)

__version__ = "0.1.0"

__all__ = [
    # Core monitoring
    "PerformanceMonitor",
    "MetricsCollector",
    "HealthChecker",
    "get_performance_monitor",
    "get_metrics_collector",
    "get_health_checker",
    # Middleware
    "PerformanceMonitoringMiddleware",
    "RequestTimingMiddleware",
    "PerformanceHeadersMiddleware",
    "CacheMonitoringMiddleware",
    "CacheMetricsMiddleware",
    "CacheHealthMiddleware",
    # HTTP client
    "OptimizedHTTPClient",
    "get_http_client",
    "close_http_client",
    # Decorators
    "timing",
    "profile",
    "monitor_performance",
    "collect_metrics",
    "track_calls",
    "business_metrics",
    "performance_counter",
]
