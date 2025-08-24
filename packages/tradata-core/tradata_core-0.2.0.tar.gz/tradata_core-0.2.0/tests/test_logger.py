"""Test the core logger functionality"""

import pytest
from tradata_core import get_logger, setup_logging, ModernLogger
from tradata_core.core.engine import ModernLoggingEngine


def test_get_logger():
    """Test getting a logger instance"""
    logger = get_logger("test")
    assert logger is not None
    assert logger.name == "test"
    assert isinstance(logger, ModernLogger)


def test_logger_has_engine():
    """Test that logger has an engine"""
    logger = get_logger("test")
    assert hasattr(logger, "engine")
    assert isinstance(logger.engine, ModernLoggingEngine)


def test_setup_logging():
    """Test setting up logging"""
    engine = setup_logging()
    assert engine is not None
    assert isinstance(engine, ModernLoggingEngine)


@pytest.mark.asyncio
async def test_logger_info():
    """Test info logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.info("Test message", "TestOperation", "TestStep")


@pytest.mark.asyncio
async def test_logger_debug():
    """Test debug logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.debug("Test debug message", "TestOperation", "TestStep")


@pytest.mark.asyncio
async def test_logger_warning():
    """Test warning logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.warning("Test warning message", "TestOperation", "TestStep")


@pytest.mark.asyncio
async def test_logger_error():
    """Test error logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.error("Test error message", "TestOperation", "TestStep")


@pytest.mark.asyncio
async def test_logger_critical():
    """Test critical logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.critical("Test critical message", "TestOperation", "TestStep")


def test_logger_with_context():
    """Test logger with context"""
    logger = get_logger("test")
    contextual_logger = logger.with_context(service="test_service")
    assert contextual_logger is not None
    assert hasattr(contextual_logger, "context")
    assert contextual_logger.context["service"] == "test_service"


def test_logger_track_client():
    """Test client tracking"""
    logger = get_logger("test")
    result = logger.track_client("test_client")
    assert result is logger  # Should return self for chaining


@pytest.mark.asyncio
async def test_logger_cache_operation():
    """Test cache operation logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.log_cache_operation("TestStep", True, "test_key", 100.0)


@pytest.mark.asyncio
async def test_logger_client_operation():
    """Test client operation logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.log_client_operation(
        "TestStep", "test_client", "test_operation", 100.0
    )


@pytest.mark.asyncio
async def test_logger_data_processing():
    """Test data processing logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.log_data_processing("TestStep")


@pytest.mark.asyncio
async def test_logger_business_logic():
    """Test business logic logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.log_business_logic("TestStep")


@pytest.mark.asyncio
async def test_logger_error_handling():
    """Test error handling logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.log_error_handling("TestStep")


@pytest.mark.asyncio
async def test_logger_performance():
    """Test performance logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.log_performance("TestStep")


@pytest.mark.asyncio
async def test_logger_mathematics():
    """Test mathematics logging"""
    logger = get_logger("test")
    # This should not raise an exception
    await logger.log_mathematics("TestStep", "test_principle")
