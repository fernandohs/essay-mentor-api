"""
Fallback system for OpenAI models with retry logic.
This module now delegates to the refactored components in app/utils/fallback/
"""
from app.utils.fallback import (
    FallbackManager,
    FallbackResult,
    RetryableError,
    NonRetryableError,
    get_fallback_manager
)

# Re-export for backward compatibility
__all__ = [
    "FallbackManager",
    "FallbackResult", 
    "RetryableError",
    "NonRetryableError",
    "get_fallback_manager"
]