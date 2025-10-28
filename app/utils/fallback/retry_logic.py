"""
Retry logic implementation for fallback management.
Handles retry calculations and delay strategies.
"""
import time
import random
from typing import Dict, List
from dataclasses import dataclass

from app.models.usage import RetryConfig


@dataclass
class RetryAttempt:
    """Represents a retry attempt."""
    attempt_number: int
    delay_seconds: float
    max_retries: int
    is_final_attempt: bool


class RetryLogic:
    """Manages retry logic and delay calculations."""
    
    def __init__(self):
        """Initialize retry logic with default configurations."""
        self.retry_configs = self._get_default_retry_configs()
    
    def _get_default_retry_configs(self) -> Dict[str, RetryConfig]:
        """Get default retry configurations for each model."""
        return {
            "gpt-4o": RetryConfig(
                model="gpt-4o",
                max_retries=2,
                base_delay=2.0,
                max_delay=10.0,
                exponential_backoff=True,
                retryable_errors=["rate_limit", "timeout", "service_unavailable"]
            ),
            "gpt-4o-mini": RetryConfig(
                model="gpt-4o-mini",
                max_retries=3,
                base_delay=1.5,
                max_delay=8.0,
                exponential_backoff=True,
                retryable_errors=["rate_limit", "timeout", "service_unavailable", "connection_error"]
            ),
            "gpt-3.5-turbo": RetryConfig(
                model="gpt-3.5-turbo",
                max_retries=5,
                base_delay=1.0,
                max_delay=5.0,
                exponential_backoff=True,
                retryable_errors=["rate_limit", "timeout", "service_unavailable", "connection_error", "internal_server_error"]
            ),
            # Default config for unknown models (like Ollama)
            "default": RetryConfig(
                model="default",
                max_retries=3,
                base_delay=1.0,
                max_delay=5.0,
                exponential_backoff=True,
                retryable_errors=["rate_limit", "timeout", "service_unavailable"]
            )
        }
    
    def get_retry_config(self, model: str) -> RetryConfig:
        """Get retry configuration for a specific model."""
        return self.retry_configs.get(model, self.retry_configs["default"])
    
    def calculate_delay(self, retry_count: int, base_delay: float, max_delay: float, exponential: bool = True) -> float:
        """
        Calculate delay for retry with exponential backoff.
        
        Args:
            retry_count: Current retry attempt number (0-based)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            exponential: Whether to use exponential backoff
            
        Returns:
            Delay in seconds
        """
        if not exponential:
            return base_delay
        
        delay = base_delay * (2 ** retry_count)
        delay = min(delay, max_delay)
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.1, 0.3) * delay  # noqa: B311
        return delay + jitter
    
    def should_retry(self, retry_count: int, max_retries: int, error_type: str, retryable_errors: List[str]) -> bool:
        """
        Determine if a retry should be attempted.
        
        Args:
            retry_count: Current retry attempt number
            max_retries: Maximum number of retries allowed
            error_type: Type of error that occurred
            retryable_errors: List of retryable error types
            
        Returns:
            True if retry should be attempted
        """
        if retry_count >= max_retries:
            return False
        
        return error_type in retryable_errors
    
    def get_retry_attempts(self, model: str) -> List[RetryAttempt]:
        """
        Get list of retry attempts for a model.
        
        Args:
            model: Model name
            
        Returns:
            List of RetryAttempt objects
        """
        config = self.get_retry_config(model)
        attempts = []
        
        for attempt_num in range(config.max_retries + 1):
            delay = self.calculate_delay(
                attempt_num,
                config.base_delay,
                config.max_delay,
                config.exponential_backoff
            )
            
            attempts.append(RetryAttempt(
                attempt_number=attempt_num,
                delay_seconds=delay,
                max_retries=config.max_retries,
                is_final_attempt=(attempt_num == config.max_retries)
            ))
        
        return attempts
    
    def wait_for_retry(self, delay_seconds: float):
        """Wait for the specified delay before retry."""
        time.sleep(delay_seconds)
