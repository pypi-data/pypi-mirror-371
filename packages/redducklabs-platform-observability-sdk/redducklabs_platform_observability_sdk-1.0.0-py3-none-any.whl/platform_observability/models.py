"""Data models for Platform Observability SDK."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import json


class LogLevel(Enum):
    """Log levels enum."""
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    WARNING = "warning"  # Alias for warn
    ERROR = "error"
    FATAL = "fatal"
    CRITICAL = "critical"  # Alias for fatal

    def __str__(self) -> str:
        return self.value


@dataclass
class LogEntry:
    """Represents a log entry."""
    message: str
    level: Union[LogLevel, str] = LogLevel.INFO
    source: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    fields: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Post-initialization processing."""
        # Convert string level to LogLevel enum
        if isinstance(self.level, str):
            try:
                self.level = LogLevel(self.level.lower())
            except ValueError:
                # If invalid level, default to INFO
                self.level = LogLevel.INFO
        
        # Set default timestamp if not provided
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        
        # Ensure timestamp is timezone-aware
        elif self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization."""
        return {
            "message": self.message,
            "level": self.level.value if isinstance(self.level, LogLevel) else str(self.level),
            "source": self.source,
            "labels": self.labels,
            "fields": self.fields,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
        """Create LogEntry from dictionary."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        
        return cls(
            message=data["message"],
            level=data.get("level", LogLevel.INFO),
            source=data.get("source"),
            labels=data.get("labels", {}),
            fields=data.get("fields", {}),
            timestamp=timestamp,
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "LogEntry":
        """Create LogEntry from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class APIKey:
    """Represents an API key."""
    id: str
    name: str
    description: Optional[str] = None
    key: Optional[str] = None  # Only populated when creating/rotating
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIKey":
        """Create APIKey from dictionary."""
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        
        expires_at = None
        if data.get("expires_at"):
            expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
        
        last_used = None
        if data.get("last_used"):
            last_used = datetime.fromisoformat(data["last_used"].replace("Z", "+00:00"))
        
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            key=data.get("key"),
            created_at=created_at,
            expires_at=expires_at,
            last_used=last_used,
            is_active=data.get("is_active", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "key": self.key,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "is_active": self.is_active,
        }

    @property
    def is_expired(self) -> bool:
        """Check if the API key is expired."""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def masked_key(self) -> Optional[str]:
        """Get masked version of the key for display."""
        if not self.key:
            return None
        if len(self.key) <= 8:
            return "*" * len(self.key)
        return self.key[:4] + "*" * (len(self.key) - 8) + self.key[-4:]


@dataclass
class DailyUsageMetric:
    """Daily usage metrics."""
    date: datetime
    request_count: int = 0
    logs_ingested: int = 0
    data_volume_bytes: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DailyUsageMetric":
        """Create from dictionary."""
        date = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
        return cls(
            date=date,
            request_count=data.get("request_count", 0),
            logs_ingested=data.get("logs_ingested", 0),
            data_volume_bytes=data.get("data_volume_bytes", 0),
        )


@dataclass
class APIKeyUsage:
    """API key usage breakdown."""
    api_key_id: str
    api_key_name: str
    request_count: int = 0
    logs_ingested: int = 0
    data_volume_bytes: int = 0
    last_used: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIKeyUsage":
        """Create from dictionary."""
        last_used = None
        if data.get("last_used"):
            last_used = datetime.fromisoformat(data["last_used"].replace("Z", "+00:00"))
        
        return cls(
            api_key_id=data["api_key_id"],
            api_key_name=data["api_key_name"],
            request_count=data.get("request_count", 0),
            logs_ingested=data.get("logs_ingested", 0),
            data_volume_bytes=data.get("data_volume_bytes", 0),
            last_used=last_used,
        )


@dataclass
class UsageMetrics:
    """Usage analytics and metrics."""
    user_id: str
    total_requests: int = 0
    total_logs_ingested: int = 0
    data_volume_bytes: int = 0
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    api_key_breakdown: List[APIKeyUsage] = field(default_factory=list)
    daily_usage: List[DailyUsageMetric] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageMetrics":
        """Create from dictionary."""
        period_start = None
        if data.get("period_start"):
            period_start = datetime.fromisoformat(data["period_start"].replace("Z", "+00:00"))
        
        period_end = None
        if data.get("period_end"):
            period_end = datetime.fromisoformat(data["period_end"].replace("Z", "+00:00"))
        
        api_key_breakdown = [
            APIKeyUsage.from_dict(usage_data) 
            for usage_data in data.get("api_key_breakdown", [])
        ]
        
        daily_usage = [
            DailyUsageMetric.from_dict(daily_data)
            for daily_data in data.get("daily_usage", [])
        ]
        
        return cls(
            user_id=data["user_id"],
            total_requests=data.get("total_requests", 0),
            total_logs_ingested=data.get("total_logs_ingested", 0),
            data_volume_bytes=data.get("data_volume_bytes", 0),
            period_start=period_start,
            period_end=period_end,
            api_key_breakdown=api_key_breakdown,
            daily_usage=daily_usage,
        )

    @property
    def total_data_volume_mb(self) -> float:
        """Get total data volume in MB."""
        return self.data_volume_bytes / (1024 * 1024)

    @property
    def total_data_volume_gb(self) -> float:
        """Get total data volume in GB."""
        return self.data_volume_bytes / (1024 * 1024 * 1024)

    @property
    def average_logs_per_request(self) -> float:
        """Get average logs per request."""
        if self.total_requests == 0:
            return 0.0
        return self.total_logs_ingested / self.total_requests

    @property
    def average_data_per_log(self) -> float:
        """Get average data per log in bytes."""
        if self.total_logs_ingested == 0:
            return 0.0
        return self.data_volume_bytes / self.total_logs_ingested


@dataclass
class KeyMetrics:
    """Metrics for a specific API key."""
    api_key_id: str
    total_requests: int = 0
    total_logs: int = 0
    data_volume: int = 0
    last_used: Optional[datetime] = None
    error_rate: float = 0.0
    avg_response_time: float = 0.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeyMetrics":
        """Create from dictionary."""
        last_used = None
        if data.get("last_used"):
            last_used = datetime.fromisoformat(data["last_used"].replace("Z", "+00:00"))
        
        return cls(
            api_key_id=data["api_key_id"],
            total_requests=data.get("total_requests", 0),
            total_logs=data.get("total_logs", 0),
            data_volume=data.get("data_volume", 0),
            last_used=last_used,
            error_rate=data.get("error_rate", 0.0),
            avg_response_time=data.get("avg_response_time", 0.0),
        )