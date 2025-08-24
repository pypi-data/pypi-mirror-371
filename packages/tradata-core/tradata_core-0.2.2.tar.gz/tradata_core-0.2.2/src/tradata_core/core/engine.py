"""
Simple logging engine for the net-new logging system.
Provides basic logging functionality with context variables.
"""

from contextvars import ContextVar
from typing import Any, Dict, Optional
from datetime import datetime
from ..config.settings import LogConfig, ENV_CONFIG

# Context variables for request tracking
trace_id: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
client_used: ContextVar[Optional[str]] = ContextVar("client_used", default=None)


class ModernLoggingEngine:
    """Simple logging engine with context variable support."""

    def __init__(self, config: Optional[LogConfig] = None):
        self.trace_id = trace_id
        self.request_id = request_id
        self.client_used = client_used
        self.config = config or ENV_CONFIG

        # Log debug configuration status at startup
        self._log_debug_configuration()

    def _log_debug_configuration(self):
        """Log the debug configuration status at startup"""
        debug_enabled = self.config.is_debug_enabled()
        debug_env = self.config.get_debug_environment()
        effective_level = self.config.get_effective_log_level()

        # Use basic print for startup logging to avoid circular dependencies
        print("[Tradata-Core] Debug Configuration:")
        print(f"  - Debug Enabled: {debug_enabled}")
        print(f"  - Debug Environment: {debug_env}")
        print(f"  - Effective Log Level: {effective_level}")

        if debug_enabled and self.config.should_allow_debug_in_environment():
            print("  - ✅ Debug logging is ACTIVE")
        else:
            print("  - ❌ Debug logging is DISABLED")
            if not debug_enabled:
                print("    Reason: LOG_ENABLE_DEBUG=false")
            elif not self.config.should_allow_debug_in_environment():
                print(
                    f"    Reason: Environment '{debug_env}' does not allow debug logging"
                )

    def is_debug_enabled(self) -> bool:
        """Check if debug logging is enabled and allowed in current environment"""
        return (
            self.config.is_debug_enabled()
            and self.config.should_allow_debug_in_environment()
        )

    def get_debug_status(self) -> Dict[str, Any]:
        """Get debug configuration status"""
        return {
            "debug_enabled": self.config.is_debug_enabled(),
            "debug_environment": self.config.get_debug_environment(),
            "environment_allows_debug": self.config.should_allow_debug_in_environment(),
            "effective_log_level": self.config.get_effective_log_level(),
            "is_debug_active": self.is_debug_enabled(),
        }

    async def log(self, level: str, message: str, operation: str, step: str, **kwargs):
        """Log a message with context."""
        # Get current context values
        current_trace_id = trace_id.get()
        current_request_id = request_id.get()
        current_client = client_used.get()

        # Create log entry
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "operation": operation,
            "step": step,
            "trace_id": current_trace_id,
            "request_id": current_request_id,
            "client": current_client,
            **kwargs,
        }

        # For now, just print to console (can be enhanced later)
        print(f"[{timestamp}] {level} {operation}:{step} | {message} | {log_entry}")

    def get_call_summary(self) -> Dict[str, Any]:
        """Get current call summary."""
        return {
            "trace_id": trace_id.get(),
            "request_id": request_id.get(),
            "client": client_used.get(),
            "timestamp": datetime.now().isoformat(),
        }
