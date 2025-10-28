"""
Base LLM Adapter abstract class.
All LLM providers must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMAdapter(ABC):
    """
    Abstract base class for LLM adapters.
    All LLM provider implementations must inherit from this class.
    """
    
    def __init__(self, model: str, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the adapter.
        
        Args:
            model: The model name to use
            base_url: The base URL for the LLM API
            api_key: Optional API key for authentication
        """
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        num_predict: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Temperature setting for generation
            num_predict: Maximum number of tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response from the LLM
            
        Raises:
            ConnectionError: If LLM request fails
        """
        pass
    
    def __repr__(self):
        """String representation of the adapter."""
        return f"{self.__class__.__name__}(model={self.model}, base_url={self.base_url})"

__all__ = ["BaseLLMAdapter"]

