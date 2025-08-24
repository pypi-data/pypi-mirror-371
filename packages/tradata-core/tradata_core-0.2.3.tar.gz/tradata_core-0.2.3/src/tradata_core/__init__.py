"""Tradata Core - Professional logging for trading applications"""

from .core import (
    get_logger,
    setup_logging,
    ModernLogger,
    ModernLoggingEngine,
    TraDataFormatter,
    TraDataHandler,
    set_trace_id,
    set_request_id,
    set_client,
    get_call_summary,
    log,
    log_sync,
    get_performance_logger,
    setup_performance_integration,
    PerformanceEventLogger,
    get_debug_status,
)
from .middleware.fastapi import LoggingMiddleware, PerformanceLoggingMiddleware
from .config.settings import LogConfig, HandlerConfig, DEFAULT_CONFIG, ENV_CONFIG
from .utils.decorators import (
    log_endpoint,
    log_with_context,
    log_cache_operation,
    log_performance,
)
from .utils.context import (
    LoggingContext,
    RequestContext,
    logging_context,
    request_context,
)
from .utils.response_builder import (
    ResponseBuilder,
    create_response,
    set_performance_headers,
    set_cache_headers,
)
from .utils.cache_helper import CacheHelper, get_cached_or_fetch, cache_key_builder

__version__ = "0.2.0"
__all__ = [
    "get_logger",
    "setup_logging",
    "ModernLogger",
    "ModernLoggingEngine",
    "TraDataFormatter",
    "TraDataHandler",
    "LoggingMiddleware",
    "PerformanceLoggingMiddleware",
    "LogConfig",
    "HandlerConfig",
    "DEFAULT_CONFIG",
    "ENV_CONFIG",
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
    "set_trace_id",
    "set_request_id",
    "set_client",
    "get_call_summary",
    "log",
    "log_sync",
    "get_performance_logger",
    "setup_performance_integration",
    "PerformanceEventLogger",
    "get_debug_status",
]
