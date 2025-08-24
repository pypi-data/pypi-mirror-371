"""
Performance decorators for automatic timing and profiling.
Provides decorators to measure function execution time and performance metrics.
"""

import time
import functools
import asyncio
from typing import Callable, Optional
from ..monitoring.event_system import (
    emit_function_timing,
    emit_profiling_result,
    emit_metric_recorded,
)


def timing(
    func: Optional[Callable] = None,
    *,
    log_result: bool = True,
    log_args: bool = False,
    metric_name: Optional[str] = None,
) -> Callable:
    """
    Decorator to measure function execution time.

    Args:
        func: Function to decorate
        log_result: Whether to log the timing result
        log_args: Whether to log function arguments
        metric_name: Custom metric name for the timing measurement

    Usage:
        @timing
        def slow_function():
            time.sleep(1)

        @timing(log_result=True, log_args=True)
        def function_with_args(x, y):
            return x + y
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                if log_result:
                    # Emit function timing event instead of direct logging
                    emit_function_timing(
                        function_name=func.__name__,
                        duration=duration,
                        success=True,
                        args=str(args) if log_args else None,
                        kwargs=str(kwargs) if log_args else None,
                    )

                # Record timing metric if collector is available
                try:
                    # Only create task if there's a running event loop
                    asyncio.create_task(
                        _record_timing_metric(
                            func.__name__, duration, True, metric_name
                        )
                    )
                except RuntimeError:
                    # No running event loop, skip async metric recording
                    pass

                return result

            except Exception as e:
                duration = time.time() - start_time

                if log_result:
                    # Emit function timing error event instead of direct logging
                    emit_function_timing(
                        function_name=func.__name__,
                        duration=duration,
                        success=False,
                        args=str(args) if log_args else None,
                        kwargs=str(kwargs) if log_args else None,
                        error=str(e),
                        error_type=type(e).__name__,
                    )

                # Record timing metric if collector is available
                try:
                    # Only create task if there's a running event loop
                    asyncio.create_task(
                        _record_timing_metric(
                            func.__name__, duration, False, metric_name
                        )
                    )
                except RuntimeError:
                    # No running event loop, skip async metric recording
                    pass

                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                if log_result:
                    # Emit function timing event instead of direct logging
                    emit_function_timing(
                        function_name=func.__name__,
                        duration=duration,
                        success=True,
                        args=str(args) if log_args else None,
                        kwargs=str(kwargs) if log_args else None,
                    )

                # Record timing metric
                await _record_timing_metric(func.__name__, duration, True, metric_name)

                return result

            except Exception as e:
                duration = time.time() - start_time

                if log_result:
                    # Emit function timing error event instead of direct logging
                    emit_function_timing(
                        function_name=func.__name__,
                        duration=duration,
                        success=False,
                        args=str(args) if log_args else None,
                        kwargs=str(kwargs) if log_args else None,
                        error=str(e),
                        error_type=type(e).__name__,
                    )

                # Record timing metric for failed execution
                await _record_timing_metric(func.__name__, duration, False, metric_name)

                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    # Handle both @timing and @timing() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


def profile(
    func: Optional[Callable] = None,
    *,
    track_memory: bool = False,
    track_cpu: bool = False,
    detailed: bool = False,
) -> Callable:
    """
    Decorator for detailed performance profiling.

    Args:
        func: Function to decorate
        track_memory: Whether to track memory usage
        track_cpu: Whether to track CPU usage
        detailed: Whether to include detailed profiling information

    Usage:
        @profile(track_memory=True, track_cpu=True)
        def memory_intensive_function():
            # Function implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Record initial state
            start_time = time.time()
            initial_memory = _get_memory_usage() if track_memory else None
            initial_cpu = _get_cpu_usage() if track_cpu else None

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Record final state
                final_memory = _get_memory_usage() if track_memory else None
                final_cpu = _get_cpu_usage() if track_cpu else None

                # Calculate deltas
                memory_delta = final_memory - initial_memory if track_memory else None
                cpu_delta = final_cpu - initial_cpu if track_cpu else None

                # Log profiling results
                _log_profiling_results(
                    func.__name__,
                    duration,
                    memory_delta,
                    cpu_delta,
                    detailed,
                    True,
                    args,
                    kwargs,
                )

                # Record profiling metrics
                asyncio.create_task(
                    _record_profiling_metrics(
                        func.__name__, duration, memory_delta, cpu_delta, True
                    )
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Log profiling results for failed execution
                _log_profiling_results(
                    func.__name__,
                    duration,
                    None,
                    None,
                    detailed,
                    False,
                    args,
                    kwargs,
                    str(e),
                )

                # Record profiling metrics for failed execution
                asyncio.create_task(
                    _record_profiling_metrics(
                        func.__name__, duration, None, None, False
                    )
                )

                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Record initial state
            start_time = time.time()
            initial_memory = _get_memory_usage() if track_memory else None
            initial_cpu = _get_cpu_usage() if track_cpu else None

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Record final state
                final_memory = _get_memory_usage() if track_memory else None
                final_cpu = _get_cpu_usage() if track_cpu else None

                # Calculate deltas
                memory_delta = final_memory - initial_memory if track_memory else None
                cpu_delta = final_cpu - initial_cpu if track_cpu else None

                # Log profiling results
                _log_profiling_results(
                    func.__name__,
                    duration,
                    memory_delta,
                    cpu_delta,
                    detailed,
                    True,
                    args,
                    kwargs,
                )

                # Record profiling metrics
                await _record_profiling_metrics(
                    func.__name__, duration, memory_delta, cpu_delta, True
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Log profiling results for failed execution
                _log_profiling_results(
                    func.__name__,
                    duration,
                    None,
                    None,
                    detailed,
                    False,
                    args,
                    kwargs,
                    str(e),
                )

                # Record profiling metrics for failed execution
                await _record_profiling_metrics(
                    func.__name__, duration, None, None, False
                )

                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    # Handle both @profile and @profile() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


def monitor_performance(
    func: Optional[Callable] = None,
    *,
    track_memory: bool = True,
    track_cpu: bool = True,
    track_calls: bool = True,
    threshold_ms: Optional[float] = None,
) -> Callable:
    """
    Comprehensive performance monitoring decorator.

    Args:
        func: Function to decorate
        track_memory: Whether to track memory usage
        track_cpu: Whether to track CPU usage
        track_calls: Whether to track call count
        threshold_ms: Performance threshold in milliseconds (logs warning if exceeded)

    Usage:
        @monitor_performance(threshold_ms=1000)
        def critical_function():
            # Function implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        # Track call count if enabled
        call_count = 0

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            start_time = time.time()
            initial_memory = _get_memory_usage() if track_memory else None
            initial_cpu = _get_cpu_usage() if track_cpu else None

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Check threshold
                if threshold_ms and (duration * 1000) > threshold_ms:
                    # Emit threshold exceeded event instead of direct logging
                    emit_function_timing(
                        function_name=func.__name__,
                        duration=duration,
                        success=True,
                        error=f"Exceeded performance threshold of {threshold_ms}ms",
                        error_type="ThresholdExceeded",
                    )

                # Record comprehensive metrics
                asyncio.create_task(
                    _record_comprehensive_metrics(
                        func.__name__,
                        duration,
                        call_count,
                        initial_memory,
                        initial_cpu,
                        _get_memory_usage() if track_memory else None,
                        _get_cpu_usage() if track_cpu else None,
                        True,
                    )
                )

                return result

            except Exception:
                duration = time.time() - start_time

                # Record comprehensive metrics for failed execution
                asyncio.create_task(
                    _record_comprehensive_metrics(
                        func.__name__,
                        duration,
                        call_count,
                        initial_memory,
                        initial_cpu,
                        None,
                        None,
                        False,
                    )
                )

                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            start_time = time.time()
            initial_memory = _get_memory_usage() if track_memory else None
            initial_cpu = _get_cpu_usage() if track_cpu else None

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Check threshold
                if threshold_ms and (duration * 1000) > threshold_ms:
                    # Emit threshold exceeded event instead of direct logging
                    emit_function_timing(
                        function_name=func.__name__,
                        duration=duration,
                        success=True,
                        error=f"Exceeded performance threshold of {threshold_ms}ms",
                        error_type="ThresholdExceeded",
                    )

                # Record comprehensive metrics
                await _record_comprehensive_metrics(
                    func.__name__,
                    duration,
                    call_count,
                    initial_memory,
                    initial_cpu,
                    _get_memory_usage() if track_memory else None,
                    _get_cpu_usage() if track_cpu else None,
                    True,
                )

                return result

            except Exception:
                duration = time.time() - start_time

                # Record comprehensive metrics for failed execution
                await _record_comprehensive_metrics(
                    func.__name__,
                    duration,
                    call_count,
                    initial_memory,
                    initial_cpu,
                    None,
                    None,
                    False,
                )

                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    # Handle both @monitor_performance and @monitor_performance() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


# Utility functions
def _get_memory_usage() -> Optional[float]:
    """Get current memory usage in MB."""
    try:
        import psutil

        process = psutil.Process()
        memory_bytes: int = process.memory_info().rss
        return memory_bytes / (1024 * 1024)  # Convert to MB
    except ImportError:
        return None


def _get_cpu_usage() -> Optional[float]:
    """Get current CPU usage percentage."""
    try:
        import psutil

        cpu_percent: float = psutil.cpu_percent(interval=None)
        return cpu_percent
    except ImportError:
        return None


def _log_profiling_results(
    func_name: str,
    duration: float,
    memory_delta: Optional[float],
    cpu_delta: Optional[float],
    detailed: bool,
    success: bool,
    args: tuple,
    kwargs: dict,
    error: Optional[str] = None,
):
    """Emit profiling result events instead of direct logging."""
    # Emit profiling result event
    emit_profiling_result(
        function_name=func_name,
        duration=duration,
        memory_delta=memory_delta,
        cpu_delta=cpu_delta,
        success=success,
        error=error,
    )
    # Also emit metric recorded events for the profiling data
    if memory_delta is not None:
        emit_metric_recorded(
            metric_name=f"{func_name}_memory_delta",
            value=memory_delta,
            labels={"function": func_name, "type": "memory"},
            timestamp=time.time(),
        )
    if cpu_delta is not None:
        emit_metric_recorded(
            metric_name=f"{func_name}_cpu_delta",
            value=cpu_delta,
            labels={"function": func_name, "type": "cpu"},
            timestamp=time.time(),
        )


async def _record_timing_metric(
    func_name: str, duration: float, success: bool, metric_name: Optional[str] = None
):
    """Record timing metric using the metrics collector."""
    try:
        from ..monitoring import get_metrics_collector

        collector = get_metrics_collector()

        metric_name = metric_name or f"{func_name}_execution_time"

        await collector.collect_custom_metric(
            name=metric_name,
            value=duration,
            tags={"function": func_name, "type": "timing"},
            metadata={"success": success, "duration_seconds": duration},
        )

    except Exception as e:
        # Emit error event instead of direct logging
        emit_function_timing(
            function_name="_record_timing_metric",
            duration=0.0,
            success=False,
            error=f"Failed to record timing metric: {e}",
            error_type="MetricRecordingError",
        )


async def _record_profiling_metrics(
    func_name: str,
    duration: float,
    memory_delta: Optional[float],
    cpu_delta: Optional[float],
    success: bool,
):
    """Record profiling metrics using the metrics collector."""
    try:
        from ..monitoring import get_metrics_collector

        collector = get_metrics_collector()

        # Record execution time
        await collector.collect_custom_metric(
            name=f"{func_name}_execution_time",
            value=duration,
            tags={"function": func_name, "type": "profiling"},
            metadata={"success": success, "duration_seconds": duration},
        )

        # Record memory delta if available
        if memory_delta is not None:
            await collector.collect_custom_metric(
                name=f"{func_name}_memory_delta",
                value=memory_delta,
                tags={"function": func_name, "type": "memory"},
                metadata={"success": success, "delta_mb": memory_delta},
            )

        # Record CPU delta if available
        if cpu_delta is not None:
            await collector.collect_custom_metric(
                name=f"{func_name}_cpu_delta",
                value=cpu_delta,
                tags={"function": func_name, "type": "cpu"},
                metadata={"success": success, "delta_percent": cpu_delta},
            )

    except Exception as e:
        # Emit error event instead of direct logging
        emit_function_timing(
            function_name="_record_profiling_metrics",
            duration=0.0,
            success=False,
            error=f"Failed to record profiling metrics: {e}",
            error_type="MetricRecordingError",
        )


async def _record_comprehensive_metrics(
    func_name: str,
    duration: float,
    call_count: int,
    initial_memory: Optional[float],
    initial_cpu: Optional[float],
    final_memory: Optional[float],
    final_cpu: Optional[float],
    success: bool,
):
    """Record comprehensive performance metrics."""
    try:
        from ..monitoring import get_metrics_collector

        collector = get_metrics_collector()

        # Record execution time
        await collector.collect_custom_metric(
            name=f"{func_name}_execution_time",
            value=duration,
            tags={"function": func_name, "type": "comprehensive"},
            metadata={
                "success": success,
                "duration_seconds": duration,
                "call_count": call_count,
            },
        )

        # Record call count
        await collector.collect_custom_metric(
            name=f"{func_name}_call_count",
            value=float(call_count),
            tags={"function": func_name, "type": "calls"},
            metadata={"success": success, "total_calls": call_count},
        )

        # Record memory metrics if available
        if initial_memory is not None and final_memory is not None:
            memory_delta = final_memory - initial_memory
            await collector.collect_custom_metric(
                name=f"{func_name}_memory_delta",
                value=memory_delta,
                tags={"function": func_name, "type": "memory"},
                metadata={
                    "success": success,
                    "initial_mb": initial_memory,
                    "final_mb": final_memory,
                    "delta_mb": memory_delta,
                },
            )

        # Record CPU metrics if available
        if initial_cpu is not None and final_cpu is not None:
            cpu_delta = final_cpu - initial_cpu
            await collector.collect_custom_metric(
                name=f"{func_name}_cpu_delta",
                value=cpu_delta,
                tags={"function": func_name, "type": "cpu"},
                metadata={
                    "success": success,
                    "initial_percent": initial_cpu,
                    "final_percent": final_cpu,
                    "delta_percent": cpu_delta,
                },
            )

    except Exception as e:
        # Emit error event instead of direct logging
        emit_function_timing(
            function_name="_record_comprehensive_metrics",
            duration=0.0,
            success=False,
            error=f"Failed to record comprehensive metrics: {e}",
            error_type="MetricRecordingError",
        )
