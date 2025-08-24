"""Main client for Platform Observability SDK."""

import json
import time
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union, Any, Callable
from urllib.parse import urljoin
import logging
from concurrent.futures import ThreadPoolExecutor
import queue

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import LogEntry, LogLevel, APIKey, UsageMetrics
from .exceptions import (
    ObservabilityError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
)


logger = logging.getLogger(__name__)


class ObservabilityClient:
    """Main client for interacting with Platform Observability service."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://observability.redducklabs.com/api/v1",
        timeout: int = 30,
        retry_attempts: int = 3,
        verify_ssl: bool = True,
        batch_size: int = 100,
        batch_timeout: float = 5.0,
        enable_batching: bool = True,
        max_queue_size: int = 10000,
    ):
        """Initialize the Observability Client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API service
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
            verify_ssl: Whether to verify SSL certificates
            batch_size: Maximum number of logs per batch
            batch_timeout: Maximum time to wait before sending batch (seconds)
            enable_batching: Whether to enable automatic batching
            max_queue_size: Maximum size of internal log queue
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.enable_batching = enable_batching
        self.max_queue_size = max_queue_size
        
        # Batching infrastructure
        self._log_queue = queue.Queue(maxsize=max_queue_size)
        self._pending_logs = []
        self._batch_lock = threading.Lock()
        self._batch_timer = None
        self._shutdown_event = threading.Event()
        self._worker_thread = None
        self._rate_limit_info = {}
        
        # Error callback for async processing
        self.error_callback: Optional[Callable[[Exception], None]] = None
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retry_attempts,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"platform-observability-python-sdk/1.0.0",
        })
        
        # Verify connection
        self._verify_connection()
        
        # Start batch worker if batching is enabled
        if self.enable_batching:
            self._start_batch_worker()

    def _verify_connection(self) -> None:
        """Verify that the API key and connection are valid."""
        try:
            response = self._make_request("GET", "/health")
            if response.status_code != 200:
                raise AuthenticationError("Invalid API key or connection failed")
        except requests.exceptions.RequestException as e:
            raise ObservabilityError(f"Failed to connect to service: {str(e)}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> requests.Response:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            Response object
            
        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors
        """
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            
            # Extract rate limit info
            self._extract_rate_limit_info(response)
            
            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", f"HTTP {response.status_code}")
                except json.JSONDecodeError:
                    error_message = f"HTTP {response.status_code}: {response.text}"
                raise APIError(error_message, status_code=response.status_code)
            
            return response
            
        except requests.exceptions.Timeout:
            raise ObservabilityError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise ObservabilityError("Connection error")
        except requests.exceptions.RequestException as e:
            raise ObservabilityError(f"Request failed: {str(e)}")

    def ingest_logs(self, logs: List[Union[LogEntry, Dict]]) -> Dict[str, Any]:
        """Ingest log entries.
        
        Args:
            logs: List of log entries or dictionaries
            
        Returns:
            Response data with ingestion status
        """
        if not logs:
            raise ValidationError("No logs provided")
        
        # Convert log entries to dictionaries
        log_data = []
        for log in logs:
            if isinstance(log, LogEntry):
                log_data.append(log.to_dict())
            elif isinstance(log, dict):
                # Validate required fields
                if "message" not in log:
                    raise ValidationError("Log entry missing required 'message' field")
                log_data.append(log)
            else:
                raise ValidationError("Invalid log entry type")
        
        data = {"logs": log_data}
        response = self._make_request("POST", "/logs/ingest", data=data)
        return response.json()

    def ingest_log(
        self,
        message: str,
        level: Union[LogLevel, str] = LogLevel.INFO,
        source: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        fields: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Ingest a single log entry.
        
        Args:
            message: Log message
            level: Log level
            source: Source/application name
            labels: Key-value labels for filtering
            fields: Additional structured data
            timestamp: Log timestamp (defaults to now)
            
        Returns:
            Response data with ingestion status
        """
        log_entry = LogEntry(
            message=message,
            level=level,
            source=source,
            labels=labels or {},
            fields=fields or {},
            timestamp=timestamp or datetime.now(timezone.utc),
        )
        
        return self.ingest_logs([log_entry])

    def get_usage_analytics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> UsageMetrics:
        """Get usage analytics.
        
        Args:
            start_time: Start time for analytics period
            end_time: End time for analytics period
            
        Returns:
            Usage metrics
        """
        params = {}
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        
        response = self._make_request("GET", "/analytics/usage", params=params)
        data = response.json()
        return UsageMetrics.from_dict(data)

    def list_api_keys(self) -> List[APIKey]:
        """List all API keys for the authenticated user.
        
        Returns:
            List of API keys
        """
        response = self._make_request("GET", "/keys")
        data = response.json()
        return [APIKey.from_dict(key_data) for key_data in data]

    def create_api_key(
        self,
        name: str,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> APIKey:
        """Create a new API key.
        
        Args:
            name: API key name
            description: Optional description
            expires_at: Optional expiration date
            
        Returns:
            Created API key
        """
        data = {
            "name": name,
            "description": description,
        }
        if expires_at:
            data["expires_at"] = expires_at.isoformat()
        
        response = self._make_request("POST", "/keys", data=data)
        return APIKey.from_dict(response.json())

    def delete_api_key(self, key_id: str) -> None:
        """Delete an API key.
        
        Args:
            key_id: API key ID to delete
        """
        self._make_request("DELETE", f"/keys/{key_id}")

    def rotate_api_key(self, key_id: str) -> Dict[str, str]:
        """Rotate an API key (generate new key value).
        
        Args:
            key_id: API key ID to rotate
            
        Returns:
            Dictionary with new key value
        """
        response = self._make_request("PUT", f"/keys/{key_id}/rotate")
        return response.json()

    def get_key_metrics(self, key_id: str) -> Dict[str, Any]:
        """Get metrics for a specific API key.
        
        Args:
            key_id: API key ID
            
        Returns:
            Key metrics data
        """
        response = self._make_request("GET", f"/analytics/keys/{key_id}/metrics")
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check.
        
        Returns:
            Health status
        """
        response = self._make_request("GET", "/health")
        return response.json()

    def add_to_batch(
        self,
        message: str,
        level: Union[LogLevel, str] = LogLevel.INFO,
        source: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        fields: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Add a log entry to the batch queue for async processing.
        
        Args:
            message: Log message
            level: Log level
            source: Source/application name
            labels: Key-value labels for filtering
            fields: Additional structured data
            timestamp: Log timestamp (defaults to now)
        """
        if not self.enable_batching:
            # If batching is disabled, send immediately
            self.ingest_log(message, level, source, labels, fields, timestamp)
            return
        
        log_entry = LogEntry(
            message=message,
            level=level,
            source=source,
            labels=labels or {},
            fields=fields or {},
            timestamp=timestamp or datetime.now(timezone.utc),
        )
        
        try:
            self._log_queue.put_nowait(log_entry)
        except queue.Full:
            if self.error_callback:
                self.error_callback(ObservabilityError("Log queue is full"))
            else:
                logger.warning("Log queue is full, dropping log entry")

    def flush_batch(self, timeout: Optional[float] = None) -> None:
        """Flush any pending logs in the batch.
        
        Args:
            timeout: Maximum time to wait for flush to complete
        """
        if not self.enable_batching:
            return
        
        with self._batch_lock:
            if self._pending_logs:
                try:
                    self.ingest_logs(self._pending_logs)
                    self._pending_logs.clear()
                except Exception as e:
                    if self.error_callback:
                        self.error_callback(e)
                    else:
                        logger.error(f"Failed to flush batch: {e}")

    def set_error_callback(self, callback: Callable[[Exception], None]) -> None:
        """Set callback function for handling async errors.
        
        Args:
            callback: Function to call when async errors occur
        """
        self.error_callback = callback

    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get current rate limit information.
        
        Returns:
            Rate limit info from last request
        """
        return self._rate_limit_info.copy()

    def _start_batch_worker(self) -> None:
        """Start the background batch processing worker."""
        self._worker_thread = threading.Thread(target=self._batch_worker, daemon=True)
        self._worker_thread.start()

    def _batch_worker(self) -> None:
        """Background worker that processes batched logs."""
        while not self._shutdown_event.is_set():
            try:
                # Try to get a log entry from the queue
                try:
                    log_entry = self._log_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Add to pending batch
                with self._batch_lock:
                    self._pending_logs.append(log_entry)
                    
                    # Check if we should send the batch
                    should_send = (
                        len(self._pending_logs) >= self.batch_size or
                        self._should_send_batch_by_time()
                    )
                    
                    if should_send:
                        logs_to_send = self._pending_logs.copy()
                        self._pending_logs.clear()
                        self._cancel_batch_timer()
                        
                        # Send logs outside the lock
                        try:
                            self.ingest_logs(logs_to_send)
                        except Exception as e:
                            # Re-add logs to the front of pending
                            with self._batch_lock:
                                self._pending_logs = logs_to_send + self._pending_logs
                            if self.error_callback:
                                self.error_callback(e)
                            else:
                                logger.error(f"Failed to send batch: {e}")
                    else:
                        # Start timer if not already running
                        self._start_batch_timer()
                
                self._log_queue.task_done()
                
            except Exception as e:
                if self.error_callback:
                    self.error_callback(e)
                else:
                    logger.error(f"Error in batch worker: {e}")

    def _should_send_batch_by_time(self) -> bool:
        """Check if batch should be sent based on time."""
        if not self._pending_logs:
            return False
        
        # For simplicity, we'll use the timer mechanism
        return False

    def _start_batch_timer(self) -> None:
        """Start timer for batch timeout."""
        if self._batch_timer is None:
            self._batch_timer = threading.Timer(self.batch_timeout, self._send_batch_on_timeout)
            self._batch_timer.start()

    def _cancel_batch_timer(self) -> None:
        """Cancel the batch timer."""
        if self._batch_timer:
            self._batch_timer.cancel()
            self._batch_timer = None

    def _send_batch_on_timeout(self) -> None:
        """Send batch when timer expires."""
        with self._batch_lock:
            if self._pending_logs:
                logs_to_send = self._pending_logs.copy()
                self._pending_logs.clear()
                
                try:
                    self.ingest_logs(logs_to_send)
                except Exception as e:
                    # Re-add logs to pending
                    self._pending_logs = logs_to_send + self._pending_logs
                    if self.error_callback:
                        self.error_callback(e)
                    else:
                        logger.error(f"Failed to send batch on timeout: {e}")
            
            self._batch_timer = None

    def _extract_rate_limit_info(self, response: requests.Response) -> None:
        """Extract rate limit information from response headers."""
        headers = response.headers
        
        rate_limit_info = {}
        if 'X-RateLimit-Limit' in headers:
            rate_limit_info['limit'] = int(headers['X-RateLimit-Limit'])
        if 'X-RateLimit-Remaining' in headers:
            rate_limit_info['remaining'] = int(headers['X-RateLimit-Remaining'])
        if 'X-RateLimit-Reset' in headers:
            rate_limit_info['reset'] = int(headers['X-RateLimit-Reset'])
        if 'Retry-After' in headers:
            rate_limit_info['retry_after'] = int(headers['Retry-After'])
        
        if rate_limit_info:
            self._rate_limit_info = rate_limit_info

    def close(self) -> None:
        """Close the client session and cleanup resources."""
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel batch timer
        self._cancel_batch_timer()
        
        # Wait for worker thread to finish
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)
        
        # Flush any remaining logs
        self.flush_batch()
        
        # Close session
        if hasattr(self, "session"):
            self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()