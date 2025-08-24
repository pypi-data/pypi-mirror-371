"""Observability logger integration for Python logging."""

import logging
import queue
import threading
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import atexit

from .client import ObservabilityClient
from .models import LogEntry, LogLevel
from .exceptions import ObservabilityError


class ObservabilityHandler(logging.Handler):
    """Custom logging handler that sends logs to Platform Observability service."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://observability.redducklabs.com/api/v1",
        source: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        batch_size: int = 100,
        flush_interval: int = 5,
        level: int = logging.INFO,
    ):
        """Initialize the Observability handler.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API service
            source: Source/application name for logs
            labels: Default labels to add to all logs
            batch_size: Number of logs to batch before sending
            flush_interval: Time in seconds between automatic flushes
            level: Minimum logging level
        """
        super().__init__(level=level)
        
        self.client = ObservabilityClient(api_key=api_key, base_url=base_url)
        self.source = source
        self.default_labels = labels or {}
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        # Buffer for batching logs
        self.log_buffer: List[LogEntry] = []
        self.buffer_lock = threading.Lock()
        
        # Background thread for periodic flushing
        self.flush_thread = threading.Thread(target=self._flush_worker, daemon=True)
        self.flush_thread.start()
        
        # Shutdown handling
        atexit.register(self.close)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        try:
            # Convert logging level to our LogLevel enum
            level_mapping = {
                logging.DEBUG: LogLevel.DEBUG,
                logging.INFO: LogLevel.INFO,
                logging.WARNING: LogLevel.WARN,
                logging.ERROR: LogLevel.ERROR,
                logging.CRITICAL: LogLevel.FATAL,
            }
            log_level = level_mapping.get(record.levelno, LogLevel.INFO)
            
            # Prepare labels and fields
            labels = self.default_labels.copy()
            fields = {
                "logger_name": record.name,
                "module": record.module,
                "function": record.funcName,
                "line_number": record.lineno,
                "thread_id": record.thread,
                "thread_name": record.threadName,
                "process_id": record.process,
            }
            
            # Add exception info if present
            if record.exc_info:
                fields["exception"] = self.format(record)
            
            # Add extra fields from the log record
            for key, value in record.__dict__.items():
                if key not in ("name", "msg", "args", "levelname", "levelno", "pathname",
                             "filename", "module", "lineno", "funcName", "created",
                             "msecs", "relativeCreated", "thread", "threadName",
                             "processName", "process", "getMessage", "exc_info",
                             "exc_text", "stack_info"):
                    if isinstance(value, (str, int, float, bool, type(None))):
                        fields[key] = value
                    else:
                        fields[key] = str(value)
            
            # Create log entry
            log_entry = LogEntry(
                message=record.getMessage(),
                level=log_level,
                source=self.source,
                labels=labels,
                fields=fields,
                timestamp=datetime.fromtimestamp(record.created, tz=timezone.utc),
            )
            
            # Add to buffer
            with self.buffer_lock:
                self.log_buffer.append(log_entry)
                
                # Flush if buffer is full
                if len(self.log_buffer) >= self.batch_size:
                    self._flush_buffer()
                    
        except Exception as e:
            # Don't let logging errors crash the application
            self.handleError(record)

    def _flush_buffer(self) -> None:
        """Flush the log buffer (must be called with buffer_lock held)."""
        if not self.log_buffer:
            return
        
        logs_to_send = self.log_buffer.copy()
        self.log_buffer.clear()
        
        try:
            # Send logs in the background to avoid blocking
            threading.Thread(
                target=self._send_logs,
                args=(logs_to_send,),
                daemon=True
            ).start()
        except Exception:
            # If we can't send, just drop the logs to avoid memory buildup
            pass

    def _send_logs(self, logs: List[LogEntry]) -> None:
        """Send logs to the observability service."""
        try:
            self.client.ingest_logs(logs)
        except ObservabilityError:
            # Log sending failed - could implement retry logic here
            pass

    def _flush_worker(self) -> None:
        """Background worker that periodically flushes the buffer."""
        while True:
            try:
                time.sleep(self.flush_interval)
                with self.buffer_lock:
                    self._flush_buffer()
            except Exception:
                # Continue running even if flush fails
                pass

    def flush(self) -> None:
        """Manually flush the log buffer."""
        with self.buffer_lock:
            self._flush_buffer()

    def close(self) -> None:
        """Close the handler and flush remaining logs."""
        self.flush()
        if hasattr(self, 'client'):
            self.client.close()
        super().close()


class ObservabilityLogger:
    """High-level logger interface for Platform Observability."""

    def __init__(
        self,
        api_key: str,
        name: str = "observability",
        base_url: str = "https://observability.redducklabs.com/api/v1",
        source: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        level: int = logging.INFO,
        batch_size: int = 100,
        flush_interval: int = 5,
    ):
        """Initialize the Observability logger.
        
        Args:
            api_key: API key for authentication
            name: Logger name
            base_url: Base URL for the API service
            source: Source/application name
            labels: Default labels for all logs
            level: Minimum logging level
            batch_size: Number of logs to batch before sending
            flush_interval: Time in seconds between automatic flushes
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove any existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add our custom handler
        self.handler = ObservabilityHandler(
            api_key=api_key,
            base_url=base_url,
            source=source,
            labels=labels,
            batch_size=batch_size,
            flush_interval=flush_interval,
            level=level,
        )
        self.logger.addHandler(self.handler)
        
        # Don't propagate to root logger to avoid duplicate logs
        self.logger.propagate = False

    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self.logger.warning(message, extra=kwargs)

    def warn(self, message: str, **kwargs) -> None:
        """Log a warning message (alias)."""
        self.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        self.logger.critical(message, extra=kwargs)

    def fatal(self, message: str, **kwargs) -> None:
        """Log a fatal message (alias)."""
        self.critical(message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log an exception message with traceback."""
        self.logger.exception(message, extra=kwargs)

    def log(self, level: int, message: str, **kwargs) -> None:
        """Log a message at the specified level."""
        self.logger.log(level, message, extra=kwargs)

    def flush(self) -> None:
        """Manually flush pending logs."""
        self.handler.flush()

    def close(self) -> None:
        """Close the logger and flush remaining logs."""
        self.handler.close()

    def set_level(self, level: int) -> None:
        """Set the logging level."""
        self.logger.setLevel(level)
        self.handler.setLevel(level)

    def add_labels(self, labels: Dict[str, str]) -> None:
        """Add default labels to all future logs."""
        self.handler.default_labels.update(labels)

    def set_source(self, source: str) -> None:
        """Set the source for all future logs."""
        self.handler.source = source