"""
Net-new log formatters - completely fresh design with operation and step structure
"""

import json
from datetime import datetime
from typing import Optional
from pythonjsonlogger import jsonlogger


class TraDataFormatter:
    """Net-new JSON formatter with trace ID, operation, and step structure"""

    def __init__(self, include_timestamp: bool = True, include_level: bool = True):
        self.include_timestamp = include_timestamp
        self.include_level = include_level

    def format(self, record) -> str:
        """Format log record with mandatory trace ID, operation, and step"""
        log_entry = {
            "timestamp": (
                datetime.utcnow().isoformat() if self.include_timestamp else None
            ),
            "level": record.levelname if self.include_level else None,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", "MISSING_TRACE_ID"),
            "request_id": getattr(record, "request_id", None),
            "operation_id": getattr(record, "operation_id", None),
            "operation": getattr(record, "operation", "MISSING_OPERATION"),
            "step": getattr(record, "step", "MISSING_STEP"),
            "client": getattr(record, "client", None),
            "endpoint": getattr(record, "endpoint", None),
            "method": getattr(record, "method", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "cache_hit": getattr(record, "cache_hit", None),
            "error": getattr(record, "error", None),
            "extra": getattr(record, "extra", {}),
        }

        # Remove None values for cleaner logs
        log_entry = {k: v for k, v in log_entry.items() if v is not None}

        return json.dumps(log_entry, ensure_ascii=False)


class TraDataJSONFormatter(jsonlogger.JsonFormatter):
    """JSON formatter extending python-json-logger with Tradata specific fields"""

    def __init__(
        self, fmt: Optional[str] = None, datefmt: Optional[str] = None, style: str = "%"
    ):
        super().__init__(fmt, datefmt, style)

    def add_fields(self, log_record, record, message_dict):
        """Add Tradata specific fields to the log record"""
        super().add_fields(log_record, record, message_dict)

        # Add mandatory Tradata fields
        log_record["trace_id"] = getattr(record, "trace_id", "MISSING_TRACE_ID")
        log_record["operation"] = getattr(record, "operation", "MISSING_OPERATION")
        log_record["step"] = getattr(record, "step", "MISSING_STEP")

        # Add optional fields
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "client"):
            log_record["client"] = record.client
        if hasattr(record, "endpoint"):
            log_record["endpoint"] = record.endpoint
        if hasattr(record, "method"):
            log_record["method"] = record.method
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms
        if hasattr(record, "cache_hit"):
            log_record["cache_hit"] = record.cache_hit
        if hasattr(record, "error"):
            log_record["error"] = record.error


class TraDataConsoleFormatter:
    """Human-readable console formatter for development"""

    def __init__(self, colorize: bool = True):
        self.colorize = colorize

    def format(self, record) -> str:
        """Format log record for console output"""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.ljust(8)
        logger = record.name
        message = record.getMessage()

        # Basic format
        formatted = f"[{timestamp}] {level} {logger} | {message}"

        # Add context if available
        context_parts = []
        if hasattr(record, "trace_id"):
            context_parts.append(f"trace_id={record.trace_id}")
        if hasattr(record, "operation"):
            context_parts.append(f"op={record.operation}")
        if hasattr(record, "step"):
            context_parts.append(f"step={record.step}")
        if hasattr(record, "client"):
            context_parts.append(f"client={record.client}")

        if context_parts:
            formatted += f" | {' '.join(context_parts)}"

        return formatted
