"""
LLM Provider Registry.
Manages registration and instantiation of LLM adapters.
"""

from typing import Dict, Type, Optional, Any
from app.adapters.base import BaseLLMAdapter


class LLMProviderRegistry:
    """
    Registry for LLM providers.
    Handles registration and instantiation of different LLM adapters.
    """
    
    _providers: Dict[str, Type[BaseLLMAdapter]] = {}
    _aliases: Dict[str, str] = {}
    
    @classmethod
    def register(cls, name: str, adapter_class: Type[BaseLLMAdapter]):
        """
        Register an LLM adapter.
        
        Args:
            name: Provider name (e.g., "ollama", "openai")
            adapter_class: The adapter class to register
        """
        cls._providers[name] = adapter_class
    
    @classmethod
    def register_alias(cls, alias: str, provider: str):
        """
        Register an alias for a provider.
        
        Args:
            alias: Alias name (e.g., "qwen2.5" -> "ollama")
            provider: Provider name to alias to
        """
        cls._aliases[alias] = provider
    
    @classmethod
    def get_adapter(cls, provider: str, **kwargs) -> BaseLLMAdapter:
        """
        Get an instance of an LLM adapter.
        
        Args:
            provider: Provider name or alias
            **kwargs: Arguments to pass to the adapter constructor
            
        Returns:
            An instance of the appropriate LLM adapter
            
        Raises:
            ValueError: If provider is not registered
        """
        # Check if it's an alias
        actual_provider = cls._aliases.get(provider, provider)
        
        # Get the adapter class
        adapter_class = cls._providers.get(actual_provider)
        
        if adapter_class is None:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Available providers: {available}"
            )
        
        # Instantiate the adapter
        return adapter_class(**kwargs)
    
    @classmethod
    def list_providers(cls) -> list:
        """List all registered providers."""
        return list(cls._providers.keys())
    
    @classmethod
    def list_aliases(cls) -> dict:
        """List all registered aliases."""
        return cls._aliases.copy()


# Convenience function for backward compatibility
def get_adapter_for_provider(provider: str, **kwargs) -> BaseLLMAdapter:
    """
    Get an adapter instance for a specific provider.
    
    Args:
        provider: Provider name or alias
        **kwargs: Arguments for the adapter
        
    Returns:
        An LLM adapter instance
    """
    return LLMProviderRegistry.get_adapter(provider, **kwargs)


__all__ = ["LLMProviderRegistry", "get_adapter_for_provider"]

