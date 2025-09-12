"""Simple in-memory metrics collection for the music recommender system.

This module provides lightweight metrics tracking for recommendation requests,
including counters for successes, failures, and basic latency tracking.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class MetricsData:
    """Container for application metrics."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    request_types: Dict[str, int] = field(default_factory=dict)

    @property
    def average_latency_ms(self) -> float:
        """Calculate average latency in milliseconds."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100.0


class MetricsCollector:
    """Thread-safe in-memory metrics collector."""

    def __init__(self):
        """Initialize the metrics collector."""
        self._data = MetricsData()
        self._lock = threading.Lock()

    def record_request_start(self) -> float:
        """Record the start of a request and return start time."""
        return time.time()

    def record_request_success(self, start_time: float, request_type: str = "unknown"):
        """Record a successful request with timing."""
        latency_ms = (time.time() - start_time) * 1000

        with self._lock:
            self._data.total_requests += 1
            self._data.successful_requests += 1
            self._data.total_latency_ms += latency_ms

            if request_type in self._data.request_types:
                self._data.request_types[request_type] += 1
            else:
                self._data.request_types[request_type] = 1

    def record_request_failure(self, request_type: str = "unknown"):
        """Record a failed request."""
        with self._lock:
            self._data.total_requests += 1
            self._data.failed_requests += 1

            failure_key = f"{request_type}_failures"
            if failure_key in self._data.request_types:
                self._data.request_types[failure_key] += 1
            else:
                self._data.request_types[failure_key] = 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics as a dictionary."""
        with self._lock:
            return {
                "total_requests": self._data.total_requests,
                "successful_requests": self._data.successful_requests,
                "failed_requests": self._data.failed_requests,
                "success_rate_percent": round(self._data.success_rate, 2),
                "average_latency_ms": round(self._data.average_latency_ms, 2),
                "request_types": dict(self._data.request_types),
            }

    def reset_metrics(self):
        """Reset all metrics to zero."""
        with self._lock:
            self._data = MetricsData()


# Global metrics collector instance
metrics_collector = MetricsCollector()
