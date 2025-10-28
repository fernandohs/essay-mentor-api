"""
Simple LLM Adapter for communicating with LLM providers.

This module provides a unified interface to interact with different LLM providers
(Ollama, OpenAI, etc.) through a common API. Uses the Registry Pattern for
easy extensibility.
"""

from typing import Optional
from app.core.config import settings
from app.adapters.registry import LLMProviderRegistry
from app.adapters.base import BaseLLMAdapter

# Import and register providers
from app.adapters.providers.ollama import OllamaAdapter
from app.adapters.providers.openai import OpenAIAdapter

# Register providers
LLMProviderRegistry.register("ollama", OllamaAdapter)
LLMProviderRegistry.register("openai", OpenAIAdapter)
LLMProviderRegistry.register("qwen2.5", OllamaAdapter)  # Qwen uses Ollama


class LLMAdapter:
    """
    Unified LLM adapter that wraps provider-specific adapters.
    Provides backward compatibility with existing code.
    """
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize LLM adapter.
        
        Args:
            provider: LLM provider (ollama, openai, qwen2.5). Defaults to config setting.
            model: Specific model name to use. Defaults to config setting.
        """
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or settings.LLM_MODEL
        
        # Determine base URL and API key based on provider
        if self.provider in ["ollama", "qwen2.5"]:
            base_url = settings.OLLAMA_URL
            api_key = None
        elif self.provider == "openai":
            base_url = settings.OPENAI_BASE_URL
            api_key = settings.OPENAI_API_KEY
        else:
            # Default to Ollama for unknown providers
            base_url = settings.OLLAMA_URL
            api_key = None
        
        # Get the actual adapter from registry
        self._adapter = LLMProviderRegistry.get_adapter(
            provider=self.provider,
            model=self.model,
            base_url=base_url,
            api_key=api_key
        )
    
    def generate(
        self, 
        prompt: str, 
        temperature: Optional[float] = None,
        num_predict: Optional[int] = None,
        mode: str = "generate",
        function: Optional[str] = None,
        use_fallback: bool = True
    ) -> str:
        """
        Generate text from a prompt using the configured LLM provider.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Temperature for text generation
            num_predict: Max tokens to generate (overrides config default)
            mode: Generation mode (for future use)
            function: Function name for fallback chain selection
            use_fallback: Whether to use fallback system for OpenAI
            
        Returns:
            Generated text response from LLM
            
        Raises:
            HTTPException: If LLM request fails
        """
        # Use fallback for OpenAI if enabled
        if self.provider == "openai" and use_fallback and function:
            return self._generate_with_fallback(prompt, temperature, num_predict, function)
        
        # Use the registered adapter
        return self._adapter.generate(prompt, temperature, num_predict)
    
    def _generate_with_fallback(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        num_predict: Optional[int] = None,
        function: Optional[str] = None
    ) -> str:
        """
        Generate text using OpenAI with fallback system.
        
        Args:
            prompt: The prompt to send to OpenAI
            temperature: Temperature setting
            num_predict: Max tokens to generate
            function: Function name for fallback chain
            
        Returns:
            Generated text response from OpenAI
        """
        from app.utils.fallback_manager import get_fallback_manager
        
        fallback_manager = get_fallback_manager()
        
        # Create a function that returns an adapter for a specific model
        def get_adapter_for_model(provider: str, model: str):
            return LLMAdapter(provider=provider, model=model)
        
        # Execute with fallback
        if function is None:
            raise ValueError("Function parameter is required for fallback execution")
            
        result = fallback_manager.execute_with_fallback(
            function=function,
            prompt=prompt,
            temperature=temperature,
            num_predict=num_predict,
            llm_adapter_func=get_adapter_for_model
        )
        
        if result.success:
            return result.response or ""
        else:
            raise RuntimeError(f"All fallback models failed: {result.error_message}")


def get_llm_adapter(provider: Optional[str] = None, model: Optional[str] = None) -> LLMAdapter:
    """
    Get or create LLM adapter instance with optional permitting instantiation for specific providers/models.
    
    Args:
        provider: LLM provider (ollama, openai, qwen2.5). If None, uses default.
        model: Specific model name. If None, uses default.
        
    Returns:
        LLMAdapter instance configured for the specified provider and model
        
    Note:
        This function can be called with provider/model arguments to use different models
        for different functions without creating a global singleton.
    """
    # Create adapter with specified provider and model
    return LLMAdapter(provider=provider, model=model)


__all__ = ["LLMAdapter", "get_llm_adapter"]
