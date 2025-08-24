"""
Basic import tests for tradata_perf package.
"""

import pytest
from tradata_perf import (
    PerformanceMonitor,
    MetricsCollector,
    HealthChecker,
    get_performance_monitor,
    get_metrics_collector,
    get_health_checker,
)

from tradata_perf.middleware import (
    PerformanceMonitoringMiddleware,
    CacheMonitoringMiddleware,
)

from tradata_perf.http import OptimizedHTTPClient, get_http_client

from tradata_perf.decorators import (
    timing,
    profile,
    monitor_performance,
    collect_metrics,
    track_calls,
)


def test_monitoring_imports():
    """Test that monitoring components can be imported."""
    assert PerformanceMonitor is not None
    assert MetricsCollector is not None
    assert HealthChecker is not None
    assert get_performance_monitor is not None
    assert get_metrics_collector is not None
    assert get_health_checker is not None


def test_middleware_imports():
    """Test that middleware components can be imported."""
    assert PerformanceMonitoringMiddleware is not None
    assert CacheMonitoringMiddleware is not None


def test_http_imports():
    """Test that HTTP components can be imported."""
    assert OptimizedHTTPClient is not None
    assert get_http_client is not None


def test_decorator_imports():
    """Test that decorators can be imported."""
    assert timing is not None
    assert profile is not None
    assert monitor_performance is not None
    assert collect_metrics is not None
    assert track_calls is not None


def test_package_version():
    """Test that package version is accessible."""
    from tradata_perf import __version__

    assert __version__ == "0.1.0"


if __name__ == "__main__":
    pytest.main([__file__])
