"""Tradata Performance - High-performance monitoring and optimization toolkit"""

from .monitoring import (
    PerformanceMonitor,
    MetricsCollector,
    HealthChecker,
    get_performance_monitor,
    get_metrics_collector,
    get_health_checker,
)

from .monitoring.event_system import (
    get_event_emitter,
    emit_event,
    emit_function_timing,
    emit_request_metrics,
    emit_cache_operation,
    emit_profiling_result,
    emit_metric_recorded,
    emit_health_check,
    emit_system_metric,
    register_handler,
    register_global_handler,
    PerformanceEventType,
    PerformanceEvent,
    PerformanceEventEmitter,
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
    # Event system
    "get_event_emitter",
    "emit_event",
    "emit_function_timing",
    "emit_request_metrics",
    "emit_cache_operation",
    "emit_profiling_result",
    "emit_metric_recorded",
    "emit_health_check",
    "emit_system_metric",
    "register_handler",
    "register_global_handler",
    "PerformanceEventType",
    "PerformanceEvent",
    "PerformanceEventEmitter",
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
