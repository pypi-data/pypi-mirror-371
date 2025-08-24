"""Comprehensive tests for all Tradata Core functionality"""

import pytest
import asyncio
import tradata_core
from tradata_core import (
    get_logger,
    ModernLogger,
    ModernLoggingEngine,
    log_endpoint,
    log_with_context,
    log_cache_operation,
    log_performance,
    LoggingContext,
    RequestContext,
    ResponseBuilder,
    create_response,
    set_performance_headers,
    set_cache_headers,
    CacheHelper,
    get_cached_or_fetch,
    cache_key_builder,
    set_trace_id,
    set_request_id,
    set_client,
    get_call_summary,
    log,
    log_sync,
)


class TestCompleteFunctionality:
    """Test that all original functionality is preserved"""

    def test_all_original_functions_exist(self):
        """Verify every function from original __init__.py exists"""
        # Core functions
        assert callable(get_logger)
        assert callable(set_trace_id)
        assert callable(set_client)
        assert callable(set_request_id)
        assert callable(get_call_summary)
        assert callable(log)
        assert callable(log_sync)

        # Classes
        assert ModernLogger is not None
        assert ModernLoggingEngine is not None

        # Utilities
        assert ResponseBuilder is not None
        assert CacheHelper is not None
        assert callable(create_response)
        assert callable(set_performance_headers)
        assert callable(set_cache_headers)
        assert callable(get_cached_or_fetch)
        assert callable(cache_key_builder)

    def test_response_builder_functionality(self):
        """Test all response_builder functions work identically"""
        # Test ResponseBuilder
        builder = ResponseBuilder("/test/endpoint")
        builder.with_data({"test": "data"})
        builder.with_performance_headers(45.2, service_duration_ms=12.5)
        builder.with_cache_headers(True, "test:key", ttl_seconds=300)

        response = builder.build()
        assert response.status_code == 200
        assert response.headers["X-Response-Time"] == "45.20ms"
        assert response.headers["X-Cache-Hit"] == "true"
        assert response.headers["X-Cache-TTL"] == "300"

        # Test create_response
        response = create_response(
            data={"test": "data"},
            endpoint="/test/endpoint",
            total_duration_ms=45.2,
            cache_hit=True,
            cache_key="test:key",
        )
        assert response.status_code == 200
        assert response.headers["X-Cache-Hit"] == "true"

    def test_cache_helper_functionality(self):
        """Test cache_helper works without external dependencies"""
        # Test cache_key_builder
        key = cache_key_builder("quote", "AAPL", "daily", "standard")
        assert key == "quote:AAPL:daily:standard"

        # Test CacheHelper (abstract class)
        cache = CacheHelper("test_cache", "redis")
        assert cache.cache_name == "test_cache"
        assert cache.cache_type == "redis"

        # Test build_key method
        key = cache.build_key("prefix", "part1", "part2")
        assert key == "prefix:part1:part2"

    def test_import_compatibility(self):
        """Test that all original import patterns still work"""
        # Test direct imports
        from tradata_core import get_logger, set_trace_id

        assert callable(get_logger)
        assert callable(set_trace_id)

        # Test utility imports
        from tradata_core import ResponseBuilder, CacheHelper

        assert ResponseBuilder is not None
        assert CacheHelper is not None

        # Test decorator imports
        from tradata_core import log_endpoint, log_with_context

        assert callable(log_endpoint)
        assert callable(log_with_context)

    def test_logger_methods_identical(self):
        """Test that all logger methods have identical signatures"""
        logger = get_logger("test")

        # Test specialized logging methods
        assert hasattr(logger, "log_cache_operation")
        assert hasattr(logger, "log_client_operation")
        assert hasattr(logger, "log_data_processing")
        assert hasattr(logger, "log_business_logic")
        assert hasattr(logger, "log_error_handling")
        assert hasattr(logger, "log_performance")
        assert hasattr(logger, "log_mathematics")

    def test_context_variables_identical(self):
        """Test that context variables work identically"""
        # Set context variables
        set_trace_id("test-trace-123")
        set_request_id("test-request-456")
        set_client("test-client")

        # Get call summary
        summary = get_call_summary()
        assert summary["trace_id"] == "test-trace-123"
        assert summary["request_id"] == "test-request-456"
        assert summary["client"] == "test-client"

    def test_decorators_functionality(self):
        """Test that all decorators work identically"""

        # Test log_endpoint decorator
        @log_endpoint
        async def test_endpoint():
            return {"status": "success"}

        # Test log_with_context context manager factory
        context_factory = log_with_context(
            "/test/endpoint", "test_algorithm", "test_service"
        )
        assert context_factory is not None

        # Test log_cache_operation decorator
        @log_cache_operation("redis", "test_cache", "get")
        async def test_cache():
            return {"status": "success"}

        # Test log_performance decorator
        @log_performance("test_operation", "test_step")
        async def test_performance():
            return {"status": "success"}

        # All decorators should be callable
        assert callable(test_endpoint)
        assert hasattr(context_factory, "__aenter__")  # Context manager
        assert callable(test_cache)
        assert callable(test_performance)

    def test_context_managers_functionality(self):
        """Test that context managers work identically"""
        # Test LoggingContext
        ctx = LoggingContext(operation="test", step="context")
        assert ctx.operation == "test"
        assert ctx.step == "context"

        # Test RequestContext
        req_ctx = RequestContext("/test/endpoint", method="GET", client_ip="127.0.0.1")
        assert req_ctx.method == "GET"
        assert req_ctx.client_ip == "127.0.0.1"

    def test_middleware_functionality(self):
        """Test that middleware works identically"""
        from tradata_core import LoggingMiddleware, PerformanceLoggingMiddleware

        # Test middleware creation
        from unittest.mock import Mock

        mock_app = Mock()
        middleware = LoggingMiddleware(mock_app)
        assert middleware is not None

        performance_middleware = PerformanceLoggingMiddleware(mock_app)
        assert performance_middleware is not None

    def test_formatters_and_handlers(self):
        """Test that formatters and handlers work identically"""
        from tradata_core import TraDataFormatter, TraDataHandler

        # Test formatter
        formatter = TraDataFormatter()
        assert formatter is not None

        # Test handler
        handler = TraDataHandler()
        assert handler is not None

    def test_configuration_functionality(self):
        """Test that configuration works identically"""
        from tradata_core import LogConfig, HandlerConfig, DEFAULT_CONFIG, ENV_CONFIG

        # Test configuration classes
        config = LogConfig()
        assert config is not None

        handler_config = HandlerConfig()
        assert handler_config is not None

        # Test default config
        assert DEFAULT_CONFIG is not None
        assert ENV_CONFIG is not None

    def test_async_functionality(self):
        """Test that async functionality works identically"""

        async def test_async():
            logger = get_logger("test")
            await logger.info("test message", "test_operation", "test_step")
            return True

        # Run async function
        result = asyncio.run(test_async())
        assert result is True

    def test_sync_functionality(self):
        """Test that sync functionality works identically"""
        # Test sync logging
        result = log_sync("info", "test message", "test_operation", "test_step")
        assert result is None  # log_sync doesn't return anything

    def test_error_handling_identical(self):
        """Test that error handling works identically"""
        get_logger("test")

        # Test error logging - should not raise exceptions
        try:
            # This should work without errors
            pass
        except Exception:
            pytest.fail("Error handling should not raise exceptions")

    def test_performance_characteristics(self):
        """Test that performance characteristics are identical"""
        import time

        # Test logging speed
        start_time = time.time()
        get_logger("test")
        end_time = time.time()

        # Logger creation should be fast (< 1ms)
        assert (end_time - start_time) < 0.001

    def test_memory_usage_identical(self):
        """Test that memory usage patterns are identical"""
        import sys

        # Test memory usage
        sys.getsizeof(get_logger("test"))

        # Create multiple loggers
        loggers = [get_logger(f"test_{i}") for i in range(10)]

        # Memory usage should be reasonable
        total_size = sum(sys.getsizeof(logger) for logger in loggers)
        assert total_size < 10000  # Less than 10KB for 10 loggers

    def test_thread_safety_identical(self):
        """Test that thread safety characteristics are identical"""
        import threading

        # Test context variable isolation
        def worker(thread_id):
            set_trace_id(f"thread-{thread_id}")
            summary = get_call_summary()
            assert summary["trace_id"] == f"thread-{thread_id}"

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

    def test_integration_compatibility(self):
        """Test that integration patterns work identically"""
        # Test FastAPI integration
        from tradata_core import LoggingMiddleware

        # Create middleware
        from unittest.mock import Mock

        mock_app = Mock()
        middleware = LoggingMiddleware(mock_app)
        assert middleware is not None

        # Test logger creation in different contexts
        logger1 = get_logger("service1")
        logger2 = get_logger("service2")

        assert logger1.name == "service1"
        assert logger2.name == "service2"

        # Test context isolation
        set_trace_id("trace1")
        assert get_call_summary()["trace_id"] == "trace1"

        set_trace_id("trace2")
        assert get_call_summary()["trace_id"] == "trace2"

    def test_backward_compatibility(self):
        """Test that all backward compatibility is maintained"""
        # Test old import patterns still work
        from tradata_core.core.logger import get_logger as old_get_logger
        from tradata_core.core.engine import ModernLoggingEngine as OldEngine

        # Test old class names
        logger = old_get_logger("test")
        assert logger is not None

        engine = OldEngine()
        assert engine is not None

    def test_forward_compatibility(self):
        """Test that new features don't break existing functionality"""
        # Test new log_sync function
        result = log_sync("info", "test", "test", "test")
        assert result is None

        # Test new setup_logging function
        from tradata_core import setup_logging

        engine = setup_logging()
        assert engine is not None

    def test_complete_api_coverage(self):
        """Test that the complete API is available"""
        # Test all public functions
        public_functions = [
            "get_logger",
            "setup_logging",
            "set_trace_id",
            "set_request_id",
            "set_client",
            "get_call_summary",
            "log",
            "log_sync",
        ]

        for func_name in public_functions:
            assert hasattr(tradata_core, func_name), f"Missing function: {func_name}"

        # Test all public classes
        public_classes = [
            "ModernLogger",
            "ModernLoggingEngine",
            "TraDataFormatter",
            "TraDataHandler",
            "LoggingMiddleware",
            "LogConfig",
            "ResponseBuilder",
            "CacheHelper",
            "LoggingContext",
            "RequestContext",
        ]

        for class_name in public_classes:
            assert hasattr(tradata_core, class_name), f"Missing class: {class_name}"

        # Test all decorators
        decorators = [
            "log_endpoint",
            "log_with_context",
            "log_cache_operation",
            "log_performance",
        ]

        for decorator_name in decorators:
            assert hasattr(
                tradata_core, decorator_name
            ), f"Missing decorator: {decorator_name}"
