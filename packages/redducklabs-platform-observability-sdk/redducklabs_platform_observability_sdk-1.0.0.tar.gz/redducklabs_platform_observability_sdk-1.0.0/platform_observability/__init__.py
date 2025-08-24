"""Platform Observability Python SDK.

A comprehensive SDK for interacting with the Platform Observability service,
providing log ingestion, analytics, and API key management capabilities.
"""

from .client import ObservabilityClient
from .logger import ObservabilityLogger
from .models import LogEntry, LogLevel, APIKey, UsageMetrics
from .exceptions import (
    ObservabilityError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
)

__version__ = "1.0.0"
__author__ = "Red Duck Labs"
__email__ = "support@redducklabs.com"

__all__ = [
    "ObservabilityClient",
    "ObservabilityLogger", 
    "LogEntry",
    "LogLevel",
    "APIKey",
    "UsageMetrics",
    "ObservabilityError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "APIError",
]

# Default configuration
DEFAULT_BASE_URL = "https://observability.redducklabs.com/api/v1"
DEFAULT_TIMEOUT = 30
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_BATCH_SIZE = 100
DEFAULT_FLUSH_INTERVAL = 5  # seconds