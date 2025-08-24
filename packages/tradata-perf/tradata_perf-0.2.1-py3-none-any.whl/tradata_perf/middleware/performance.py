"""
FastAPI middleware for automatic performance monitoring.
Automatically captures metrics for all API requests without manual instrumentation.
"""

import time
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..monitoring.event_system import emit_request_metrics


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic performance monitoring of all requests"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        pass

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and capture performance metrics"""
        start_time = time.time()

        # Extract request information
        endpoint = request.url.path
        method = request.method
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None

        try:
            # Process the request
            response: Response = await call_next(request)

            # Calculate response time
            response_time = time.time() - start_time

            # Determine if it was a cache hit
            cache_hit = False
            if hasattr(response, "headers"):
                cache_hit = response.headers.get("X-Cache") == "HIT"

            # Emit successful request event
            emit_request_metrics(
                endpoint=endpoint,
                method=method,
                duration=response_time,
                success=True,
                status_code=response.status_code,
                cache_hit=cache_hit,
            )

            # Record successful request metrics
            await self._record_request_metrics(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                response_time=response_time,
                cache_hit=cache_hit,
                user_agent=user_agent or "",
                ip_address=ip_address or "",
            )

            # Add performance headers
            if hasattr(response, "headers"):
                response.headers["X-Response-Time"] = f"{response_time:.3f}s"
                response.headers["X-Request-ID"] = f"{int(start_time * 1000000)}"

            return response

        except Exception as e:
            # Calculate response time for failed requests
            response_time = time.time() - start_time

            # Emit failed request event
            emit_request_metrics(
                endpoint=endpoint,
                method=method,
                duration=response_time,
                success=False,
                status_code=500,
                error=str(e),
                cache_hit=False,
            )

            # Record failed request metrics
            await self._record_request_metrics(
                endpoint=endpoint,
                method=method,
                status_code=500,
                response_time=response_time,
                cache_hit=False,
                error=str(e),
                user_agent=user_agent or "",
                ip_address=ip_address or "",
            )

            # Re-raise the exception
            raise

    async def _record_request_metrics(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        cache_hit: bool = False,
        error: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ):
        """Record request metrics using the performance monitor"""
        try:
            from ..monitoring import record_request_metrics

            await record_request_metrics(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                cache_hit=cache_hit,
                error=error,
                user_agent=user_agent or "",
                ip_address=ip_address or "",
            )
        except Exception as e:
            # Emit error event instead of direct logging
            emit_request_metrics(
                endpoint=endpoint,
                method=method,
                duration=0.0,
                success=False,
                error=f"Failed to record request metrics: {e}",
            )


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware for adding request timing headers"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Note: logger.info is async but we can't await in __init__
        pass

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add timing headers to response"""
        start_time = time.time()

        response: Response = await call_next(request)

        # Calculate response time
        response_time = time.time() - start_time

        # Add timing headers
        if hasattr(response, "headers"):
            response.headers["X-Request-Time"] = f"{start_time:.6f}"
            response.headers["X-Response-Time"] = f"{response_time:.6f}"
            response.headers["X-Total-Time"] = f"{response_time:.6f}"

        return response


class PerformanceHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding performance-related headers"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Note: logger.info is async but we can't await in __init__
        pass

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add performance headers to response"""
        start_time = time.time()

        response: Response = await call_next(request)

        # Calculate response time
        response_time = time.time() - start_time

        # Add performance headers
        if hasattr(response, "headers"):
            response.headers["X-Request-Start"] = f"{start_time:.6f}"
            response.headers["X-Response-Time"] = f"{response_time:.6f}"

        return response
