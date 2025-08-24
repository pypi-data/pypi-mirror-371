"""
Response builder utilities for clean, consistent API responses.
Handles headers, performance metrics, and response formatting.
"""

from typing import Any, Dict, Optional
from fastapi import Response
from fastapi.responses import JSONResponse


class ResponseBuilder:
    """
    Builder pattern for creating consistent API responses with proper headers.

    Usage:
        response = ResponseBuilder("/quotes/{symbol}")
            .with_data({"symbol": "AAPL", "price": 150.00})
            .with_performance_headers(total_duration_ms=45.2)
            .with_cache_headers(cache_hit=True, cache_key="quote:AAPL")
            .build()
    """

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.data: Optional[Any] = None
        self.status_code: int = 200
        self.headers: Dict[str, str] = {}
        self.cache_info: Optional[Dict[str, Any]] = None
        self.performance_info: Optional[Dict[str, Any]] = None

    def with_data(self, data: Any) -> "ResponseBuilder":
        """Set the response data."""
        self.data = data
        return self

    def with_status(self, status_code: int) -> "ResponseBuilder":
        """Set the HTTP status code."""
        self.status_code = status_code
        return self

    def with_headers(self, headers: Dict[str, str]) -> "ResponseBuilder":
        """Add custom headers."""
        self.headers.update(headers)
        return self

    def with_performance_headers(
        self, total_duration_ms: float, **kwargs
    ) -> "ResponseBuilder":
        """Add performance-related headers."""
        self.performance_info = {"total_duration_ms": total_duration_ms, **kwargs}

        self.headers.update(
            {
                "X-Response-Time": f"{total_duration_ms:.2f}ms",
                "X-Endpoint": self.endpoint,
            }
        )

        # Add additional performance headers
        if "service_duration_ms" in kwargs:
            self.headers["X-Service-Time"] = f"{kwargs['service_duration_ms']:.2f}ms"

        if "external_api_calls" in kwargs:
            self.headers["X-External-API-Calls"] = str(kwargs["external_api_calls"])

        return self

    def with_cache_headers(
        self, cache_hit: bool, cache_key: str = None, **kwargs
    ) -> "ResponseBuilder":
        """Add cache-related headers."""
        self.cache_info = {"cache_hit": cache_hit, "cache_key": cache_key, **kwargs}

        self.headers.update(
            {"X-Cache-Hit": str(cache_hit).lower(), "X-Cache-Key": cache_key or "N/A"}
        )

        if "ttl_seconds" in kwargs:
            self.headers["X-Cache-TTL"] = str(kwargs["ttl_seconds"])

        return self

    def with_business_headers(self, **kwargs) -> "ResponseBuilder":
        """Add business-specific headers."""
        for key, value in kwargs.items():
            if value is not None:
                header_key = f"X-{key.replace('_', '-').title()}"
                self.headers[header_key] = str(value)
        return self

    def build(self) -> JSONResponse:
        """Build and return the final JSONResponse."""
        if self.data is None:
            raise ValueError("Response data must be set before building")

        return JSONResponse(
            content=self.data, status_code=self.status_code, headers=self.headers
        )


def create_response(
    data: Any,
    endpoint: str,
    total_duration_ms: float = None,
    cache_hit: bool = None,
    cache_key: str = None,
    **kwargs,
) -> JSONResponse:
    """
    Quick response creation with common headers.

    Usage:
        return create_response(
            data=quote_data,
            endpoint="/quotes/{symbol}",
            total_duration_ms=45.2,
            cache_hit=False,
            symbol="AAPL"
        )
    """
    builder = ResponseBuilder(endpoint).with_data(data)

    if total_duration_ms is not None:
        builder.with_performance_headers(total_duration_ms, **kwargs)

    if cache_hit is not None:
        builder.with_cache_headers(cache_hit, cache_key, **kwargs)

    # Add any additional business headers
    business_headers = {
        k: v
        for k, v in kwargs.items()
        if k not in ["total_duration_ms", "cache_hit", "cache_key"]
    }
    if business_headers:
        builder.with_business_headers(**business_headers)

    return builder.build()


def set_performance_headers(
    resp: Response,
    total_duration_ms: float,
    service_duration_ms: float = None,
    external_api_calls: int = None,
    **kwargs,
) -> None:
    """
    Set performance headers on an existing response object.

    Usage:
        set_performance_headers(resp, total_duration_ms=45.2, service_duration_ms=12.5)
    """
    if resp:
        resp.headers["X-Response-Time"] = f"{total_duration_ms:.2f}ms"

        if service_duration_ms is not None:
            resp.headers["X-Service-Time"] = f"{service_duration_ms:.2f}ms"

        if external_api_calls is not None:
            resp.headers["X-External-API-Calls"] = str(external_api_calls)

        # Add any additional performance headers
        for key, value in kwargs.items():
            if value is not None:
                header_key = f"X-{key.replace('_', '-').title()}"
                resp.headers[header_key] = str(value)


def set_cache_headers(
    resp: Response,
    cache_hit: bool,
    cache_key: str = None,
    ttl_seconds: int = None,
    **kwargs,
) -> None:
    """
    Set cache headers on an existing response object.

    Usage:
        set_cache_headers(resp, cache_hit=True, cache_key="quote:AAPL", ttl_seconds=300)
    """
    if resp:
        resp.headers["X-Cache-Hit"] = str(cache_hit).lower()

        if cache_key:
            resp.headers["X-Cache-Key"] = cache_key

        if ttl_seconds:
            resp.headers["X-Cache-TTL"] = str(ttl_seconds)

        # Add any additional cache headers
        for key, value in kwargs.items():
            if value is not None:
                header_key = f"X-{key.replace('_', '-').title()}"
                resp.headers[header_key] = str(value)
