"""Exception classes for Platform Observability SDK."""

from typing import Optional


class ObservabilityError(Exception):
    """Base exception for all Observability SDK errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(ObservabilityError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class RateLimitError(ObservabilityError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class ValidationError(ObservabilityError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class APIError(ObservabilityError):
    """Raised for general API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, status_code)


class ConnectionError(ObservabilityError):
    """Raised when connection to service fails."""
    
    def __init__(self, message: str = "Failed to connect to observability service"):
        super().__init__(message)


class TimeoutError(ObservabilityError):
    """Raised when request times out."""
    
    def __init__(self, message: str = "Request timed out"):
        super().__init__(message)


class ConfigurationError(ObservabilityError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str):
        super().__init__(message)


class RetryExhaustedError(ObservabilityError):
    """Raised when all retry attempts are exhausted."""
    
    def __init__(self, message: str = "All retry attempts exhausted"):
        super().__init__(message)