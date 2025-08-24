"""Test middleware functionality"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tradata_core.middleware.fastapi import (
    LoggingMiddleware,
    PerformanceLoggingMiddleware,
)
from tradata_core.core.engine import ModernLoggingEngine


@pytest.fixture
def app():
    """Create a test FastAPI app"""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")

    return app


@pytest.fixture
def client(app):
    """Create a test client"""
    return TestClient(app)


def test_logging_middleware_creation():
    """Test creating logging middleware"""
    engine = ModernLoggingEngine()
    middleware = LoggingMiddleware(None, engine)
    assert middleware is not None
    assert middleware.engine is engine


def test_performance_middleware_creation():
    """Test creating performance middleware"""
    engine = ModernLoggingEngine()
    middleware = PerformanceLoggingMiddleware(None, engine)
    assert middleware is not None
    assert middleware.engine is engine


def test_middleware_with_default_engine():
    """Test middleware with default engine"""
    middleware = LoggingMiddleware(None)
    assert middleware is not None
    assert middleware.engine is not None
    assert isinstance(middleware.engine, ModernLoggingEngine)


def test_middleware_adds_trace_id_header(app, client):
    """Test that middleware adds trace ID header"""
    app.add_middleware(LoggingMiddleware)

    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Trace-ID" in response.headers
    assert "X-Request-ID" in response.headers
    assert "X-Response-Time" in response.headers


def test_middleware_handles_existing_trace_id(app, client):
    """Test that middleware handles existing trace ID"""
    app.add_middleware(LoggingMiddleware)

    headers = {"X-Trace-ID": "existing-trace-123"}
    response = client.get("/test", headers=headers)
    assert response.status_code == 200
    assert response.headers["X-Trace-ID"] == "existing-trace-123"


def test_middleware_generates_trace_id_when_missing(app, client):
    """Test that middleware generates trace ID when missing"""
    app.add_middleware(LoggingMiddleware)

    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Trace-ID" in response.headers
    trace_id = response.headers["X-Trace-ID"]
    assert trace_id.startswith("auto-")


def test_middleware_logs_request_start(app, client):
    """Test that middleware logs request start"""
    app.add_middleware(LoggingMiddleware)

    # This test verifies the middleware doesn't crash
    # In a real test, you'd mock the logging engine and verify calls
    response = client.get("/test")
    assert response.status_code == 200


def test_middleware_logs_request_completion(app, client):
    """Test that middleware logs request completion"""
    app.add_middleware(LoggingMiddleware)

    # This test verifies the middleware doesn't crash
    response = client.get("/test")
    assert response.status_code == 200


def test_middleware_logs_errors(app, client):
    """Test that middleware logs errors"""
    app.add_middleware(LoggingMiddleware)

    # This test verifies the middleware doesn't crash on errors
    with pytest.raises(ValueError):
        client.get("/error")


def test_performance_middleware_adds_headers(app, client):
    """Test that performance middleware adds performance headers"""
    app.add_middleware(PerformanceLoggingMiddleware)

    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Response-Time" in response.headers
    assert "X-Request-ID" in response.headers
    assert "X-Trace-ID" in response.headers


def test_performance_middleware_handles_cache_headers(app, client):
    """Test that performance middleware handles cache headers"""
    app.add_middleware(PerformanceLoggingMiddleware)

    # Mock a response with cache headers
    @app.get("/cached")
    async def cached_endpoint():
        from fastapi.responses import Response

        response = Response(content="cached content")
        response.headers["X-Cache"] = "HIT"
        return response

    response = client.get("/cached")
    assert response.status_code == 200
    assert response.headers["X-Cache"] == "HIT"


def test_middleware_context_variables():
    """Test that middleware sets context variables"""
    engine = ModernLoggingEngine()
    LoggingMiddleware(None, engine)

    # Test that context variables are accessible
    assert hasattr(engine, "trace_id")
    assert hasattr(engine, "request_id")
    assert hasattr(engine, "client_used")


def test_middleware_engine_integration():
    """Test that middleware integrates with engine"""
    engine = ModernLoggingEngine()
    middleware = LoggingMiddleware(None, engine)

    # Test that middleware can access engine methods
    assert hasattr(middleware.engine, "log")
    assert hasattr(middleware.engine, "get_call_summary")
