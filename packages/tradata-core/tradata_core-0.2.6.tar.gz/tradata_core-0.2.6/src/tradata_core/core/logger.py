"""
Net-new logger interface - completely fresh design with operation and step tracking
"""

from typing import Any, Dict, Optional
from .engine import ModernLoggingEngine
from ..config.settings import LogConfig


class ModernLogger:
    """Net-new logger with trace ID, operation, and step tracking as first-class citizens"""

    def __init__(self, name: str, engine: ModernLoggingEngine):
        self.name = name
        self.engine = engine
        # Performance event handler registration system
        self.performance_handlers: dict[str, Any] = {}
        self.event_processors: dict[str, list] = {}

    def register_performance_handler(self, event_type: str, handler):
        """Allow performance libraries to register event handlers."""
        if event_type not in self.event_processors:
            self.event_processors[event_type] = []
        self.event_processors[event_type].append(handler)

    def emit_performance_event(self, event_type: str, data: dict):
        """Process performance events from external systems."""
        if event_type in self.event_processors:
            for handler in self.event_processors[event_type]:
                try:
                    result = handler(event_type, data)
                    # Handle async handlers
                    if hasattr(result, "__await__"):
                        # Schedule async handler execution
                        import asyncio

                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                asyncio.create_task(result)
                            else:
                                loop.run_until_complete(result)
                        except RuntimeError:
                            # No event loop, create a new one
                            asyncio.run(result)
                except Exception as e:
                    # Log the error but don't break
                    self._log_internal_error(f"Performance handler failed: {e}")

    def _log_internal_error(self, message: str):
        """Internal error logging that doesn't create loops."""
        # Use basic logging, not the full system
        import logging

        logging.error(f"[Tradata-Core] {message}")

    async def info(self, message: str, operation: str, step: str, **kwargs):
        """Info logging with automatic trace ID, operation, and step tracking"""
        await self.engine.log(
            "INFO", message, operation, step, logger=self.name, **kwargs
        )

    async def debug(self, message: str, operation: str, step: str, **kwargs):
        """Debug logging with automatic trace ID, operation, and step tracking"""
        # Check if debug logging is enabled
        if not self.engine.is_debug_enabled():
            return  # Early return if debug is disabled

        await self.engine.log(
            "DEBUG", message, operation, step, logger=self.name, **kwargs
        )

    async def warning(self, message: str, operation: str, step: str, **kwargs):
        """Warning logging with automatic trace ID, operation, and step tracking"""
        await self.engine.log(
            "WARNING", message, operation, step, logger=self.name, **kwargs
        )

    async def error(self, message: str, operation: str, step: str, **kwargs):
        """Error logging with automatic trace ID, operation, and step tracking"""
        await self.engine.log(
            "ERROR", message, operation, step, logger=self.name, **kwargs
        )

    async def critical(self, message: str, operation: str, step: str, **kwargs):
        """Critical logging with automatic trace ID, operation, and step tracking"""
        await self.engine.log(
            "CRITICAL", message, operation, step, logger=self.name, **kwargs
        )

    def with_context(self, **context):
        """Add context to all subsequent log calls"""
        return ContextualLogger(self, context)

    def track_client(self, client_name: str):
        """Track which client is being used for this operation"""
        self.engine.client_used.set(client_name)
        return self

    async def log_cache_operation(
        self,
        step: str,
        cache_hit: bool,
        cache_key: str,
        duration_ms: float = None,
        **kwargs,
    ):
        """Log cache operations with structured key/value pairs"""
        extra = {"cacheHit": cache_hit, "cacheKey": cache_key, **kwargs}
        if duration_ms:
            extra["duration_ms"] = duration_ms

        # Remove any conflicting keys that match method parameters
        if "operation" in extra:
            del extra["operation"]
        if "step" in extra:
            del extra["step"]

        return await self.info("Cache operation", "Cache", step, **extra)

    async def log_client_operation(
        self,
        step: str,
        client_name: str,
        operation_name: str,
        duration_ms: float = None,
        **kwargs,
    ):
        """Log client operations with structured key/value pairs"""
        extra = {"client": client_name, "operation_name": operation_name, **kwargs}
        if duration_ms:
            extra["duration_ms"] = duration_ms

        # Remove any conflicting keys that match method parameters
        if "operation" in extra:
            del extra["operation"]
        if "step" in extra:
            del extra["step"]

        return await self.info(
            f"Client operation: {operation_name}", "Client", step, **extra
        )

    async def log_data_processing(self, step: str, **kwargs):
        """Log data processing operations"""
        return await self.info(
            "Data processing operation", "DataProcessing", step, **kwargs
        )

    async def log_business_logic(self, step: str, **kwargs):
        """Log business logic operations"""
        return await self.info(
            "Business logic operation", "BusinessLogic", step, **kwargs
        )

    async def log_error_handling(self, step: str, **kwargs):
        """Log error handling operations"""
        return await self.info(
            "Error handling operation", "ErrorHandling", step, **kwargs
        )

    async def log_performance(self, step: str, **kwargs):
        """Log performance operations"""
        return await self.info("Performance operation", "Performance", step, **kwargs)

    async def log_mathematics(
        self, step: str, mathematical_principle: str = None, **kwargs
    ):
        """Log mathematics operations with mathematical principle tracking"""
        extra = {"mathematical_principle": mathematical_principle, **kwargs}
        return await self.info("Mathematics operation", "Mathematics", step, **extra)


class PerformanceEventLogger:
    """Handles performance events from external performance libraries."""

    def __init__(self, logger: ModernLogger):
        self.logger = logger

    async def handle_function_timing(self, event_type: str, data: dict):
        """Handle function timing events from performance library."""
        if data.get("success"):
            await self.logger.info(
                f"Function {data['function']} completed in {data['duration']:.3f}s",
                "Performance",
                "Function_Completed",
                function=data["function"],
                duration=data["duration"],
                event_type=event_type,
            )
        else:
            await self.logger.error(
                f"Function {data['function']} failed after {data['duration']:.3f}s: {data.get('error')}",
                "Performance",
                "Function_Failed",
                function=data["function"],
                duration=data["duration"],
                error=data.get("error"),
                event_type=event_type,
            )

    async def handle_request_metrics(self, event_type: str, data: dict):
        """Handle request performance events."""
        if data.get("success"):
            await self.logger.info(
                f"Request {data['method']} {data['endpoint']} completed in {data['duration']:.3f}s",
                "Performance",
                "Request_Completed",
                endpoint=data["endpoint"],
                method=data["method"],
                duration=data["duration"],
                event_type=event_type,
            )
        else:
            await self.logger.error(
                f"Request {data['method']} {data['endpoint']} failed after {data['duration']:.3f}s: {data.get('error')}",
                "Performance",
                "Request_Failed",
                endpoint=data["endpoint"],
                method=data["method"],
                duration=data["duration"],
                error=data.get("error"),
                event_type=event_type,
            )

    async def handle_cache_operation(self, event_type: str, data: dict):
        """Handle cache performance events."""
        await self.logger.log_cache_operation(
            step=data.get("operation", "cache_operation"),
            cache_hit=data.get("cache_hit", False),
            cache_key=data.get("key", "unknown"),
            duration_ms=data.get("duration", 0) * 1000,  # Convert to ms
            event_type=event_type,
        )

    async def handle_profiling_result(self, event_type: str, data: dict):
        """Handle profiling result events."""
        function_name = data.get("function", "unknown")
        duration = data.get("duration", 0.0)
        memory_delta = data.get("memory_delta")
        cpu_delta = data.get("cpu_delta")
        success = data.get("success", True)
        error = data.get("error")

        if success:
            details = []
            if memory_delta is not None:
                details.append(f"memory: {memory_delta:+.2f}MB")
            if cpu_delta is not None:
                details.append(f"CPU: {cpu_delta:+.2f}%")

            detail_str = f" ({', '.join(details)})" if details else ""

            await self.logger.info(
                f"Profiling: {function_name} completed in {duration:.3f}s{detail_str}",
                "Performance",
                "Profiling_Completed",
                function=function_name,
                duration=duration,
                memory_delta=memory_delta,
                cpu_delta=cpu_delta,
                event_type=event_type,
            )
        else:
            await self.logger.error(
                f"Profiling: {function_name} failed after {duration:.3f}s: {error}",
                "Performance",
                "Profiling_Failed",
                function=function_name,
                duration=duration,
                error=error,
                event_type=event_type,
            )

    async def handle_metric_recorded(self, event_type: str, data: dict):
        """Handle metric recorded events."""
        metric_name = data.get("metric_name", "unknown")
        value = data.get("value", 0.0)
        labels = data.get("labels", {})
        timestamp = data.get("timestamp")

        label_str = (
            f" [{', '.join(f'{k}={v}' for k, v in labels.items())}]" if labels else ""
        )

        await self.logger.info(
            f"Metric recorded: {metric_name} = {value}{label_str}",
            "Performance",
            "Metric_Recorded",
            metric_name=metric_name,
            value=value,
            labels=labels,
            timestamp=timestamp,
            event_type=event_type,
        )

    async def handle_health_check(self, event_type: str, data: dict):
        """Handle health check events."""
        component = data.get("component", "unknown")
        status = data.get("status", "unknown")
        duration = data.get("duration", 0.0)
        details = data.get("details", {})

        if status == "healthy":
            await self.logger.info(
                f"Health check: {component} is HEALTHY ({duration:.3f}s)",
                "Health",
                "Check_Healthy",
                component=component,
                status=status,
                duration=duration,
                details=details,
                event_type=event_type,
            )
        elif status == "degraded":
            await self.logger.warning(
                f"Health check: {component} is DEGRADED ({duration:.3f}s)",
                "Health",
                "Check_Degraded",
                component=component,
                status=status,
                duration=duration,
                details=details,
                event_type=event_type,
            )
        else:
            await self.logger.error(
                f"Health check: {component} is UNHEALTHY ({duration:.3f}s)",
                "Health",
                "Check_Unhealthy",
                component=component,
                status=status,
                duration=duration,
                details=details,
                event_type=event_type,
            )

    async def handle_system_metric(self, event_type: str, data: dict):
        """Handle system metric events."""
        metric_name = data.get("metric_name", "unknown")
        value = data.get("value", 0.0)
        unit = data.get("unit", "")
        metadata = data.get("metadata", {})

        unit_str = f" {unit}" if unit else ""

        await self.logger.info(
            f"System metric: {metric_name} = {value}{unit_str}",
            "Performance",
            "System_Metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            metadata=metadata,
            event_type=event_type,
        )

    async def handle_database_query(self, event_type: str, data: dict):
        """Handle database query events."""
        query = data.get("query", "unknown")
        duration = data.get("duration", 0.0)
        success = data.get("success", True)
        rows_affected = data.get("rows_affected")

        if success:
            rows_str = f" ({rows_affected} rows)" if rows_affected is not None else ""
            await self.logger.info(
                f"Database query completed in {duration:.3f}s{rows_str}",
                "Database",
                "Query_Completed",
                query=query,
                duration=duration,
                rows_affected=rows_affected,
                event_type=event_type,
            )
        else:
            await self.logger.error(
                f"Database query failed after {duration:.3f}s",
                "Database",
                "Query_Failed",
                query=query,
                duration=duration,
                event_type=event_type,
            )

    async def handle_external_api_call(self, event_type: str, data: dict):
        """Handle external API call events."""
        endpoint = data.get("endpoint", "unknown")
        method = data.get("method", "unknown")
        duration = data.get("duration", 0.0)
        success = data.get("success", True)
        status_code = data.get("status_code")

        if success:
            status_str = f" (HTTP {status_code})" if status_code else ""
            await self.logger.info(
                f"External API {method} {endpoint} completed in {duration:.3f}s{status_str}",
                "ExternalAPI",
                "Call_Completed",
                endpoint=endpoint,
                method=method,
                duration=duration,
                status_code=status_code,
                event_type=event_type,
            )
        else:
            await self.logger.error(
                f"External API {method} {endpoint} failed after {duration:.3f}s",
                "ExternalAPI",
                "Call_Failed",
                endpoint=endpoint,
                method=method,
                duration=duration,
                event_type=event_type,
            )

    async def handle_background_task(self, event_type: str, data: dict):
        """Handle background task events."""
        task_name = data.get("task_name", "unknown")
        duration = data.get("duration", 0.0)
        success = data.get("success", True)

        if success:
            await self.logger.info(
                f"Background task {task_name} completed in {duration:.3f}s",
                "BackgroundTask",
                "Task_Completed",
                task_name=task_name,
                duration=duration,
                event_type=event_type,
            )
        else:
            await self.logger.error(
                f"Background task {task_name} failed after {duration:.3f}s",
                "BackgroundTask",
                "Task_Failed",
                task_name=task_name,
                duration=duration,
                event_type=event_type,
            )


class ContextualLogger:
    """Logger with additional context"""

    def __init__(self, logger: ModernLogger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context

    async def info(self, message: str, operation: str, step: str, **kwargs):
        """Info with context"""
        await self.logger.info(message, operation, step, **{**self.context, **kwargs})

    async def debug(self, message: str, operation: str, step: str, **kwargs):
        """Debug with context"""
        await self.logger.debug(message, operation, step, **{**self.context, **kwargs})

    async def warning(self, message: str, operation: str, step: str, **kwargs):
        """Warning with context"""
        await self.logger.warning(
            message, operation, step, **{**self.context, **kwargs}
        )

    async def error(self, message: str, operation: str, step: str, **kwargs):
        """Error with context"""
        await self.logger.error(message, operation, step, **{**self.context, **kwargs})

    async def critical(self, message: str, operation: str, step: str, **kwargs):
        """Critical with context"""
        await self.logger.critical(
            message, operation, step, **{**self.context, **kwargs}
        )


# Global logging engine instance
_logging_engine: Optional[ModernLoggingEngine] = None


def set_logging_engine(engine: ModernLoggingEngine):
    """Set the global logging engine instance"""
    global _logging_engine
    _logging_engine = engine


def get_logging_engine() -> ModernLoggingEngine:
    """Get the global logging engine instance"""
    global _logging_engine
    if _logging_engine is None:
        _logging_engine = ModernLoggingEngine()
    return _logging_engine


def get_logger(name: str) -> ModernLogger:
    """Get a logger instance for the specified name"""
    engine = get_logging_engine()
    return ModernLogger(name, engine)


def setup_logging(config: Optional[LogConfig] = None):
    """Setup logging with optional configuration"""
    global _logging_engine

    if config is None:
        # Use environment configuration if none provided
        from ..config.settings import ENV_CONFIG

        config = ENV_CONFIG

    # Create new engine with configuration
    _logging_engine = ModernLoggingEngine(config)
    return _logging_engine


# Context setting functions
def set_trace_id(trace_id: str):
    """Set the trace ID for the current context"""
    engine = get_logging_engine()
    engine.trace_id.set(trace_id)


def set_request_id(request_id: str):
    """Set the request ID for the current context"""
    engine = get_logging_engine()
    engine.request_id.set(request_id)


def set_client(client_name: str):
    """Set the client being used for the current context"""
    engine = get_logging_engine()
    engine.client_used.set(client_name)


def get_call_summary() -> Dict[str, Any]:
    """Get the current call summary"""
    engine = get_logging_engine()
    return engine.get_call_summary()


def get_debug_status() -> Dict[str, Any]:
    """Get debug configuration status"""
    engine = get_logging_engine()
    return engine.get_debug_status()


# Convenience function for quick logging
async def log(level: str, message: str, operation: str, step: str, **kwargs):
    """Quick logging function for simple use cases"""
    engine = get_logging_engine()
    await engine.log(level, message, operation, step, **kwargs)


# Convenience function for quick logging without async
def log_sync(level: str, message: str, operation: str, step: str, **kwargs):
    """Synchronous logging function for simple use cases"""
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, schedule the log
            asyncio.create_task(log(level, message, operation, step, **kwargs))
        else:
            # If no loop is running, run it
            asyncio.run(log(level, message, operation, step, **kwargs))
    except RuntimeError:
        # No event loop, create a new one
        asyncio.run(log(level, message, operation, step, **kwargs))


# Performance event integration functions
def get_performance_logger(name: str) -> PerformanceEventLogger:
    """Get a performance event logger for the specified name."""
    logger = get_logger(name)
    return PerformanceEventLogger(logger)


def setup_performance_integration(logger_name: str = None):
    """Setup performance event integration for a logger."""
    if logger_name is None:
        logger_name = "performance_integration"

    logger = get_logger(logger_name)
    perf_logger = PerformanceEventLogger(logger)

    # Register default performance event handlers
    logger.register_performance_handler(
        "function_timing", perf_logger.handle_function_timing
    )
    logger.register_performance_handler(
        "function_timing_error", perf_logger.handle_function_timing
    )
    logger.register_performance_handler(
        "request_completed", perf_logger.handle_request_metrics
    )
    logger.register_performance_handler(
        "request_failed", perf_logger.handle_request_metrics
    )
    logger.register_performance_handler(
        "cache_operation", perf_logger.handle_cache_operation
    )
    logger.register_performance_handler(
        "profiling_result", perf_logger.handle_profiling_result
    )
    logger.register_performance_handler(
        "metric_recorded", perf_logger.handle_metric_recorded
    )
    logger.register_performance_handler("health_check", perf_logger.handle_health_check)
    logger.register_performance_handler(
        "system_metric", perf_logger.handle_system_metric
    )
    logger.register_performance_handler(
        "database_query", perf_logger.handle_database_query
    )
    logger.register_performance_handler(
        "external_api_call", perf_logger.handle_external_api_call
    )
    logger.register_performance_handler(
        "background_task", perf_logger.handle_background_task
    )

    return logger, perf_logger
