"""
Metrics collection decorators for automatic data collection.
Provides decorators to collect custom metrics, business metrics, and performance counters.
"""

import time
import functools
import asyncio
from typing import Any, Callable, Optional, Dict
from ..monitoring.event_system import emit_function_timing


def collect_metrics(
    func: Optional[Callable] = None,
    *,
    metric_name: Optional[str] = None,
    metric_type: str = "counter",
    tags: Optional[Dict[str, str]] = None,
    include_args: bool = False,
    include_result: bool = False,
) -> Callable:
    """
    Decorator to collect custom metrics for function calls.

    Args:
        func: Function to decorate
        metric_name: Custom metric name (defaults to function name)
        metric_type: Type of metric (counter, gauge, histogram)
        tags: Additional tags for the metric
        include_args: Whether to include function arguments in metadata
        include_result: Whether to include function result in metadata

    Usage:
        @collect_metrics(metric_type="counter", tags={"service": "quotes"})
        def get_quote(symbol: str):
            # Function implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Collect metrics
                asyncio.create_task(
                    _collect_function_metrics(
                        func.__name__,
                        metric_name,
                        metric_type,
                        tags,
                        duration,
                        True,
                        args,
                        kwargs,
                        result,
                        include_args,
                        include_result,
                    )
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Collect metrics for failed execution
                asyncio.create_task(
                    _collect_function_metrics(
                        func.__name__,
                        metric_name,
                        metric_type,
                        tags,
                        duration,
                        False,
                        args,
                        kwargs,
                        None,
                        include_args,
                        include_result,
                        str(e),
                    )
                )

                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Collect metrics
                await _collect_function_metrics(
                    func.__name__,
                    metric_name,
                    metric_type,
                    tags,
                    duration,
                    True,
                    args,
                    kwargs,
                    result,
                    include_args,
                    include_result,
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Collect metrics for failed execution
                await _collect_function_metrics(
                    func.__name__,
                    metric_name,
                    metric_type,
                    tags,
                    duration,
                    False,
                    args,
                    kwargs,
                    None,
                    include_args,
                    include_result,
                    str(e),
                )

                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    # Handle both @collect_metrics and @collect_metrics() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


def track_calls(
    func: Optional[Callable] = None,
    *,
    track_success: bool = True,
    track_failure: bool = True,
    track_duration: bool = True,
    custom_tags: Optional[Dict[str, str]] = None,
) -> Callable:
    """
    Decorator to track function call statistics.

    Args:
        func: Function to decorate
        track_success: Whether to track successful calls
        track_failure: Whether to track failed calls
        track_duration: Whether to track call duration
        custom_tags: Additional tags for the metrics

    Usage:
        @track_calls(track_duration=True, custom_tags={"priority": "high"})
        def critical_function():
            # Function implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Track successful call
                if track_success:
                    asyncio.create_task(
                        _track_call_metric(
                            func.__name__, "success", duration, custom_tags
                        )
                    )

                # Track duration if enabled
                if track_duration:
                    asyncio.create_task(
                        _track_duration_metric(func.__name__, duration, custom_tags)
                    )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Track failed call
                if track_failure:
                    asyncio.create_task(
                        _track_call_metric(
                            func.__name__, "failure", duration, custom_tags, str(e)
                        )
                    )

                # Track duration if enabled
                if track_duration:
                    asyncio.create_task(
                        _track_duration_metric(func.__name__, duration, custom_tags)
                    )

                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Track successful call
                if track_success:
                    await _track_call_metric(
                        func.__name__, "success", duration, custom_tags
                    )

                # Track duration if enabled
                if track_duration:
                    await _track_duration_metric(func.__name__, duration, custom_tags)

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Track failed call
                if track_failure:
                    await _track_call_metric(
                        func.__name__, "failure", duration, custom_tags, str(e)
                    )

                # Track duration if enabled
                if track_duration:
                    await _track_duration_metric(func.__name__, duration, custom_tags)

                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    # Handle both @track_calls and @track_calls() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


def business_metrics(
    func: Optional[Callable] = None,
    *,
    metric_name: Optional[str] = None,
    value_extractor: Optional[Callable] = None,
    tags: Optional[Dict[str, str]] = None,
    aggregation: str = "sum",
) -> Callable:
    """
    Decorator to collect business-specific metrics.

    Args:
        func: Function to decorate
        metric_name: Custom metric name
        value_extractor: Function to extract metric value from result
        tags: Additional tags for the metric
        aggregation: Aggregation type (sum, avg, min, max, count)

    Usage:
        @business_metrics(
            metric_name="quotes_processed",
            value_extractor=lambda result: len(result),
            tags={"service": "quotes"}
        )
        def process_quotes(symbols: List[str]):
            # Function implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # Extract business metric value
                if value_extractor:
                    metric_value = value_extractor(result)
                else:
                    # Default to 1 for counter metrics
                    metric_value = 1.0

                # Collect business metric
                asyncio.create_task(
                    _collect_business_metric(
                        func.__name__, metric_name, metric_value, tags, aggregation
                    )
                )

                return result

            except Exception as e:
                # Collect business metric for failed execution (usually 0 or error count)
                asyncio.create_task(
                    _collect_business_metric(
                        func.__name__, metric_name, 0.0, tags, aggregation, str(e)
                    )
                )

                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                # Extract business metric value
                if value_extractor:
                    metric_value = value_extractor(result)
                else:
                    # Default to 1 for counter metrics
                    metric_value = 1.0

                # Collect business metric
                await _collect_business_metric(
                    func.__name__, metric_name, metric_value, tags, aggregation
                )

                return result

            except Exception as e:
                # Collect business metric for failed execution (usually 0 or error count)
                await _collect_business_metric(
                    func.__name__, metric_name, 0.0, tags, aggregation, str(e)
                )

                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    # Handle both @business_metrics and @business_metrics() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


def performance_counter(
    func: Optional[Callable] = None,
    *,
    counter_name: Optional[str] = None,
    increment_on: str = "call",
    tags: Optional[Dict[str, str]] = None,
) -> Callable:
    """
    Decorator to maintain performance counters.

    Args:
        func: Function to decorate
        counter_name: Custom counter name
        increment_on: When to increment counter (call, success, failure)
        tags: Additional tags for the counter

    Usage:
        @performance_counter(increment_on="success", tags={"priority": "high"})
        def critical_function():
            # Function implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # Increment counter based on configuration
                if increment_on in ["call", "success"]:
                    asyncio.create_task(
                        _increment_performance_counter(
                            func.__name__, counter_name, tags
                        )
                    )

                return result

            except Exception:
                # Increment counter based on configuration
                if increment_on in ["call", "failure"]:
                    asyncio.create_task(
                        _increment_performance_counter(
                            func.__name__, counter_name, tags, "failure"
                        )
                    )

                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                # Increment counter based on configuration
                if increment_on in ["call", "success"]:
                    await _increment_performance_counter(
                        func.__name__, counter_name, tags
                    )

                return result

            except Exception:
                # Increment counter based on configuration
                if increment_on in ["call", "failure"]:
                    await _increment_performance_counter(
                        func.__name__, counter_name, tags, "failure"
                    )

                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    # Handle both @performance_counter and @performance_counter() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


# Utility functions for metrics collection
async def _collect_function_metrics(
    func_name: str,
    metric_name: Optional[str],
    metric_type: str,
    tags: Optional[Dict[str, str]],
    duration: float,
    success: bool,
    args: tuple,
    kwargs: dict,
    result: Any,
    include_args: bool,
    include_result: bool,
    error: Optional[str] = None,
):
    """Collect function execution metrics."""
    try:
        from ..monitoring import get_metrics_collector

        collector = get_metrics_collector()

        # Prepare tags
        metric_tags = tags or {}
        metric_tags.update(
            {"function": func_name, "type": metric_type, "success": str(success)}
        )

        # Prepare metadata
        metadata: Dict[str, Any] = {"duration_seconds": duration, "success": success}

        if include_args:
            metadata["args"] = str(args)
            metadata["kwargs"] = str(kwargs)

        if include_result and result is not None:
            metadata["result"] = str(result)

        if error:
            metadata["error"] = error

        # Use custom metric name or default
        name = metric_name or f"{func_name}_{metric_type}"

        # Collect the metric
        await collector.collect_custom_metric(
            name=name,
            value=duration if metric_type == "histogram" else 1.0,
            tags=metric_tags,
            metadata=metadata,
        )

    except Exception as e:
        # Emit error event instead of direct logging
        emit_function_timing(
            function_name="_collect_function_metrics",
            duration=0.0,
            success=False,
            error=f"Failed to collect function metrics: {e}",
            error_type="MetricCollectionError",
        )


async def _track_call_metric(
    func_name: str,
    call_type: str,
    duration: float,
    custom_tags: Optional[Dict[str, str]],
    error: Optional[str] = None,
):
    """Track function call metrics."""
    try:
        from ..monitoring import get_metrics_collector

        collector = get_metrics_collector()

        # Prepare tags
        tags = custom_tags or {}
        tags.update({"function": func_name, "call_type": call_type})

        # Prepare metadata
        metadata = {"duration_seconds": duration, "call_type": call_type}

        if error:
            metadata["error"] = error

        # Collect call count metric
        await collector.collect_custom_metric(
            name=f"{func_name}_calls", value=1.0, tags=tags, metadata=metadata
        )

    except Exception as e:
        # Emit error event instead of direct logging
        emit_function_timing(
            function_name="_track_call_metric",
            duration=0.0,
            success=False,
            error=f"Failed to track call metric: {e}",
            error_type="MetricTrackingError",
        )


async def _track_duration_metric(
    func_name: str, duration: float, custom_tags: Optional[Dict[str, str]]
):
    """Track function duration metrics."""
    try:
        from ..monitoring import get_metrics_collector

        collector = get_metrics_collector()

        # Prepare tags
        tags = custom_tags or {}
        tags.update({"function": func_name, "type": "duration"})

        # Collect duration metric
        await collector.collect_custom_metric(
            name=f"{func_name}_duration",
            value=duration,
            tags=tags,
            metadata={"duration_seconds": duration},
        )

    except Exception as e:
        # Emit error event instead of direct logging
        emit_function_timing(
            function_name="_track_duration_metric",
            duration=0.0,
            success=False,
            error=f"Failed to track duration metric: {e}",
            error_type="MetricTrackingError",
        )


async def _collect_business_metric(
    func_name: str,
    metric_name: Optional[str],
    metric_value: float,
    tags: Optional[Dict[str, str]],
    aggregation: str,
    error: Optional[str] = None,
):
    """Collect business-specific metrics."""
    try:
        from ..monitoring import get_metrics_collector

        collector = get_metrics_collector()

        # Prepare tags
        metric_tags = tags or {}
        metric_tags.update({"function": func_name, "aggregation": aggregation})

        # Prepare metadata
        metadata = {"value": metric_value, "aggregation": aggregation}

        if error:
            metadata["error"] = error

        # Use custom metric name or default
        name = metric_name or f"{func_name}_business_metric"

        # Collect the business metric
        await collector.collect_custom_metric(
            name=name, value=metric_value, tags=metric_tags, metadata=metadata
        )

    except Exception as e:
        # Emit error event instead of direct logging
        emit_function_timing(
            function_name="_collect_business_metric",
            duration=0.0,
            success=False,
            error=f"Failed to collect business metric: {e}",
            error_type="BusinessMetricError",
        )


async def _increment_performance_counter(
    func_name: str,
    counter_name: Optional[str],
    tags: Optional[Dict[str, str]],
    counter_type: str = "success",
):
    """Increment performance counter."""
    try:
        from ..monitoring import get_metrics_collector

        collector = get_metrics_collector()

        # Prepare tags
        counter_tags = tags or {}
        counter_tags.update({"function": func_name, "counter_type": counter_type})

        # Use custom counter name or default
        name = counter_name or f"{func_name}_counter"

        # Collect the counter metric
        await collector.collect_custom_metric(
            name=name,
            value=1.0,
            tags=counter_tags,
            metadata={"counter_type": counter_type},
        )

    except Exception as e:
        # Emit error event instead of direct logging
        emit_function_timing(
            function_name="_increment_performance_counter",
            duration=0.0,
            success=False,
            error=f"Failed to increment performance counter: {e}",
            error_type="CounterIncrementError",
        )
