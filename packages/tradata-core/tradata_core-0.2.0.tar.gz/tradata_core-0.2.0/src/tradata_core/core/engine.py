"""
Simple logging engine for the net-new logging system.
Provides basic logging functionality with context variables.
"""

from contextvars import ContextVar
from typing import Any, Dict, Optional
from datetime import datetime

# Context variables for request tracking
trace_id: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
client_used: ContextVar[Optional[str]] = ContextVar("client_used", default=None)


class ModernLoggingEngine:
    """Simple logging engine with context variable support."""

    def __init__(self):
        self.trace_id = trace_id
        self.request_id = request_id
        self.client_used = client_used

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
