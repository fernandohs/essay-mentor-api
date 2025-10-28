"""
Fallback manager implementation.
Orchestrates fallback chains, retry logic, and circuit breakers.
"""
import time
from typing import List, Optional, Callable, Dict
from dataclasses import dataclass

from app.models.usage import FallbackConfig, Function
from app.utils.token_tracker import get_token_tracker, estimate_tokens

from .circuit_breaker import CircuitBreaker
from .retry_logic import RetryLogic
from .error_classifier import ErrorClassifier, RetryableError, NonRetryableError


@dataclass
class FallbackResult:
    """Result of a fallback attempt."""
    success: bool
    response: Optional[str] = None
    model_used: Optional[str] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    fallback_reason: Optional[str] = None


class FallbackManager:
    """Manages fallback chains and retry logic for LLM models."""
    
    def __init__(self):
        """Initialize fallback manager with default configurations."""
        self.fallback_configs = self._get_default_fallback_configs()
        self.circuit_breaker = CircuitBreaker()
        self.retry_logic = RetryLogic()
        self.error_classifier = ErrorClassifier()
    
    def _get_default_fallback_configs(self) -> Dict[str, FallbackConfig]:
        """Get default fallback configurations for each function."""
        return {
            "ai_detection": FallbackConfig(
                function=Function.AI_DETECTION,
                primary_model="gpt-4o",
                fallback_chain=["gpt-4o-mini", "gpt-3.5-turbo"],
                max_retries_per_model=2,
                base_delay_seconds=1.0,
                max_delay_seconds=5.0,
                exponential_backoff=True
            ),
            "feedback": FallbackConfig(
                function=Function.FEEDBACK,
                primary_model="gpt-4o",
                fallback_chain=["gpt-4o-mini", "gpt-3.5-turbo"],
                max_retries_per_model=3,
                base_delay_seconds=1.5,
                max_delay_seconds=8.0,
                exponential_backoff=True
            ),
            "guidance": FallbackConfig(
                function=Function.GUIDANCE,
                primary_model="gpt-4o-mini",
                fallback_chain=["gpt-3.5-turbo"],
                max_retries_per_model=3,
                base_delay_seconds=1.0,
                max_delay_seconds=5.0,
                exponential_backoff=True
            ),
            "section_check": FallbackConfig(
                function=Function.SECTION_CHECK,
                primary_model="gpt-4o-mini",
                fallback_chain=["gpt-3.5-turbo"],
                max_retries_per_model=3,
                base_delay_seconds=1.0,
                max_delay_seconds=5.0,
                exponential_backoff=True
            )
        }
    
    def get_fallback_chain(self, function: str) -> List[str]:
        """Get the fallback chain for a specific function."""
        config = self.fallback_configs.get(function)
        if not config:
            return ["gpt-4o-mini"]  # Default fallback
        
        return [config.primary_model] + config.fallback_chain
    
    def execute_with_fallback(
        self,
        function: str,
        prompt: str,
        temperature: Optional[float] = None,
        num_predict: Optional[int] = None,
        llm_adapter_func: Optional[Callable] = None
    ) -> FallbackResult:
        """
        Execute LLM call with fallback chain and retry logic.
        
        Args:
            function: Function name (ai_detection, feedback, etc.)
            prompt: Prompt to send to LLM
            temperature: Temperature setting
            num_predict: Max tokens to generate
            llm_adapter_func: Function to call LLM adapter
            
        Returns:
            FallbackResult with success status and details
        """
        if not llm_adapter_func:
            raise ValueError("llm_adapter_func is required")
        
        fallback_chain = self.get_fallback_chain(function)
        tracker = get_token_tracker()
        tokens_input = estimate_tokens(prompt)
        
        for model_index, model in enumerate(fallback_chain):
            # Check circuit breaker
            if self.circuit_breaker.is_open(model):
                continue
            
            retry_config = self.retry_logic.get_retry_config(model)
            
            # Try model with retries
            for retry_count in range(retry_config.max_retries + 1):
                try:
                    start_time = time.time()
                    
                    # Create adapter for this specific model
                    adapter = llm_adapter_func(provider="openai", model=model)  # type: ignore
                    response = adapter.generate(prompt, temperature, num_predict)
                    
                    response_time_ms = int((time.time() - start_time) * 1000)
                    tokens_output = estimate_tokens(response)
                    
                    # Log successful usage
                    tracker.log_usage(
                        provider="openai",
                        model=model,
                        function=function,
                        tokens_input=tokens_input,
                        tokens_output=tokens_output,
                        response_time_ms=response_time_ms,
                        status="success",
                        fallback_model=model if model_index > 0 else None,
                        retry_count=retry_count
                    )
                    
                    # Record success for circuit breaker
                    self.circuit_breaker.record_success(model)
                    
                    return FallbackResult(
                        success=True,
                        response=response,
                        model_used=model,
                        retry_count=retry_count,
                        fallback_reason=f"Used fallback model {model}" if model_index > 0 else None
                    )
                    
                except Exception as e:
                    error_type, is_retryable = self.error_classifier.classify_error(e)
                    
                    if not is_retryable:
                        # Non-retryable error, move to next model
                        break
                    
                    if retry_count < retry_config.max_retries:
                        # Calculate delay and wait
                        delay = self.retry_logic.calculate_delay(
                            retry_count,
                            retry_config.base_delay,
                            retry_config.max_delay,
                            retry_config.exponential_backoff
                        )
                        self.retry_logic.wait_for_retry(delay)
                    else:
                        # Max retries reached, record failure and move to next model
                        self.circuit_breaker.record_failure(model)
                        break
        
        # All models failed
        tracker.log_usage(
            provider="openai",
            model="unknown",
            function=function,
            tokens_input=tokens_input,
            tokens_output=0,
            response_time_ms=0,
            status="failed",
            error_message="All fallback models failed"
        )
        
        return FallbackResult(
            success=False,
            error_message="All fallback models failed",
            fallback_reason="Exhausted all fallback options"
        )
    
    def get_circuit_breaker_state(self, model: str) -> str:
        """Get circuit breaker state for a model."""
        return self.circuit_breaker.get_state(model)
    
    def get_failure_count(self, model: str) -> int:
        """Get failure count for a model."""
        return self.circuit_breaker.get_failure_count(model)
    
    def reset_circuit_breaker(self, model: str):
        """Reset circuit breaker for a model."""
        self.circuit_breaker.record_success(model)

# Global fallback manager instance
_fallback_manager = None

def get_fallback_manager() -> FallbackManager:
    """Get or create global fallback manager instance."""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = FallbackManager()
    return _fallback_manager
