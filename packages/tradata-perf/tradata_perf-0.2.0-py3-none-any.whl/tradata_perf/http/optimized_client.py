"""
High-performance HTTP client with connection pooling and optimization.
Provides optimized HTTP operations with performance tracking and metrics collection.
"""

import asyncio
import time
from typing import Any, Dict, Optional
import httpx
from ..monitoring.event_system import emit_system_metric, emit_function_timing


class OptimizedHTTPClient:
    """High-performance HTTP client with connection pooling and optimization."""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._lock = asyncio.Lock()
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._total_response_time = 0.0
        self._request_times: list[float] = []

        # Note: logger.info is async but we can't await in __init__
        pass

    async def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client with connection pooling."""
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    # Use default values for now
                    limits = httpx.Limits(
                        max_keepalive_connections=20,
                        max_connections=100,
                        keepalive_expiry=30.0,
                    )
                    timeout = httpx.Timeout(
                        connect=2.0, read=10.0, write=10.0, pool=30.0
                    )
                    self._client = httpx.AsyncClient(
                        limits=limits,
                        timeout=timeout,
                        http2=False,  # Disable HTTP2 for compatibility
                        follow_redirects=True,
                    )
                    # Emit HTTP client creation event
                    emit_system_metric(
                        metric_name="http_client_created",
                        value=1.0,
                        unit="count",
                        metadata={
                            "operation": "init",
                            "step": "connection_pool",
                            "max_connections": limits.max_connections,
                            "max_keepalive": limits.max_keepalive_connections,
                        },
                    )
        return self._client

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Optimized GET request with performance tracking."""
        start_time = time.time()
        try:
            client = await self._get_client()
            response = await client.get(url, **kwargs)
            self._record_request(start_time, success=True)

            # Record API call metrics
            await self._record_api_metrics(
                "GET", url, time.time() - start_time, True, response.status_code
            )

            return response
        except Exception as e:
            self._record_request(start_time, success=False)

            # Record API call metrics for failed requests
            await self._record_api_metrics(
                "GET", url, time.time() - start_time, False, None, str(e)
            )

            raise

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Optimized POST request with performance tracking."""
        start_time = time.time()
        try:
            client = await self._get_client()
            response = await client.post(url, **kwargs)
            self._record_request(start_time, success=True)

            # Record API call metrics
            await self._record_api_metrics(
                "POST", url, time.time() - start_time, True, response.status_code
            )

            return response
        except Exception as e:
            self._record_request(start_time, success=False)

            # Record API call metrics for failed requests
            await self._record_api_metrics(
                "POST", url, time.time() - start_time, False, None, str(e)
            )

            raise

    async def put(self, url: str, **kwargs) -> httpx.Response:
        """Optimized PUT request with performance tracking."""
        start_time = time.time()
        try:
            client = await self._get_client()
            response = await client.put(url, **kwargs)
            self._record_request(start_time, success=True)

            # Record API call metrics
            await self._record_api_metrics(
                "PUT", url, time.time() - start_time, True, response.status_code
            )

            return response
        except Exception as e:
            self._record_request(start_time, success=False)

            # Record API call metrics for failed requests
            await self._record_api_metrics(
                "PUT", url, time.time() - start_time, False, None, str(e)
            )

            raise

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """Optimized DELETE request with performance tracking."""
        start_time = time.time()
        try:
            client = await self._get_client()
            response = await client.delete(url, **kwargs)
            self._record_request(start_time, success=True)

            # Record API call metrics
            await self._record_api_metrics(
                "DELETE", url, time.time() - start_time, True, response.status_code
            )

            return response
        except Exception as e:
            self._record_request(start_time, success=False)

            # Record API call metrics for failed requests
            await self._record_api_metrics(
                "DELETE", url, time.time() - start_time, False, None, str(e)
            )

            raise

    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            # Emit HTTP client closed event
            emit_system_metric(
                metric_name="http_client_closed",
                value=1.0,
                unit="count",
                metadata={"operation": "cleanup", "step": "http_client"},
            )

    def _record_request(self, start_time: float, success: bool = True):
        """Record request performance metrics."""
        response_time = time.time() - start_time
        self._total_requests += 1
        self._total_response_time += response_time
        self._request_times.append(response_time)

        if success:
            self._successful_requests += 1
        else:
            self._failed_requests += 1

        # Keep only last 1000 request times for memory efficiency
        if len(self._request_times) > 1000:
            self._request_times = self._request_times[-1000:]

    async def _record_api_metrics(
        self,
        method: str,
        url: str,
        duration: float,
        success: bool,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
    ):
        """Record API call metrics using the metrics collector."""
        try:
            from ..monitoring import get_metrics_collector

            collector = get_metrics_collector()

            # Extract API name from URL
            api_name = self._extract_api_name(url)
            endpoint = self._extract_endpoint(url)

            await collector.collect_api_call_metrics(
                api_name=api_name,
                endpoint=endpoint,
                duration=duration,
                success=success,
                status_code=status_code,
                error_message=error_message,
            )

        except Exception as e:
            # Emit error event instead of direct logging
            emit_function_timing(
                function_name="_record_api_metrics",
                duration=0.0,
                success=False,
                error=f"Failed to record API metrics: {e}",
                error_type="MetricRecordingError",
            )

    def _extract_api_name(self, url: str) -> str:
        """Extract API name from URL for metrics categorization."""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            hostname = parsed.hostname or "unknown"

            # Extract API name from hostname
            if "alpaca" in hostname.lower():
                return "alpaca"
            elif "alphavantage" in hostname.lower():
                return "alpha_vantage"
            elif "api" in hostname.lower():
                return "external_api"
            else:
                return hostname.split(".")[0] if "." in hostname else hostname
        except Exception:
            return "unknown_api"

    def _extract_endpoint(self, url: str) -> str:
        """Extract endpoint path from URL for metrics categorization."""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            return parsed.path or "/"
        except Exception:
            return "/"

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get HTTP client performance statistics."""
        if not self._request_times:
            return {
                "total_requests": 0,
                "success_rate_percent": 0.0,
                "avg_response_time_ms": 0.0,
                "p95_response_time_ms": 0.0,
                "p99_response_time_ms": 0.0,
            }

        sorted_times = sorted(self._request_times)
        n = len(sorted_times)

        avg_response_time = self._total_response_time / n
        p95_index = int(0.95 * n)
        p99_index = int(0.99 * n)

        success_rate = (
            (self._successful_requests / self._total_requests * 100)
            if self._total_requests > 0
            else 0
        )

        return {
            "total_requests": self._total_requests,
            "successful_requests": self._successful_requests,
            "failed_requests": self._failed_requests,
            "success_rate_percent": round(success_rate, 2),
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "p95_response_time_ms": round(sorted_times[p95_index] * 1000, 2),
            "p99_response_time_ms": round(sorted_times[p99_index] * 1000, 2),
            "min_response_time_ms": round(min(sorted_times) * 1000, 2),
            "max_response_time_ms": round(max(sorted_times) * 1000, 2),
        }


# Global HTTP client instance
_http_client: Optional[OptimizedHTTPClient] = None


def get_http_client() -> OptimizedHTTPClient:
    """Get global HTTP client instance."""
    global _http_client
    if _http_client is None:
        _http_client = OptimizedHTTPClient()
    return _http_client


async def close_http_client():
    """Close global HTTP client."""
    global _http_client
    if _http_client:
        await _http_client.close()
        _http_client = None
