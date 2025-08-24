"""
Cache performance monitoring middleware for FastAPI applications.
Tracks cache hit rates, operation durations, and cache health metrics.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..monitoring.event_system import emit_function_timing


class CacheMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring cache performance and updating cache metrics"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        pass

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and update cache metrics"""
        response: Response = await call_next(request)

        # Update cache metrics if response has cache headers
        if hasattr(response, "headers"):
            cache_header = response.headers.get("X-Cache")
            if cache_header:
                # Extract cache name from endpoint
                endpoint = request.url.path
                cache_name = self._get_cache_name_from_endpoint(endpoint)

                if cache_name:
                    # Update cache size and memory usage (simplified)
                    # In production, this would get actual cache statistics
                    await self._update_cache_stats(cache_name)

        return response

    def _get_cache_name_from_endpoint(self, endpoint: str) -> str:
        """Map endpoint to cache name"""
        if "candles" in endpoint:
            return "candle_cache"
        elif "quotes" in endpoint:
            return "quote_cache"
        else:
            return "unknown_cache"

    async def _update_cache_stats(self, cache_name: str):
        """Update cache statistics using the performance monitor"""
        try:
            from ..monitoring import get_performance_monitor

            monitor = get_performance_monitor()

            # Placeholder values - would get actual cache stats
            cache_size = 100  # Placeholder
            memory_usage = 50.0  # Placeholder MB

            await monitor.update_cache_stats(cache_name, cache_size, memory_usage)

        except Exception as e:
            # Emit error event instead of direct logging
            emit_function_timing(
                function_name="_update_cache_stats",
                duration=0.0,
                success=False,
                error=f"Failed to update cache stats: {e}",
                error_type="CacheStatsError",
            )


class CacheMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for detailed cache metrics collection"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Note: logger.info is async but we can't await in __init__
        pass

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Collect detailed cache metrics"""
        start_time = time.time()

        # Check if this is a cache-related operation
        is_cache_operation = self._is_cache_operation(request)

        response: Response = await call_next(request)

        if is_cache_operation:
            # Calculate operation duration
            duration = time.time() - start_time

            # Extract cache information from response headers
            cache_operation = response.headers.get("X-Cache-Operation", "unknown")
            cache_name = response.headers.get("X-Cache-Name", "unknown")
            cache_hit = response.headers.get("X-Cache") == "HIT"

            # Record cache metrics
            await self._record_cache_metrics(
                cache_operation=cache_operation,
                cache_name=cache_name,
                hit=cache_hit,
                duration=duration,
                endpoint=request.url.path,
            )

        return response

    def _is_cache_operation(self, request: Request) -> bool:
        """Determine if this request involves cache operations"""
        cache_indicators = [
            "cache" in request.url.path.lower(),
            "redis" in request.url.path.lower(),
            request.headers.get("X-Cache-Operation") is not None,
        ]
        return any(cache_indicators)

    async def _record_cache_metrics(
        self,
        cache_operation: str,
        cache_name: str,
        hit: bool,
        duration: float,
        endpoint: str,
    ):
        """Record cache metrics using the metrics collector"""
        try:
            from ..monitoring import get_metrics_collector

            collector = get_metrics_collector()

            await collector.collect_cache_metrics(
                cache_operation=cache_operation,
                cache_name=cache_name,
                hit=hit,
                duration=duration,
            )

        except Exception as e:
            # Emit error event instead of direct logging
            emit_function_timing(
                function_name="_record_cache_metrics",
                duration=0.0,
                success=False,
                error=f"Failed to record cache metrics: {e}",
                error_type="CacheMetricsError",
            )


class CacheHealthMiddleware(BaseHTTPMiddleware):
    """Middleware for cache health monitoring"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Note: logger.info is async but we can't await in __init__
        pass

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitor cache health and add health headers"""
        response: Response = await call_next(request)

        # Add cache health headers if this is a cache operation
        if self._is_cache_operation(request):
            cache_health = await self._get_cache_health()

            if hasattr(response, "headers"):
                response.headers["X-Cache-Health"] = cache_health["status"]
                response.headers["X-Cache-Hit-Rate"] = (
                    f"{cache_health['hit_rate']:.2f}%"
                )
                response.headers["X-Cache-Status"] = cache_health["message"]

        return response

    def _is_cache_operation(self, request: Request) -> bool:
        """Determine if this request involves cache operations"""
        return (
            "cache" in request.url.path.lower() or "redis" in request.url.path.lower()
        )

    async def _get_cache_health(self) -> dict:
        """Get cache health status"""
        try:
            from ..monitoring import get_performance_monitor

            monitor = get_performance_monitor()

            # Get cache metrics
            summary = monitor.get_performance_summary()
            cache_metrics = summary.get("caches", {})

            # Calculate overall cache health
            total_hits = 0
            total_misses = 0

            for cache_data in cache_metrics.values():
                total_hits += cache_data.get("hits", 0)
                total_misses += cache_data.get("misses", 0)

            total_requests = total_hits + total_misses
            hit_rate = (
                (total_hits / total_requests * 100) if total_requests > 0 else 0.0
            )

            # Determine health status
            if hit_rate >= 80:
                status = "healthy"
                message = "Cache performing well"
            elif hit_rate >= 60:
                status = "degraded"
                message = "Cache performance below optimal"
            else:
                status = "unhealthy"
                message = "Cache performance needs attention"

            return {
                "status": status,
                "hit_rate": hit_rate,
                "message": message,
                "total_requests": total_requests,
                "total_hits": total_hits,
                "total_misses": total_misses,
            }

        except Exception as e:
            # Emit error event instead of direct logging
            emit_function_timing(
                function_name="_get_cache_health",
                duration=0.0,
                success=False,
                error=f"Failed to get cache health: {e}",
                error_type="CacheHealthError",
            )
            return {
                "status": "unknown",
                "hit_rate": 0.0,
                "message": "Unable to determine cache health",
                "total_requests": 0,
                "total_hits": 0,
                "total_misses": 0,
            }
