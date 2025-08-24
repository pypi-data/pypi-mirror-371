"""
Health checking functionality for system and service monitoring.
Provides comprehensive health status checking for applications and dependencies.
"""

import time
import psutil
from typing import Dict, Any, Optional, List, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from .event_system import emit_health_check


class HealthStatus(Enum):
    """Health status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check result"""

    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class HealthResult:
    """Overall health check result"""

    status: HealthStatus
    timestamp: datetime
    checks: List[HealthCheck]
    overall_health: bool
    summary: Dict[str, Any]


class HealthChecker:
    """System and service health monitoring"""

    def __init__(self):
        self.health_checks: Dict[str, Callable[[], Awaitable[HealthCheck]]] = {}
        self.last_check_time: Optional[datetime] = None
        self.check_results: List[HealthResult] = []
        self.max_history: int = 100

        # Note: logger.info is async but we can't await in __init__
        pass

    def register_health_check(
        self, name: str, check_func: Callable[[], Awaitable[HealthCheck]]
    ) -> None:
        """Register a new health check function"""
        self.health_checks[name] = check_func
        # Emit health check registration event
        emit_health_check(
            component=name,
            status="registered",
            duration=0.0,
            details={"operation": "register", "step": "health_check"},
        )

    def register_simple_health_check(
        self,
        name: str,
        check_func: Callable[[], Awaitable[bool]],
        message: str = "Health check completed",
    ) -> None:
        """Register a simple health check that returns boolean"""

        async def wrapped_check() -> HealthCheck:
            start_time = time.time()
            try:
                is_healthy = await check_func()
                duration = (time.time() - start_time) * 1000

                return HealthCheck(
                    name=name,
                    status=(
                        HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY
                    ),
                    message=message,
                    timestamp=datetime.now(),
                    duration_ms=duration,
                    details={"healthy": is_healthy},
                )
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                return HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(e)}",
                    timestamp=datetime.now(),
                    duration_ms=duration,
                    error=str(e),
                    details={"healthy": False},
                )

        self.register_health_check(name, wrapped_check)

    async def run_all_health_checks(self) -> HealthResult:
        """Run all registered health checks"""
        # Run health checks
        checks: List[HealthCheck] = []
        for name, check_func in self.health_checks.items():
            try:
                check_result: HealthCheck = await self._run_single_check(
                    name, check_func
                )
                checks.append(check_result)
            except Exception as e:
                checks.append(
                    HealthCheck(
                        name="unknown",
                        status=HealthStatus.UNHEALTHY,
                        message=f"Health check execution failed: {str(e)}",
                        timestamp=datetime.now(),
                        duration_ms=0,
                        error=str(e),
                    )
                )

        # Determine overall health
        overall_health = all(check.status == HealthStatus.HEALTHY for check in checks)

        # Determine overall status
        if overall_health:
            status = HealthStatus.HEALTHY
        elif any(check.status == HealthStatus.UNHEALTHY for check in checks):
            status = HealthStatus.UNHEALTHY
        elif any(check.status == HealthStatus.DEGRADED for check in checks):
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNKNOWN

        # Create summary
        summary: Dict[str, Any] = {
            "total_checks": len(checks),
            "healthy_checks": len(
                [c for c in checks if c.status == HealthStatus.HEALTHY]
            ),
            "degraded_checks": len(
                [c for c in checks if c.status == HealthStatus.DEGRADED]
            ),
            "unhealthy_checks": len(
                [c for c in checks if c.status == HealthStatus.UNHEALTHY]
            ),
            "unknown_checks": len(
                [c for c in checks if c.status == HealthStatus.UNKNOWN]
            ),
            "total_duration_ms": sum(c.duration_ms for c in checks),
            "avg_duration_ms": (
                sum(c.duration_ms for c in checks) / len(checks) if checks else 0
            ),
        }

        result: HealthResult = HealthResult(
            status=status,
            timestamp=datetime.now(),
            checks=checks,
            overall_health=overall_health,
            summary=summary,
        )

        # Store result
        self.last_check_time = result.timestamp
        self.check_results.append(result)

        # Maintain history size
        if len(self.check_results) > self.max_history:
            self.check_results = self.check_results[-self.max_history :]

        # Emit health check completion event
        emit_health_check(
            component="health_checker",
            status=status.value,
            duration=0.0,
            details={
                "operation": "health_check",
                "step": "complete",
                "overall_health": overall_health,
                "total_checks": summary["total_checks"],
                "healthy_checks": summary["healthy_checks"],
                "unhealthy_checks": summary["unhealthy_checks"],
            },
        )

        return result

    async def _run_single_check(
        self, name: str, check_func: Callable[[], Awaitable[HealthCheck]]
    ) -> HealthCheck:
        """Run a single health check with error handling"""
        try:
            return await check_func()
        except Exception as e:
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check execution failed: {str(e)}",
                timestamp=datetime.now(),
                duration_ms=0,
                error=str(e),
            )

    async def get_health_status(self) -> HealthResult:
        """Get current health status (run checks if needed)"""
        # If we haven't run checks recently or don't have any results, run them now
        if (
            self.last_check_time is None
            or datetime.now() - self.last_check_time > timedelta(minutes=5)
            or not self.check_results
        ):
            return await self.run_all_health_checks()

        return self.check_results[-1]

    def get_health_history(self, hours: int = 24) -> List[HealthResult]:
        """Get health check history for the specified time period"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [result for result in self.check_results if result.timestamp >= cutoff]

    def get_health_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get health summary for the specified time period"""
        history = self.get_health_history(hours)

        if not history:
            return {
                "period_hours": hours,
                "total_checks": 0,
                "health_trend": "unknown",
                "uptime_percentage": 0.0,
            }

        # Calculate uptime percentage
        total_checks = len(history)
        healthy_checks = len([r for r in history if r.overall_health])
        uptime_percentage = (
            (healthy_checks / total_checks * 100) if total_checks > 0 else 0.0
        )

        # Determine health trend
        if len(history) >= 2:
            recent_status = history[-1].status
            previous_status = history[-2].status

            if (
                recent_status == HealthStatus.HEALTHY
                and previous_status != HealthStatus.HEALTHY
            ):
                trend = "improving"
            elif (
                recent_status != HealthStatus.HEALTHY
                and previous_status == HealthStatus.HEALTHY
            ):
                trend = "degrading"
            elif recent_status == previous_status:
                trend = "stable"
            else:
                trend = "fluctuating"
        else:
            trend = "unknown"

        return {
            "period_hours": hours,
            "total_checks": total_checks,
            "healthy_checks": healthy_checks,
            "unhealthy_checks": total_checks - healthy_checks,
            "uptime_percentage": round(uptime_percentage, 2),
            "health_trend": trend,
            "current_status": history[-1].status.value if history else "unknown",
            "last_check_time": history[-1].timestamp.isoformat() if history else None,
        }


# Built-in health checks
async def check_system_resources() -> HealthCheck:
    """Check system resource usage"""
    start_time = time.time()

    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Disk usage
        disk = psutil.disk_usage("/")
        disk_percent = (disk.used / disk.total) * 100

        # Determine health status
        if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
            status = HealthStatus.DEGRADED
            message = "System resources are under high load"
        elif cpu_percent > 80 or memory_percent > 80 or disk_percent > 80:
            status = HealthStatus.DEGRADED
            message = "System resources are under moderate load"
        else:
            status = HealthStatus.HEALTHY
            message = "System resources are healthy"

        duration = (time.time() - start_time) * 1000

        return HealthCheck(
            name="system_resources",
            status=status,
            message=message,
            timestamp=datetime.now(),
            duration_ms=duration,
            details={
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory_percent, 2),
                "disk_percent": round(disk_percent, 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
            },
        )

    except Exception as e:
        duration = (time.time() - start_time) * 1000
        return HealthCheck(
            name="system_resources",
            status=HealthStatus.UNHEALTHY,
            message=f"Failed to check system resources: {str(e)}",
            timestamp=datetime.now(),
            duration_ms=duration,
            error=str(e),
        )


async def check_application_responsiveness() -> HealthCheck:
    """Check if the application is responsive"""
    start_time = time.time()

    try:
        # Simple responsiveness check - just return True for now
        # In a real implementation, this might check if the app can respond to requests
        is_responsive = True
        duration = (time.time() - start_time) * 1000

        return HealthCheck(
            name="application_responsiveness",
            status=HealthStatus.HEALTHY if is_responsive else HealthStatus.UNHEALTHY,
            message=(
                "Application is responsive"
                if is_responsive
                else "Application is not responsive"
            ),
            timestamp=datetime.now(),
            duration_ms=duration,
            details={"responsive": is_responsive},
        )

    except Exception as e:
        duration = (time.time() - start_time) * 1000
        return HealthCheck(
            name="application_responsiveness",
            status=HealthStatus.UNHEALTHY,
            message=f"Failed to check application responsiveness: {str(e)}",
            timestamp=datetime.now(),
            duration_ms=duration,
            error=str(e),
        )


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get global health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()

        # Register built-in health checks
        _health_checker.register_health_check(
            "system_resources", check_system_resources
        )
        _health_checker.register_health_check(
            "application_responsiveness", check_application_responsiveness
        )

    return _health_checker
