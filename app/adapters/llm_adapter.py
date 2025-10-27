"""
Simple LLM Adapter for communicating with LLM providers.

This module provides a unified interface to interact with different LLM providers
(Ollama, OpenAI, etc.) through a common API.
"""

import json
import requests
from typing import Optional
from app.core.config import settings


class LLMAdapter:
    """
    Base adapter for LLM communication.
    Provides methods to generate text from prompts.
    """
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM adapter.
        
        Args:
            provider: LLM provider (ollama, openai). Defaults to config setting.
        """
        self.provider = provider or settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.base_url = settings.OLLAMA_URL
    
    def generate(
        self, 
        prompt: str, 
        temperature: Optional[float] = None,
        num_predict: Optional[int] = None,
        mode: str = "generate"
    ) -> str:
        """
        Generate text from a prompt using the configured LLM provider.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Temperature for text generation
            num_predict: Max tokens to generate (overrides config default)
            mode: Generation mode (for future use)
            
        Returns:
            Generated text response from LLM
            
        Raises:
            HTTPException: If LLM request fails
        """
        if self.provider == "ollama":
            return self._generate_ollama(prompt, temperature, num_predict)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _generate_ollama(self, prompt: str, temperature: Optional[float] = None, num_predict: Optional[int] = None) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: The prompt to send
            temperature: Temperature setting
            
        Returns:
            Generated text response
        """
        if temperature is None:
            temperature = settings.LLM_TEMPERATURE
        
        effective_num_predict = num_predict if num_predict is not None else settings.LLM_NUM_PREDICT
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "options": {
                "temperature": temperature,
                "num_predict": effective_num_predict
            }
        }
        
        try:
            response = requests.post(url, json=payload, stream=True, timeout=120)
            response.raise_for_status()
            
            # Parse streaming response
            full_output = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk_data = json.loads(line.decode("utf-8"))
                        if "response" in chunk_data:
                            full_output += chunk_data["response"]
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            return full_output.strip()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error connecting to Ollama: {e}")
        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")


# Singleton instance
_llm_adapter = None

def get_llm_adapter() -> LLMAdapter:
    """
    Get or create singleton LLM adapter instance.
    
    Returns:
        LLMAdapter instance
    """
    global _llm_adapter
    if _llm_adapter is None:
        _llm_adapter = LLMAdapter()
    return _llm_adapter

