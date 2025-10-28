"""
Ollama LLM Provider.
"""

import json
import requests
from typing import Optional
from app.adapters.base import BaseLLMAdapter
from app.core.config import settings


class OllamaAdapter(BaseLLMAdapter):
    """
    Adapter for Ollama LLM provider.
    Supports local Ollama models like Llama, Mistral, Qwen, etc.
    """
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        num_predict: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: The prompt to send
            temperature: Temperature setting
            num_predict: Maximum tokens to generate
            
        Returns:
            Generated text response
            
        Raises:
            ConnectionError: If connection to Ollama fails
        """
        if temperature is None:
            temperature = settings.LLM_TEMPERATURE
        
        effective_num_predict = num_predict if num_predict is not None else settings.LLM_NUM_PREDICT
        
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": True,
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
                        # Handle both /api/generate and /api/chat formats
                        if "response" in chunk_data:
                            # /api/generate format
                            full_output += chunk_data["response"]
                        elif "message" in chunk_data and "content" in chunk_data["message"]:
                            # /api/chat format
                            full_output += chunk_data["message"]["content"]
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            return full_output.strip()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error connecting to Ollama: {e}")
        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")


__all__ = ["OllamaAdapter"]

