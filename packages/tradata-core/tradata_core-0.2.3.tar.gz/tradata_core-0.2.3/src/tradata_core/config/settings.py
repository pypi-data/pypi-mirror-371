"""
Logging configuration for Tradata logger
"""

import os
from typing import Optional, List
from pydantic import BaseModel, Field


class HandlerConfig(BaseModel):
    """Configuration for a single log handler"""

    type: str = Field(
        default="console",
        description="Handler type: console, file, timed_rotating, null",
    )
    level: str = Field(default="INFO", description="Log level for this handler")
    filename: Optional[str] = Field(
        default=None, description="File path for file handlers"
    )
    max_bytes: Optional[int] = Field(
        default=10 * 1024 * 1024, description="Max file size for rotating handlers"
    )
    backup_count: Optional[int] = Field(default=5, description="Number of backup files")
    when: Optional[str] = Field(
        default="midnight", description="When to rotate for timed handlers"
    )
    interval: Optional[int] = Field(
        default=1, description="Rotation interval for timed handlers"
    )
    formatter: Optional[str] = Field(
        default="json", description="Formatter type: json, console"
    )


class LogConfig(BaseModel):
    """Main logging configuration"""

    # General settings
    level: str = Field(default="INFO", description="Default log level")
    format: str = Field(default="json", description="Default format: json, console")

    # Debug settings
    enable_debug: bool = Field(
        default=False, description="Enable debug logging (overrides level setting)"
    )
    debug_environment: str = Field(
        default="development",
        description="Environment where debug is allowed: development, staging, production",
    )

    # Handlers
    handlers: List[HandlerConfig] = Field(
        default_factory=lambda: [HandlerConfig(type="console", level="INFO")],
        description="List of log handlers",
    )

    # Context settings
    include_trace_id: bool = Field(default=True, description="Include trace ID in logs")
    include_request_id: bool = Field(
        default=True, description="Include request ID in logs"
    )
    include_client: bool = Field(
        default=True, description="Include client information in logs"
    )

    # Performance settings
    log_performance: bool = Field(
        default=True, description="Enable performance logging"
    )
    log_cache_operations: bool = Field(
        default=True, description="Enable cache operation logging"
    )
    log_client_operations: bool = Field(
        default=True, description="Enable client operation logging"
    )

    # Output settings
    pretty_print: bool = Field(default=False, description="Pretty print JSON logs")
    include_timestamp: bool = Field(
        default=True, description="Include timestamp in logs"
    )
    include_level: bool = Field(default=True, description="Include log level in logs")

    @classmethod
    def from_env(cls) -> "LogConfig":
        """Create configuration from environment variables"""
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "json"),
            enable_debug=os.getenv("LOG_ENABLE_DEBUG", "false").lower() == "true",
            debug_environment=os.getenv("LOG_DEBUG_ENVIRONMENT", "development"),
            include_trace_id=os.getenv("LOG_INCLUDE_TRACE_ID", "true").lower()
            == "true",
            include_request_id=os.getenv("LOG_INCLUDE_REQUEST_ID", "true").lower()
            == "true",
            include_client=os.getenv("LOG_INCLUDE_CLIENT", "true").lower() == "true",
            log_performance=os.getenv("LOG_PERFORMANCE", "true").lower() == "true",
            log_cache_operations=os.getenv("LOG_CACHE_OPERATIONS", "true").lower()
            == "true",
            log_client_operations=os.getenv("LOG_CLIENT_OPERATIONS", "true").lower()
            == "true",
            pretty_print=os.getenv("LOG_PRETTY_PRINT", "false").lower() == "true",
            include_timestamp=os.getenv("LOG_INCLUDE_TIMESTAMP", "true").lower()
            == "true",
            include_level=os.getenv("LOG_INCLUDE_LEVEL", "true").lower() == "true",
        )

    def get_handler_configs(self) -> List[HandlerConfig]:
        """Get handler configurations"""
        return self.handlers

    def get_default_level(self) -> str:
        """Get default log level"""
        return self.level

    def get_default_format(self) -> str:
        """Get default format"""
        return self.format

    def should_include_trace_id(self) -> bool:
        """Check if trace ID should be included"""
        return self.include_trace_id

    def should_include_request_id(self) -> bool:
        """Check if request ID should be included"""
        return self.include_request_id

    def should_include_client(self) -> bool:
        """Check if client should be included"""
        return self.include_client

    def should_log_performance(self) -> bool:
        """Check if performance logging is enabled"""
        return self.log_performance

    def should_log_cache_operations(self) -> bool:
        """Check if cache operation logging is enabled"""
        return self.log_cache_operations

    def should_log_client_operations(self) -> bool:
        """Check if client operation logging is enabled"""
        return self.log_client_operations

    def is_debug_enabled(self) -> bool:
        """Check if debug logging is enabled"""
        return self.enable_debug

    def get_debug_environment(self) -> str:
        """Get the debug environment setting"""
        return self.debug_environment

    def should_allow_debug_in_environment(self) -> bool:
        """Check if debug is allowed in the current environment"""
        # Only allow debug in development and staging
        return self.debug_environment in ["development", "staging"]

    def get_effective_log_level(self) -> str:
        """Get the effective log level considering debug settings"""
        if self.is_debug_enabled() and self.should_allow_debug_in_environment():
            return "DEBUG"
        return self.level


# Default configuration
DEFAULT_CONFIG = LogConfig()

# Environment-based configuration
ENV_CONFIG = LogConfig.from_env()
