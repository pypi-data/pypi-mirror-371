"""
Logging decorators for clean, minimal API implementations.
Provides one-liner logging for API endpoints while maintaining comprehensive observability.
"""

import time
import uuid
import functools
from typing import Callable
from ..core.logger import get_logger, set_trace_id, set_client, set_request_id

logger = get_logger(__name__)


def log_endpoint(
    endpoint_name: str,
    algorithm_type: str = None,
    client_service: str = None,
    set_performance_headers: bool = True,
):
    """
    Decorator that provides comprehensive end-to-end logging for API endpoints.

    Usage:
        @log_endpoint("/quotes/{symbol}", "quote_retrieval", "quotes_service")
        async def get_quote(symbol: str, resp: Response = None):
            # Your endpoint logic here - super clean!
            return {"symbol": symbol, "price": 150.00}

    This decorator automatically handles:
    - Request timing and context
    - Service call logging
    - Response logging
    - Error handling
    - Performance headers
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract response object if present
            resp = kwargs.get("resp")

            # Start timing
            start_time = time.time()

            # Set up logging context
            trace_id = kwargs.get("trace_id")
            if trace_id:
                set_trace_id(trace_id)

            client_name = client_service or func.__module__.split(".")[-1] + "_service"
            set_client(client_name)
            set_request_id("req-" + str(uuid.uuid4()))

            # Log request start
            await logger.log_data_processing(
                step="Request_Started", endpoint=endpoint_name
            )

            try:
                # Service call initiation
                service_start_time = time.time()
                await logger.log_data_processing(
                    step="Service_Call_Initiated",
                    endpoint=endpoint_name,
                    algorithm_type=algorithm_type or "api_operation",
                )

                # Execute the actual endpoint function
                result = await func(*args, **kwargs)

                # Calculate timing
                service_duration_ms = (time.time() - service_start_time) * 1000
                total_duration_ms = (time.time() - start_time) * 1000

                # Log service completion
                await logger.log_data_processing(
                    step="Service_Call_Completed",
                    endpoint=endpoint_name,
                    algorithm_type=algorithm_type or "api_operation",
                    service_duration_ms=service_duration_ms,
                )

                # Log response ready
                response_size = len(str(result)) if result else 0
                await logger.log_data_processing(
                    step="Response_Ready",
                    endpoint=endpoint_name,
                    response_size=response_size,
                    total_duration_ms=total_duration_ms,
                    service_duration_ms=service_duration_ms,
                    success=True,
                    status_code=200,
                )

                # Set performance headers if requested
                if set_performance_headers and resp:
                    resp.headers["X-Response-Time"] = f"{total_duration_ms:.2f}ms"
                    resp.headers["X-Endpoint"] = endpoint_name

                # Log performance complete
                await logger.log_performance(
                    step="Request_Completed",
                    total_duration_ms=total_duration_ms,
                    service_duration_ms=service_duration_ms,
                    external_api_calls=0,
                    response_code=200,
                    endpoint=endpoint_name,
                    success=True,
                )

                return result

            except Exception as e:
                # Comprehensive error logging
                error_duration_ms = (time.time() - start_time) * 1000
                await logger.log_error_handling(
                    step="Unexpected_Error",
                    endpoint=endpoint_name,
                    error=str(e),
                    error_type=type(e).__name__,
                    error_duration_ms=error_duration_ms,
                    success=False,
                    status_code=500,
                    algorithm_type=algorithm_type or "api_operation",
                )

                # Log final error metrics
                await logger.log_performance(
                    step="Request_Failed",
                    total_duration_ms=error_duration_ms,
                    service_duration_ms=0,
                    external_api_calls=0,
                    response_code=500,
                    endpoint=endpoint_name,
                    success=False,
                    error_occurred=True,
                    error_type=type(e).__name__,
                )

                raise

        return wrapper

    return decorator


def log_with_context(
    endpoint_name: str, algorithm_type: str = None, client_service: str = None
):
    """
    Context manager for logging that can be used with 'with' statements.

    Usage:
        async with log_with_context("/quotes/{symbol}", "quote_retrieval"):
            # Your endpoint logic here
            result = await service.get_quote(symbol)
            return result
    """

    class LoggingContext:
        def __init__(self, endpoint: str, algorithm: str = None, client: str = None):
            self.endpoint = endpoint
            self.algorithm = algorithm or "api_operation"
            self.client = client or "api_service"
            self.start_time = None
            self.service_start_time = None

        async def __aenter__(self):
            self.start_time = time.time()
            self.service_start_time = time.time()

            # Set up logging context
            set_client(self.client)
            set_request_id("req-" + str(uuid.uuid4()))

            await logger.log_data_processing(
                step="Request_Started", endpoint=self.endpoint
            )

            await logger.log_data_processing(
                step="Service_Call_Initiated",
                endpoint=self.endpoint,
                algorithm_type=self.algorithm,
            )

            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                # Success case
                service_duration_ms = (time.time() - self.service_start_time) * 1000
                total_duration_ms = (time.time() - self.start_time) * 1000

                await logger.log_data_processing(
                    step="Service_Call_Completed",
                    endpoint=self.endpoint,
                    algorithm_type=self.algorithm,
                    service_duration_ms=service_duration_ms,
                )

                await logger.log_performance(
                    step="Request_Completed",
                    total_duration_ms=total_duration_ms,
                    service_duration_ms=service_duration_ms,
                    external_api_calls=0,
                    response_code=200,
                    endpoint=self.endpoint,
                    success=True,
                )
            else:
                # Error case
                error_duration_ms = (time.time() - self.start_time) * 1000

                await logger.log_error_handling(
                    step="Unexpected_Error",
                    endpoint=self.endpoint,
                    error=str(exc_val),
                    error_type=exc_type.__name__,
                    error_duration_ms=error_duration_ms,
                    success=False,
                    status_code=500,
                    algorithm_type=self.algorithm,
                )

                await logger.log_performance(
                    step="Request_Failed",
                    total_duration_ms=error_duration_ms,
                    service_duration_ms=0,
                    external_api_calls=0,
                    response_code=500,
                    endpoint=self.endpoint,
                    success=False,
                    error_occurred=True,
                    error_type=exc_type.__name__,
                )

    return LoggingContext(endpoint_name, algorithm_type, client_service)


def log_cache_operation(cache_type: str, cache_name: str, operation: str, **kwargs):
    """
    Decorator for logging cache operations with automatic context.

    Usage:
        @log_cache_operation("redis", "quote_cache", "get")
        async def get_cached_quote(symbol: str):
            # Cache logic here
            return cached_data
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                duration_ms = (time.time() - start_time) * 1000
                await logger.log_cache_operation(
                    step=f"Cache_{operation.capitalize()}_Success",
                    cache_hit=True,  # Success means cache hit or operation succeeded
                    cache_key=f"{cache_name}:{operation}",
                    duration_ms=duration_ms,
                    cache_type=cache_type,
                    cache_name=cache_name,
                    operation=operation,
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                await logger.log_cache_operation(
                    step=f"Cache_{operation.capitalize()}_Failed",
                    cache_hit=False,  # Failure means cache miss or operation failed
                    cache_key=f"{cache_name}:{operation}",
                    duration_ms=duration_ms,
                    error=str(e),
                    cache_type=cache_type,
                    cache_name=cache_name,
                    operation=operation,
                )
                raise

        return wrapper

    return decorator


def log_performance(operation: str, step: str):
    """
    Decorator for logging performance metrics.

    Usage:
        @log_performance("data_processing", "calculation")
        async def process_data():
            # Data processing logic
            return result
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                duration_ms = (time.time() - start_time) * 1000
                await logger.log_performance(
                    step=step, duration_ms=duration_ms, success=True
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                await logger.log_performance(
                    step=step, duration_ms=duration_ms, success=False, error=str(e)
                )
                raise

        return wrapper

    return decorator
