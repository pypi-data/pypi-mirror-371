"""Utility functions and helpers for Tradata Core"""

from .decorators import (
    log_endpoint,
    log_with_context,
    log_cache_operation,
    log_performance,
)

from .context import LoggingContext, RequestContext, logging_context, request_context

from .response_builder import (
    ResponseBuilder,
    create_response,
    set_performance_headers,
    set_cache_headers,
)

from .cache_helper import CacheHelper, get_cached_or_fetch, cache_key_builder

# Removed performance_schema import as it doesn't exist
# from .performance_schema import (
#     PerformanceEventType,
#     PERFORMANCE_EVENTS,
#     validate_performance_event,
#     create_performance_event,
# )

__all__ = [
    "log_endpoint",
    "log_with_context",
    "log_cache_operation",
    "log_performance",
    "LoggingContext",
    "RequestContext",
    "logging_context",
    "request_context",
    "ResponseBuilder",
    "create_response",
    "set_performance_headers",
    "set_cache_headers",
    "CacheHelper",
    "get_cached_or_fetch",
    "cache_key_builder",
    # Removed performance_schema related items
    # "PerformanceEventType",
    # "PERFORMANCE_EVENTS",
    # "validate_performance_event",
    # "create_performance_event",
]
