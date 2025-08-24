"""
FastAPI logging middleware for Tradata logger
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..core.engine import ModernLoggingEngine
from ..core.logger import get_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """FastAPI logging middleware with trace ID extraction and operation tracking"""

    def __init__(self, app: ASGIApp, engine: ModernLoggingEngine = None):
        super().__init__(app)
        self.engine = engine or ModernLoggingEngine()
        self.logger = get_logger("middleware")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract trace ID from header
        trace_id: str = (
            request.headers.get("X-Trace-ID") or f"auto-{uuid.uuid4().hex[:8]}"
        )

        # Set context variables
        self.engine.trace_id.set(trace_id)
        self.engine.request_id.set(
            f"{int(time.time() * 1000000)}-{uuid.uuid4().hex[:8]}"
        )

        # Log request start with operation and step
        start_time = time.time()
        await self.engine.log(
            "INFO",
            "Request started",
            "Route",
            "Request_Started",
            endpoint=str(request.url.path),
            method=request.method,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            query_params=dict(request.query_params),
            trace_id=trace_id,
        )

        # Process request
        try:
            response: Response = await call_next(request)
            duration = time.time() - start_time

            # Log successful response with operation and step
            await self.engine.log(
                "INFO",
                "Request completed",
                "Route",
                "Response_Completed",
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                response_size_bytes=(
                    len(response.body) if hasattr(response, "body") else 0
                ),
                trace_id=trace_id,
            )

            # Add trace ID to response headers
            if hasattr(response, "headers"):
                response.headers["X-Trace-ID"] = trace_id
                request_id_value = self.engine.request_id.get() or "unknown"
                response.headers["X-Request-ID"] = request_id_value
                response.headers["X-Response-Time"] = f"{duration:.3f}s"

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Log error with operation and step
            await self.engine.log(
                "ERROR",
                "Request failed",
                "Route",
                "Response_Failed",
                endpoint=str(request.url.path),
                method=request.method,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration * 1000, 2),
                trace_id=trace_id,
            )
            raise


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """Performance-focused logging middleware for Tradata logger"""

    def __init__(self, app: ASGIApp, engine: ModernLoggingEngine = None):
        super().__init__(app)
        self.engine = engine or ModernLoggingEngine()
        self.logger = get_logger("performance_middleware")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Extract request information
        endpoint = request.url.path
        method = request.method
        user_agent = request.headers.get("user-agent")
        ip_address = request.client.host if request.client else None

        # Extract trace ID
        trace_id: str = (
            request.headers.get("X-Trace-ID") or f"auto-{uuid.uuid4().hex[:8]}"
        )

        # Set context
        self.engine.trace_id.set(trace_id)
        self.engine.request_id.set(f"{int(start_time * 1000000)}")

        try:
            # Process the request
            response: Response = await call_next(request)

            # Calculate response time
            response_time = time.time() - start_time

            # Determine if it was a cache hit
            cache_hit = False
            if hasattr(response, "headers"):
                cache_hit = response.headers.get("X-Cache") == "HIT"

            # Log successful request metrics
            await self.engine.log(
                "INFO",
                "Request completed successfully",
                "Performance",
                "Request_Completed",
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                response_time=response_time,
                cache_hit=cache_hit,
                user_agent=user_agent,
                ip_address=ip_address,
                trace_id=trace_id,
            )

            # Add performance headers
            if hasattr(response, "headers"):
                response.headers["X-Response-Time"] = f"{response_time:.3f}s"
                request_id_value = self.engine.request_id.get() or "unknown"
                response.headers["X-Request-ID"] = request_id_value
                response.headers["X-Trace-ID"] = trace_id

            return response

        except Exception as e:
            # Calculate response time for failed requests
            response_time = time.time() - start_time

            # Log failed request metrics
            await self.engine.log(
                "ERROR",
                "Request failed",
                "Performance",
                "Request_Failed",
                endpoint=endpoint,
                method=method,
                status_code=500,
                response_time=response_time,
                cache_hit=False,
                error=str(e),
                user_agent=user_agent,
                ip_address=ip_address,
                trace_id=trace_id,
            )

            # Re-raise the exception
            raise
