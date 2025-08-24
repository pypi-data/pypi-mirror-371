"""
Event-driven performance monitoring system.
Replaces direct logger dependencies with an event emission system.
"""

import time
import asyncio
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class PerformanceEventType(Enum):
    """Enumeration of all performance event types"""

    FUNCTION_TIMING = "function_timing"
    FUNCTION_TIMING_ERROR = "function_timing_error"
    REQUEST_COMPLETED = "request_completed"
    REQUEST_FAILED = "request_failed"
    CACHE_OPERATION = "cache_operation"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    PROFILING_RESULT = "profiling_result"
    METRIC_RECORDED = "metric_recorded"
    HEALTH_CHECK = "health_check"
    SYSTEM_METRIC = "system_metric"


@dataclass
class PerformanceEvent:
    """Base performance event structure"""

    event_type: PerformanceEventType
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = "tradata_perf"
    version: str = "1.0"


class PerformanceEventEmitter:
    """Event emitter for performance events"""

    def __init__(self):
        self._handlers: Dict[PerformanceEventType, List[Callable]] = {
            event_type: [] for event_type in PerformanceEventType
        }
        self._global_handlers: List[Callable] = []
        self._event_queue: List[PerformanceEvent] = []
        self._max_queue_size = 10000
        self._lock = asyncio.Lock()

    def emit_event(
        self,
        event_type: PerformanceEventType,
        data: Dict[str, Any],
        source: str = "tradata_perf",
    ):
        """Emit a performance event without assuming any logger"""
        event = PerformanceEvent(event_type=event_type, data=data, source=source)

        # Add to queue
        self._event_queue.append(event)
        if len(self._event_queue) > self._max_queue_size:
            self._event_queue.pop(0)

        # Notify all registered handlers
        self._notify_handlers(event)

    def emit_function_timing(
        self,
        function_name: str,
        duration: float,
        success: bool,
        args: Optional[str] = None,
        kwargs: Optional[str] = None,
        error: Optional[str] = None,
        error_type: Optional[str] = None,
    ):
        """Emit function timing event"""
        event_type = (
            PerformanceEventType.FUNCTION_TIMING
            if success
            else PerformanceEventType.FUNCTION_TIMING_ERROR
        )

        data = {
            "function": function_name,
            "duration": duration,
            "success": success,
            "args": args,
            "kwargs": kwargs,
        }

        if not success and error:
            data.update({"error": error, "error_type": error_type or "Exception"})

        self.emit_event(event_type, data)

    def emit_request_metrics(
        self,
        endpoint: str,
        method: str,
        duration: float,
        success: bool,
        status_code: Optional[int] = None,
        error: Optional[str] = None,
        cache_hit: bool = False,
    ):
        """Emit request performance event"""
        event_type = (
            PerformanceEventType.REQUEST_COMPLETED
            if success
            else PerformanceEventType.REQUEST_FAILED
        )

        data = {
            "endpoint": endpoint,
            "method": method,
            "duration": duration,
            "success": success,
            "status_code": status_code,
            "cache_hit": cache_hit,
        }

        if not success and error:
            data["error"] = error

        self.emit_event(event_type, data)

    def emit_cache_operation(
        self,
        operation: str,
        cache_hit: bool,
        duration: float,
        key: str,
        cache_name: str = "default",
    ):
        """Emit cache operation event"""
        data = {
            "operation": operation,
            "cache_hit": cache_hit,
            "duration": duration,
            "key": key,
            "cache_name": cache_name,
        }

        self.emit_event(PerformanceEventType.CACHE_OPERATION, data)

    def emit_profiling_result(
        self,
        function_name: str,
        duration: float,
        memory_delta: Optional[float] = None,
        cpu_delta: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """Emit profiling result event"""
        data = {
            "function": function_name,
            "duration": duration,
            "success": success,
            "memory_delta": memory_delta,
            "cpu_delta": cpu_delta,
        }

        if not success and error:
            data["error"] = error

        self.emit_event(PerformanceEventType.PROFILING_RESULT, data)

    def emit_metric_recorded(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[float] = None,
    ):
        """Emit metric recorded event"""
        data = {
            "metric_name": metric_name,
            "value": value,
            "labels": labels or {},
            "timestamp": timestamp or time.time(),
        }

        self.emit_event(PerformanceEventType.METRIC_RECORDED, data)

    def emit_health_check(
        self,
        component: str,
        status: str,
        duration: float,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Emit health check event"""
        data = {
            "component": component,
            "status": status,
            "duration": duration,
            "details": details or {},
        }

        self.emit_event(PerformanceEventType.HEALTH_CHECK, data)

    def emit_system_metric(
        self,
        metric_name: str,
        value: float,
        unit: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Emit system metric event"""
        data = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "metadata": metadata or {},
        }

        self.emit_event(PerformanceEventType.SYSTEM_METRIC, data)

    def register_handler(self, event_type: PerformanceEventType, handler: Callable):
        """Register a handler for a specific event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def register_global_handler(self, handler: Callable):
        """Register a handler for all event types"""
        self._global_handlers.append(handler)

    def unregister_handler(self, event_type: PerformanceEventType, handler: Callable):
        """Unregister a handler for a specific event type"""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass

    def unregister_global_handler(self, handler: Callable):
        """Unregister a global handler"""
        try:
            self._global_handlers.remove(handler)
        except ValueError:
            pass

    def _notify_handlers(self, event: PerformanceEvent):
        """Notify all registered handlers of an event"""
        # Notify specific handlers
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    handler(event)
                except Exception:
                    # Never fail if handler is broken
                    pass

        # Notify global handlers
        for handler in self._global_handlers:
            try:
                handler(event)
            except Exception:
                # Never fail if handler is broken
                pass

    async def get_event_history(
        self, event_type: Optional[PerformanceEventType] = None, limit: int = 100
    ) -> List[PerformanceEvent]:
        """Get event history, optionally filtered by type"""
        async with self._lock:
            if event_type:
                filtered_events = [
                    e for e in self._event_queue if e.event_type == event_type
                ]
            else:
                filtered_events = self._event_queue.copy()

            return filtered_events[-limit:]

    def clear_event_history(self):
        """Clear event history"""
        self._event_queue.clear()


# Global event emitter instance
_event_emitter = PerformanceEventEmitter()


def get_event_emitter() -> PerformanceEventEmitter:
    """Get the global event emitter instance"""
    return _event_emitter


def emit_event(
    event_type: PerformanceEventType, data: Dict[str, Any], source: str = "tradata_perf"
):
    """Convenience function to emit events"""
    _event_emitter.emit_event(event_type, data, source)


def emit_function_timing(
    function_name: str,
    duration: float,
    success: bool,
    args: Optional[str] = None,
    kwargs: Optional[str] = None,
    error: Optional[str] = None,
    error_type: Optional[str] = None,
):
    """Convenience function to emit function timing events"""
    _event_emitter.emit_function_timing(
        function_name, duration, success, args, kwargs, error, error_type
    )


def emit_request_metrics(
    endpoint: str,
    method: str,
    duration: float,
    success: bool,
    status_code: Optional[int] = None,
    error: Optional[str] = None,
    cache_hit: bool = False,
):
    """Convenience function to emit request metrics events"""
    _event_emitter.emit_request_metrics(
        endpoint, method, duration, success, status_code, error, cache_hit
    )


def emit_cache_operation(
    operation: str,
    cache_hit: bool,
    duration: float,
    key: str,
    cache_name: str = "default",
):
    """Convenience function to emit cache operation events"""
    _event_emitter.emit_cache_operation(operation, cache_hit, duration, key, cache_name)


def emit_profiling_result(
    function_name: str,
    duration: float,
    memory_delta: Optional[float] = None,
    cpu_delta: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None,
):
    """Convenience function to emit profiling result events"""
    _event_emitter.emit_profiling_result(
        function_name, duration, memory_delta, cpu_delta, success, error
    )


def emit_metric_recorded(
    metric_name: str,
    value: float,
    labels: Optional[Dict[str, str]] = None,
    timestamp: Optional[float] = None,
):
    """Convenience function to emit metric recorded events"""
    _event_emitter.emit_metric_recorded(metric_name, value, labels, timestamp)


def emit_health_check(
    component: str,
    status: str,
    duration: float,
    details: Optional[Dict[str, Any]] = None,
):
    """Convenience function to emit health check events"""
    _event_emitter.emit_health_check(component, status, duration, details)


def emit_system_metric(
    metric_name: str,
    value: float,
    unit: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Convenience function to emit system metric events"""
    _event_emitter.emit_system_metric(metric_name, value, unit, metadata)


def register_handler(event_type: PerformanceEventType, handler: Callable):
    """Convenience function to register event handlers"""
    _event_emitter.register_handler(event_type, handler)


def register_global_handler(handler: Callable):
    """Convenience function to register global event handlers"""
    _event_emitter.register_global_handler(handler)
