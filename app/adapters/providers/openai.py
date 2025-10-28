"""
OpenAI LLM Provider.
"""

import json
import requests
from typing import Optional
from app.adapters.base import BaseLLMAdapter
from app.core.config import settings


class OpenAIAdapter(BaseLLMAdapter):
    """
    Adapter for OpenAI API.
    Supports GPT-4, GPT-3.5, and other OpenAI models.
    """
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        num_predict: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text using OpenAI API.
        
        Args:
            prompt: The prompt to send to OpenAI
            temperature: Temperature setting
            num_predict: Maximum tokens to generate
            
        Returns:
            Generated text response
            
        Raises:
            ConnectionError: If connection to OpenAI fails
            ValueError: If API key is not configured
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY in environment.")
        
        if temperature is None:
            temperature = settings.LLM_TEMPERATURE
        
        effective_max_tokens = num_predict if num_predict is not None else settings.LLM_NUM_PREDICT
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": effective_max_tokens,
            "stream": True
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, stream=True, timeout=120)
            response.raise_for_status()
            
            # Parse streaming response
            full_output = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]  # Remove "data: " prefix
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                                delta = chunk_data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    full_output += content
                        except (json.JSONDecodeError, KeyError):
                            continue
            
            return full_output.strip()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error connecting to OpenAI: {e}")
        except Exception as e:
            raise RuntimeError(f"Error generating response from OpenAI: {e}")


__all__ = ["OpenAIAdapter"]

