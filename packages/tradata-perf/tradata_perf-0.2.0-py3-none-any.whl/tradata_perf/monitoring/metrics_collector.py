"""
Metrics collection functionality for performance monitoring.
Provides utilities for collecting request, cache, API, and custom business metrics.
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import statistics
from .event_system import emit_system_metric


@dataclass
class MetricPoint:
    """Individual metric data point"""

    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """Series of metric data points"""

    name: str
    points: deque = field(default_factory=lambda: deque(maxlen=1000))
    tags: Dict[str, str] = field(default_factory=dict)

    def add_point(
        self,
        value: float,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Add a new metric point"""
        if timestamp is None:
            timestamp = datetime.now()
        if metadata is None:
            metadata = {}

        point = MetricPoint(
            name=self.name,
            value=value,
            timestamp=timestamp,
            tags=self.tags,
            metadata=metadata,
        )
        self.points.append(point)

    def get_latest(self, count: int = 100) -> List[MetricPoint]:
        """Get the latest N metric points"""
        return list(self.points)[-count:]

    def get_statistics(self, window_minutes: int = 60) -> Dict[str, float]:
        """Get statistics for the specified time window"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=window_minutes)

        # Filter points within the time window
        recent_points = [point for point in self.points if point.timestamp >= cutoff]

        if not recent_points:
            return {
                "count": 0,
                "min": 0.0,
                "max": 0.0,
                "avg": 0.0,
                "p95": 0.0,
                "p99": 0.0,
            }

        values = [point.value for point in recent_points]
        values.sort()

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "p95": (
                statistics.quantiles(values, n=20)[18]
                if len(values) >= 20
                else values[-1]
            ),
            "p99": (
                statistics.quantiles(values, n=100)[98]
                if len(values) >= 100
                else values[-1]
            ),
        }


class MetricsCollector:
    """Central metrics collection system"""

    def __init__(self, max_series: int = 1000):
        self.max_series = max_series
        self.metric_series: Dict[str, MetricSeries] = {}
        self._lock = asyncio.Lock()

        # Note: logger.info is async but we can't await in __init__
        pass

    async def collect_request_metrics(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        cache_hit: bool = False,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """Collect request performance metrics"""
        async with self._lock:
            # Response time metric
            await self._ensure_metric_series(
                "request_response_time", {"endpoint": endpoint, "method": method}
            )
            self.metric_series["request_response_time"].add_point(
                value=response_time,
                metadata={
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": status_code,
                    "cache_hit": cache_hit,
                    "user_agent": user_agent,
                    "ip_address": ip_address,
                },
            )

            # Status code counter
            await self._ensure_metric_series(
                "request_status_codes", {"endpoint": endpoint, "method": method}
            )
            self.metric_series["request_status_codes"].add_point(
                value=1.0,  # Count metric
                metadata={
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": status_code,
                    "cache_hit": cache_hit,
                },
            )

            # Cache hit rate
            if cache_hit is not None:
                await self._ensure_metric_series(
                    "cache_hit_rate", {"endpoint": endpoint}
                )
                self.metric_series["cache_hit_rate"].add_point(
                    value=1.0 if cache_hit else 0.0, metadata={"endpoint": endpoint}
                )

    async def collect_cache_metrics(
        self,
        cache_operation: str,
        cache_name: str,
        hit: bool,
        duration: float,
        key_size: Optional[int] = None,
        value_size: Optional[int] = None,
    ) -> None:
        """Collect cache performance metrics"""
        async with self._lock:
            # Cache operation duration
            await self._ensure_metric_series(
                "cache_operation_duration",
                {"operation": cache_operation, "cache": cache_name},
            )
            self.metric_series["cache_operation_duration"].add_point(
                value=duration,
                metadata={
                    "operation": cache_operation,
                    "cache": cache_name,
                    "hit": hit,
                    "key_size": key_size,
                    "value_size": value_size,
                },
            )

            # Cache hit rate
            await self._ensure_metric_series("cache_hit_rate", {"cache": cache_name})
            self.metric_series["cache_hit_rate"].add_point(
                value=1.0 if hit else 0.0, metadata={"cache": cache_name}
            )

            # Cache operation count
            await self._ensure_metric_series(
                "cache_operation_count",
                {"operation": cache_operation, "cache": cache_name},
            )
            self.metric_series["cache_operation_count"].add_point(
                value=1.0,
                metadata={
                    "operation": cache_operation,
                    "cache": cache_name,
                    "hit": hit,
                },
            )

    async def collect_custom_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Collect custom business metrics"""
        async with self._lock:
            await self._ensure_metric_series(name, tags or {})
            self.metric_series[name].add_point(value=value, metadata=metadata or {})

    async def collect_api_call_metrics(
        self,
        api_name: str,
        endpoint: str,
        duration: float,
        success: bool,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Collect external API call metrics"""
        async with self._lock:
            # API call duration
            await self._ensure_metric_series(
                "api_call_duration", {"api": api_name, "endpoint": endpoint}
            )
            self.metric_series["api_call_duration"].add_point(
                value=duration,
                metadata={
                    "api": api_name,
                    "endpoint": endpoint,
                    "success": success,
                    "status_code": status_code,
                    "error_message": error_message,
                },
            )

            # API call success rate
            await self._ensure_metric_series(
                "api_call_success_rate", {"api": api_name, "endpoint": endpoint}
            )
            self.metric_series["api_call_success_rate"].add_point(
                value=1.0 if success else 0.0,
                metadata={"api": api_name, "endpoint": endpoint},
            )

    async def _ensure_metric_series(self, name: str, tags: Dict[str, str]) -> None:
        """Ensure a metric series exists, create if it doesn't"""
        if name not in self.metric_series:
            if len(self.metric_series) >= self.max_series:
                # Remove oldest series if we're at capacity
                oldest_name = next(iter(self.metric_series))
                del self.metric_series[oldest_name]
                # Emit metric cleanup event
                emit_system_metric(
                    metric_name="metric_series_removed",
                    value=1.0,
                    unit="count",
                    metadata={
                        "removed_series": oldest_name,
                        "reason": "capacity_limit",
                    },
                )

            self.metric_series[name] = MetricSeries(name=name, tags=tags)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics with statistics"""
        result = {}

        for name, series in self.metric_series.items():
            result[name] = {
                "tags": series.tags,
                "statistics": series.get_statistics(),
                "latest_points": len(series.points),
            }

        return result

    def get_metric_series(self, name: str) -> Optional[MetricSeries]:
        """Get a specific metric series by name"""
        return self.metric_series.get(name)

    def get_metric_statistics(
        self, name: str, window_minutes: int = 60
    ) -> Optional[Dict[str, float]]:
        """Get statistics for a specific metric series"""
        series = self.metric_series.get(name)
        if series:
            return series.get_statistics(window_minutes)
        return None

    async def clear_old_metrics(self, older_than_hours: int = 24) -> int:
        """Clear metrics older than specified hours, return count of cleared points"""
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        cleared_count = 0

        async with self._lock:
            for series in self.metric_series.values():
                # Remove old points
                original_count = len(series.points)
                series.points = deque(
                    (point for point in series.points if point.timestamp >= cutoff),
                    maxlen=series.points.maxlen,
                )
                cleared_count += original_count - len(series.points)

        # Emit metric cleanup event
        emit_system_metric(
            metric_name="metrics_cleaned",
            value=float(cleared_count),
            unit="count",
            metadata={
                "operation": "cleanup",
                "step": "metrics",
                "older_than_hours": older_than_hours,
                "cleared_count": cleared_count,
            },
        )

        return cleared_count


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
