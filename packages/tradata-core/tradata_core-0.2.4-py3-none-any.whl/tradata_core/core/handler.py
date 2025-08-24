"""
Custom log handlers for Tradata logging system
"""

import logging
import logging.handlers
from pathlib import Path
from .formatter import TraDataJSONFormatter, TraDataConsoleFormatter


class TraDataHandler:
    """Base handler class for Tradata logging"""

    def __init__(self, formatter=None):
        self.formatter = formatter or TraDataJSONFormatter()

    def get_handler(self) -> logging.Handler:
        """Get the underlying logging handler"""
        raise NotImplementedError("Subclasses must implement get_handler")


class TraDataConsoleHandler(TraDataHandler):
    """Console handler with Tradata formatting"""

    def __init__(self, level: int = logging.INFO, formatter=None):
        super().__init__(formatter or TraDataConsoleFormatter())
        self.level = level

    def get_handler(self) -> logging.Handler:
        """Get console handler"""
        handler = logging.StreamHandler()
        handler.setLevel(self.level)
        handler.setFormatter(self.formatter)
        return handler


class TraDataFileHandler(TraDataHandler):
    """File handler with Tradata formatting and rotation"""

    def __init__(
        self,
        filename: str,
        level: int = logging.INFO,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        formatter=None,
    ):
        super().__init__(formatter or TraDataJSONFormatter())
        self.filename = filename
        self.level = level
        self.max_bytes = max_bytes
        self.backup_count = backup_count

    def get_handler(self) -> logging.Handler:
        """Get rotating file handler"""
        # Ensure directory exists
        Path(self.filename).parent.mkdir(parents=True, exist_ok=True)

        handler = logging.handlers.RotatingFileHandler(
            self.filename, maxBytes=self.max_bytes, backupCount=self.backup_count
        )
        handler.setLevel(self.level)
        handler.setFormatter(self.formatter)
        return handler


class TraDataTimedRotatingHandler(TraDataHandler):
    """Time-based rotating file handler with Tradata formatting"""

    def __init__(
        self,
        filename: str,
        level: int = logging.INFO,
        when: str = "midnight",
        interval: int = 1,
        backup_count: int = 30,
        formatter=None,
    ):
        super().__init__(formatter or TraDataJSONFormatter())
        self.filename = filename
        self.level = level
        self.when = when
        self.interval = interval
        self.backup_count = backup_count

    def get_handler(self) -> logging.Handler:
        """Get time-based rotating file handler"""
        # Ensure directory exists
        Path(self.filename).parent.mkdir(parents=True, exist_ok=True)

        handler = logging.handlers.TimedRotatingFileHandler(
            self.filename,
            when=self.when,
            interval=self.interval,
            backupCount=self.backup_count,
        )
        handler.setLevel(self.level)
        handler.setFormatter(self.formatter)
        return handler


class TraDataNullHandler(TraDataHandler):
    """Null handler for testing or when logging should be disabled"""

    def get_handler(self) -> logging.Handler:
        """Get null handler"""
        return logging.NullHandler()


def create_handler(handler_type: str = "console", **kwargs) -> TraDataHandler:
    """Factory function to create handlers"""

    if handler_type == "console":
        return TraDataConsoleHandler(**kwargs)
    elif handler_type == "file":
        return TraDataFileHandler(**kwargs)
    elif handler_type == "timed_rotating":
        return TraDataTimedRotatingHandler(**kwargs)
    elif handler_type == "null":
        return TraDataNullHandler(**kwargs)
    else:
        raise ValueError(f"Unknown handler type: {handler_type}")
