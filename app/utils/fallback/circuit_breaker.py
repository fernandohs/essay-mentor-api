"""
Circuit breaker implementation for fallback management.
Handles circuit breaker state and failure tracking.
"""
import time
from typing import Dict, Any


class CircuitBreaker:
    """Manages circuit breaker state for individual models."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 300):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.breakers: Dict[str, Dict[str, Any]] = {}
    
    def is_open(self, model: str) -> bool:
        """Check if circuit breaker is open for a model."""
        if model not in self.breakers:
            return False
        
        breaker = self.breakers[model]
        if breaker["state"] == "open":
            # Check if recovery timeout has passed
            if time.time() - breaker["last_failure"] > self.recovery_timeout:
                breaker["state"] = "half_open"
                breaker["half_open_calls"] = 0
                return False
            return True
        
        return False
    
    def record_failure(self, model: str):
        """Record a failure for circuit breaker."""
        if model not in self.breakers:
            self.breakers[model] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure": 0,
                "half_open_calls": 0
            }
        
        breaker = self.breakers[model]
        breaker["failure_count"] += 1
        breaker["last_failure"] = time.time()
        
        # Open circuit breaker after threshold failures
        if breaker["failure_count"] >= self.failure_threshold:
            breaker["state"] = "open"
    
    def record_success(self, model: str):
        """Record a success for circuit breaker."""
        if model in self.breakers:
            breaker = self.breakers[model]
            breaker["failure_count"] = 0
            breaker["state"] = "closed"
    
    def get_state(self, model: str) -> str:
        """Get current circuit breaker state for a model."""
        if model not in self.breakers:
            return "closed"
        return self.breakers[model]["state"]
    
    def get_failure_count(self, model: str) -> int:
        """Get failure count for a model."""
        if model not in self.breakers:
            return 0
        return self.breakers[model]["failure_count"]
