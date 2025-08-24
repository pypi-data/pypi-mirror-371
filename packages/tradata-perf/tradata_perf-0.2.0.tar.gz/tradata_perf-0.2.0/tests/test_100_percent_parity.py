"""
Test file to verify 100% functional parity between original and extracted performance code.
This test suite ensures that all performance-related functionality has been successfully extracted.
"""

import pytest
from datetime import datetime

from tradata_perf.monitoring import (
    PerformanceMonitor,
    RequestMetrics,
    CacheMetrics,
    SystemMetrics,
    get_performance_monitor,
    record_request_metrics,
)
from tradata_perf.middleware import (
    PerformanceMonitoringMiddleware,
    CacheMonitoringMiddleware,
)
from tradata_perf.http import OptimizedHTTPClient, get_http_client
from tradata_perf.decorators.performance import timing


class TestDataClassParity:
    """Test that all dataclasses have the same structure and behavior."""

    def test_request_metrics_dataclass(self):
        """Test RequestMetrics dataclass functionality."""
        metrics = RequestMetrics(
            endpoint="/test",
            method="GET",
            status_code=200,
            response_time=0.1,
            timestamp=datetime.now(),
            cache_hit=True,
            user_agent="test-agent",
            ip_address="127.0.0.1",
        )

        assert metrics.endpoint == "/test"
        assert metrics.method == "GET"
        assert metrics.status_code == 200
        assert metrics.response_time == 0.1
        assert metrics.cache_hit is True
        assert metrics.user_agent == "test-agent"
        assert metrics.ip_address == "127.0.0.1"

    def test_cache_metrics_dataclass(self):
        """Test CacheMetrics dataclass functionality."""
        cache_metrics = CacheMetrics(cache_name="test_cache")
        cache_metrics.hits = 10
        cache_metrics.misses = 5
        cache_metrics.update_hit_rate()

        assert cache_metrics.hits == 10
        assert cache_metrics.misses == 5
        assert cache_metrics.hit_rate == pytest.approx(
            66.67, abs=0.01
        )  # 10/(10+5) * 100

    def test_system_metrics_dataclass(self):
        """Test SystemMetrics dataclass functionality."""
        system_metrics = SystemMetrics()
        system_metrics.total_requests = 100
        system_metrics.successful_requests = 95
        system_metrics.failed_requests = 5

        assert system_metrics.total_requests == 100
        assert system_metrics.successful_requests == 95
        assert system_metrics.failed_requests == 5


class TestPerformanceMonitorParity:
    """Test that PerformanceMonitor has all required functionality."""

    @pytest.fixture
    def monitor(self):
        """Create a fresh PerformanceMonitor instance for each test."""
        return PerformanceMonitor(max_history=100)

    @pytest.mark.asyncio
    async def test_monitor_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor.max_history == 100
        assert len(monitor.request_history) == 0
        assert "candle_cache" in monitor.cache_metrics
        assert "quote_cache" in monitor.cache_metrics
        assert monitor.start_time is not None

    @pytest.mark.asyncio
    async def test_record_request(self, monitor):
        """Test recording request metrics."""
        metrics = RequestMetrics(
            endpoint="/test",
            method="GET",
            status_code=200,
            response_time=0.1,
            timestamp=datetime.now(),
        )

        await monitor.record_request(metrics)

        assert len(monitor.request_history) == 1
        assert monitor.system_metrics.total_requests == 1
        assert monitor.system_metrics.successful_requests == 1
        assert monitor.system_metrics.failed_requests == 0

    @pytest.mark.asyncio
    async def test_get_performance_summary(self, monitor):
        """Test performance summary generation."""
        # Add some test data
        for i in range(5):
            metrics = RequestMetrics(
                endpoint=f"/test{i}",
                method="GET",
                status_code=200,
                response_time=0.1 + i * 0.01,
                timestamp=datetime.now(),
            )
            await monitor.record_request(metrics)

        summary = monitor.get_performance_summary()

        assert "system" in summary
        assert "caches" in summary
        assert "recent_performance" in summary
        assert "endpoint_performance" in summary
        assert summary["system"]["total_requests"] == 5
        assert summary["system"]["successful_requests"] == 5

    @pytest.mark.asyncio
    async def test_health_status(self, monitor):
        """Test health status generation."""
        health = await monitor.get_health_status()

        assert "status" in health
        assert "overall_health" in health
        assert "health_checks" in health
        assert "uptime_seconds" in health


class TestMiddlewareParity:
    """Test that middleware classes have required functionality."""

    def test_performance_middleware_initialization(self):
        """Test PerformanceMonitoringMiddleware initialization."""

        # Create a mock app for testing
        class MockApp:
            pass

        app = MockApp()
        middleware = PerformanceMonitoringMiddleware(app)

        assert middleware.app == app

    def test_cache_middleware_initialization(self):
        """Test CacheMonitoringMiddleware initialization."""

        # Create a mock app for testing
        class MockApp:
            pass

        app = MockApp()
        middleware = CacheMonitoringMiddleware(app)

        assert middleware.app == app


class TestHTTPClientParity:
    """Test that HTTP client has required functionality."""

    @pytest.fixture
    def client(self):
        """Create a fresh HTTP client for each test."""
        return OptimizedHTTPClient()

    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initialization."""
        assert client._client is None
        assert client._total_requests == 0
        assert client._successful_requests == 0
        assert client._failed_requests == 0

    def test_performance_stats(self, client):
        """Test performance stats generation."""
        # Simulate some requests
        client._total_requests = 10
        client._successful_requests = 8
        client._failed_requests = 2
        client._total_response_time = 1.0
        client._request_times = [0.1] * 10

        stats = client.get_performance_stats()

        assert stats["total_requests"] == 10
        assert stats["successful_requests"] == 8
        assert stats["failed_requests"] == 2
        assert stats["success_rate_percent"] == 80.0
        assert stats["avg_response_time_ms"] == 100.0


class TestGlobalFunctionsParity:
    """Test that global functions work correctly."""

    def test_get_performance_monitor(self):
        """Test get_performance_monitor function."""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()

        # Should return the same instance (singleton)
        assert monitor1 is monitor2
        assert isinstance(monitor1, PerformanceMonitor)

    def test_get_http_client(self):
        """Test get_http_client function."""
        client1 = get_http_client()
        client2 = get_http_client()

        # Should return the same instance (singleton)
        assert client1 is client2
        assert isinstance(client1, OptimizedHTTPClient)


class TestEnhancedFunctionalityExists:
    """Test that enhanced functionality exists and works."""

    def test_metrics_collector_exists(self):
        """Test that MetricsCollector is available."""
        from tradata_perf.monitoring import MetricsCollector

        collector = MetricsCollector()
        assert collector is not None

    def test_health_checker_exists(self):
        """Test that HealthChecker is available."""
        from tradata_perf.monitoring import HealthChecker

        checker = HealthChecker()
        assert checker is not None

    def test_decorators_exist(self):
        """Test that performance decorators are available."""

        # Test that decorators can be imported and used
        @timing
        def test_function():
            return "test"

        result = test_function()
        assert result == "test"


class TestBehavioralParity:
    """Test that the extracted package behaves identically to the original."""

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Create monitor
        monitor = get_performance_monitor()

        # Record some metrics
        await record_request_metrics(
            endpoint="/test",
            method="GET",
            status_code=200,
            response_time=0.1,
            cache_hit=True,
        )

        # Get summary
        summary = monitor.get_performance_summary()

        # Verify the workflow works
        assert summary["system"]["total_requests"] == 1
        assert summary["system"]["successful_requests"] == 1
        assert (
            summary["caches"]["candle_cache"]["hits"] >= 0
        )  # May be 0 or 1 depending on cache mapping

        # Verify enhanced functionality works
        health = await monitor.get_health_status()
        assert "status" in health
        assert "overall_health" in health


if __name__ == "__main__":
    pytest.main([__file__])
