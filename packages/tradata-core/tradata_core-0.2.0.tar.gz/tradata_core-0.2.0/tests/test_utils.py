"""Test utility functions"""

import pytest
from tradata_core.utils.decorators import (
    log_endpoint,
    log_with_context,
    log_cache_operation,
    log_performance,
)
from tradata_core.utils.context import (
    LoggingContext,
    RequestContext,
    logging_context,
    request_context,
)


@pytest.mark.asyncio
async def test_log_endpoint_decorator():
    """Test log_endpoint decorator"""

    @log_endpoint("/test", "test_algorithm", "test_service")
    async def test_function():
        return "success"

    result = await test_function()
    assert result == "success"


@pytest.mark.asyncio
async def test_log_endpoint_with_response():
    """Test log_endpoint decorator with response object"""
    from fastapi.responses import Response

    @log_endpoint("/test", "test_algorithm", "test_service")
    async def test_function(resp: Response = None):
        if resp:
            resp.headers["X-Test"] = "test_value"
        return "success"

    # Mock response object
    response = Response()
    result = await test_function(resp=response)
    assert result == "success"
    assert response.headers["X-Test"] == "test_value"


@pytest.mark.asyncio
async def test_log_endpoint_error_handling():
    """Test log_endpoint decorator error handling"""

    @log_endpoint("/test", "test_algorithm", "test_service")
    async def test_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        await test_function()


@pytest.mark.asyncio
async def test_log_with_context():
    """Test log_with_context context manager"""

    async with log_with_context("/test", "test_algorithm", "test_service") as ctx:
        assert ctx.endpoint == "/test"
        assert ctx.algorithm == "test_algorithm"
        assert ctx.client == "test_service"
        # Context should be active
        pass


@pytest.mark.asyncio
async def test_log_with_context_error():
    """Test log_with_context error handling"""

    with pytest.raises(ValueError, match="Test error"):
        async with log_with_context("/test", "test_algorithm", "test_service"):
            raise ValueError("Test error")


@pytest.mark.asyncio
async def test_log_cache_operation():
    """Test log_cache_operation decorator"""

    @log_cache_operation("redis", "test_cache", "get")
    async def test_cache_function():
        return "cached_data"

    result = await test_cache_function()
    assert result == "cached_data"


@pytest.mark.asyncio
async def test_log_cache_operation_error():
    """Test log_cache_operation error handling"""

    @log_cache_operation("redis", "test_cache", "get")
    async def test_cache_function():
        raise ValueError("Cache error")

    with pytest.raises(ValueError, match="Cache error"):
        await test_cache_function()


@pytest.mark.asyncio
async def test_log_performance():
    """Test log_performance decorator"""

    @log_performance("test_operation", "test_step")
    async def test_performance_function():
        return "performance_result"

    result = await test_performance_function()
    assert result == "performance_result"


@pytest.mark.asyncio
async def test_log_performance_error():
    """Test log_performance error handling"""

    @log_performance("test_operation", "test_step")
    async def test_performance_function():
        raise ValueError("Performance error")

    with pytest.raises(ValueError, match="Performance error"):
        await test_performance_function()


def test_logging_context_creation():
    """Test LoggingContext creation"""
    ctx = LoggingContext(
        "test_operation", "test_step", "test_client", "test_trace", "test_request"
    )
    assert ctx.operation == "test_operation"
    assert ctx.step == "test_step"
    assert ctx.client == "test_client"
    assert ctx.trace_id == "test_trace"
    assert ctx.request_id == "test_request"


def test_logging_context_add_context():
    """Test LoggingContext add_context method"""
    ctx = LoggingContext("test_operation")
    ctx.add_context(service="test_service", user="test_user")

    assert ctx.service == "test_service"
    assert ctx.user == "test_user"


@pytest.mark.asyncio
async def test_logging_context_async_context():
    """Test LoggingContext async context manager"""
    ctx = LoggingContext("test_operation", "test_step")

    async with ctx:
        # Context should be active
        assert ctx.start_time is not None
        pass


@pytest.mark.asyncio
async def test_logging_context_error():
    """Test LoggingContext error handling"""
    ctx = LoggingContext("test_operation", "test_step")

    with pytest.raises(ValueError, match="Test error"):
        async with ctx:
            raise ValueError("Test error")


def test_request_context_creation():
    """Test RequestContext creation"""
    ctx = RequestContext("/test", "GET", "127.0.0.1", "test-agent", "test-trace")
    assert ctx.endpoint == "/test"
    assert ctx.method == "GET"
    assert ctx.client_ip == "127.0.0.1"
    assert ctx.user_agent == "test-agent"
    assert ctx.trace_id == "test-trace"


def test_request_context_default_trace_id():
    """Test RequestContext default trace ID generation"""
    ctx = RequestContext("/test")
    assert ctx.trace_id is not None
    assert ctx.trace_id.startswith("req-")


@pytest.mark.asyncio
async def test_request_context_async_context():
    """Test RequestContext async context manager"""
    ctx = RequestContext("/test", "GET")

    async with ctx:
        # Context should be active
        assert ctx.start_time is not None
        pass


@pytest.mark.asyncio
async def test_request_context_error():
    """Test RequestContext error handling"""
    ctx = RequestContext("/test", "GET")

    with pytest.raises(ValueError, match="Test error"):
        async with ctx:
            raise ValueError("Test error")


@pytest.mark.asyncio
async def test_logging_context_function():
    """Test logging_context function"""
    async with logging_context("test_operation", "test_step", "test_client") as ctx:
        assert ctx.operation == "test_operation"
        assert ctx.step == "test_step"
        assert ctx.client == "test_client"


@pytest.mark.asyncio
async def test_request_context_function():
    """Test request_context function"""
    async with request_context("/test", "GET", "127.0.0.1") as ctx:
        assert ctx.endpoint == "/test"
        assert ctx.method == "GET"
        assert ctx.client_ip == "127.0.0.1"
