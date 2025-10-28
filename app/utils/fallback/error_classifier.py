"""
Error classification for fallback management.
Handles error type detection and retryability determination.
"""
from enum import Enum
from typing import Tuple


class RetryableError(str, Enum):
    """Types of errors that should trigger retries."""
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    SERVICE_UNAVAILABLE = "service_unavailable"
    CONNECTION_ERROR = "connection_error"
    INTERNAL_SERVER_ERROR = "internal_server_error"


class NonRetryableError(str, Enum):
    """Types of errors that should not trigger retries."""
    INVALID_API_KEY = "invalid_api_key"
    MODEL_NOT_FOUND = "model_not_found"
    INVALID_REQUEST = "invalid_request"
    QUOTA_EXCEEDED = "quota_exceeded"
    CONTENT_FILTER = "content_filter"


class ErrorClassifier:
    """Classifies errors and determines retryability."""
    
    def __init__(self):
        """Initialize error classifier."""
        self.retryable_patterns = {
            RetryableError.RATE_LIMIT: ["rate limit", "429", "too many requests"],
            RetryableError.TIMEOUT: ["timeout", "timed out", "connection timeout"],
            RetryableError.SERVICE_UNAVAILABLE: ["service unavailable", "503", "server error"],
            RetryableError.CONNECTION_ERROR: ["connection", "network", "connection refused"],
            RetryableError.INTERNAL_SERVER_ERROR: ["internal server error", "500", "server error"]
        }
        
        self.non_retryable_patterns = {
            NonRetryableError.INVALID_API_KEY: ["invalid api key", "401", "unauthorized", "authentication"],
            NonRetryableError.MODEL_NOT_FOUND: ["model not found", "404", "model does not exist"],
            NonRetryableError.INVALID_REQUEST: ["invalid request", "400", "bad request", "malformed"],
            NonRetryableError.QUOTA_EXCEEDED: ["quota exceeded", "billing", "payment required"],
            NonRetryableError.CONTENT_FILTER: ["content filter", "policy violation", "inappropriate"]
        }
    
    def classify_error(self, error: Exception) -> Tuple[str, bool]:
        """
        Classify error type and determine if it's retryable.
        
        Args:
            error: Exception to classify
            
        Returns:
            Tuple of (error_type, is_retryable)
        """
        error_str = str(error).lower()
        
        # Check for retryable errors first
        for error_type, patterns in self.retryable_patterns.items():
            if any(pattern in error_str for pattern in patterns):
                return error_type.value, True
        
        # Check for non-retryable errors
        for error_type, patterns in self.non_retryable_patterns.items():
            if any(pattern in error_str for pattern in patterns):
                return error_type.value, False
        
        # Default to retryable for unknown errors (conservative approach)
        return "unknown", True
    
    def is_retryable(self, error: Exception) -> bool:
        """
        Quick check if an error is retryable.
        
        Args:
            error: Exception to check
            
        Returns:
            True if error is retryable
        """
        _, is_retryable = self.classify_error(error)
        return is_retryable
    
    def get_error_type(self, error: Exception) -> str:
        """
        Get the error type without retryability check.
        
        Args:
            error: Exception to classify
            
        Returns:
            Error type string
        """
        error_type, _ = self.classify_error(error)
        return error_type
    
    def is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is a rate limit error."""
        error_type, _ = self.classify_error(error)
        return error_type == RetryableError.RATE_LIMIT.value
    
    def is_timeout_error(self, error: Exception) -> bool:
        """Check if error is a timeout error."""
        error_type, _ = self.classify_error(error)
        return error_type == RetryableError.TIMEOUT.value
    
    def is_authentication_error(self, error: Exception) -> bool:
        """Check if error is an authentication error."""
        error_type, _ = self.classify_error(error)
        return error_type == NonRetryableError.INVALID_API_KEY.value
