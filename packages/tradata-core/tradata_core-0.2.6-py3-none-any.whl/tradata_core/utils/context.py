"""Context managers for Tradata logging"""

import time
import uuid
from typing import Optional
from contextlib import asynccontextmanager
from ..core.logger import get_logger, set_trace_id, set_client, set_request_id


class LoggingContext:
    """Context manager for logging operations"""

    def __init__(
        self,
        operation: str,
        step: str = "start",
        client: Optional[str] = None,
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        self.operation = operation
        self.step = step
        self.client = client
        self.trace_id = trace_id
        self.request_id = request_id
        self.start_time = None
        self.logger = get_logger(__name__)

    async def __aenter__(self):
        """Enter the logging context"""
        self.start_time = time.time()

        # Set context variables
        if self.trace_id:
            set_trace_id(self.trace_id)
        if self.client:
            set_client(self.client)
        if self.request_id:
            set_request_id(self.request_id)
        else:
            set_request_id(f"ctx-{uuid.uuid4().hex[:8]}")

        # Log context start
        await self.logger.info(
            f"Context started: {self.operation}", self.operation, f"{self.step}_Started"
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the logging context"""
        duration_ms = (time.time() - self.start_time) * 1000

        if exc_type is None:
            # Success case
            await self.logger.info(
                f"Context completed: {self.operation}",
                self.operation,
                f"{self.step}_Completed",
                duration_ms=duration_ms,
                success=True,
            )
        else:
            # Error case
            await self.logger.error(
                f"Context failed: {self.operation}",
                self.operation,
                f"{self.step}_Failed",
                duration_ms=duration_ms,
                success=False,
                error=str(exc_val),
                error_type=exc_type.__name__,
            )

    def add_context(self, **context):
        """Add additional context to the logging context"""
        for key, value in context.items():
            setattr(self, key, value)
        return self


@asynccontextmanager
async def logging_context(
    operation: str,
    step: str = "start",
    client: Optional[str] = None,
    trace_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **context,
):
    """Async context manager for logging operations"""
    ctx = LoggingContext(operation, step, client, trace_id, request_id)
    ctx.add_context(**context)

    async with ctx:
        yield ctx


class RequestContext:
    """Context manager for request-level logging"""

    def __init__(
        self,
        endpoint: str,
        method: str = "GET",
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        trace_id: Optional[str] = None,
    ):
        self.endpoint = endpoint
        self.method = method
        self.client_ip = client_ip
        self.user_agent = user_agent
        self.trace_id = trace_id or f"req-{uuid.uuid4().hex[:8]}"
        self.start_time = None
        self.logger = get_logger(__name__)

    async def __aenter__(self):
        """Enter the request context"""
        self.start_time = time.time()

        # Set context variables
        set_trace_id(self.trace_id)
        set_request_id(f"req-{uuid.uuid4().hex[:8]}")

        # Log request start
        await self.logger.info(
            f"Request started: {self.method} {self.endpoint}",
            "Request",
            "Started",
            endpoint=self.endpoint,
            method=self.method,
            client_ip=self.client_ip,
            user_agent=self.user_agent,
            trace_id=self.trace_id,
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the request context"""
        duration_ms = (time.time() - self.start_time) * 1000

        if exc_type is None:
            # Success case
            await self.logger.info(
                f"Request completed: {self.method} {self.endpoint}",
                "Request",
                "Completed",
                endpoint=self.endpoint,
                method=self.method,
                duration_ms=duration_ms,
                success=True,
                trace_id=self.trace_id,
            )
        else:
            # Error case
            await self.logger.error(
                f"Request failed: {self.method} {self.endpoint}",
                "Request",
                "Failed",
                endpoint=self.endpoint,
                method=self.method,
                duration_ms=duration_ms,
                success=False,
                error=str(exc_val),
                error_type=exc_type.__name__,
                trace_id=self.trace_id,
            )


@asynccontextmanager
async def request_context(
    endpoint: str,
    method: str = "GET",
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    trace_id: Optional[str] = None,
):
    """Async context manager for request-level logging"""
    ctx = RequestContext(endpoint, method, client_ip, user_agent, trace_id)

    async with ctx:
        yield ctx
