"""
Cost calculator for token usage tracking.
Handles cost calculations based on provider and model pricing.
"""
from typing import Dict


class CostCalculator:
    """Calculates costs for different LLM providers and models."""
    
    # OpenAI pricing (as of 2024) - per 1K tokens
    OPENAI_PRICING = {
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    
    def calculate_cost(self, provider: str, model: str, tokens_input: int, tokens_output: int) -> float:
        """
        Calculate cost based on provider and model pricing.
        
        Args:
            provider: LLM provider (openai, ollama)
            model: Model name (e.g., gpt-4o, llama3.1)
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens
            
        Returns:
            Cost in USD
        """
        if provider == "openai" and model in self.OPENAI_PRICING:
            pricing = self.OPENAI_PRICING[model]
            input_cost = (tokens_input / 1000) * pricing["input"]
            output_cost = (tokens_output / 1000) * pricing["output"]
            return input_cost + output_cost
        
        # Ollama and other providers are free
        return 0.0
    
    def get_pricing_info(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Get pricing information for all supported models.
        
        Returns:
            Dictionary with pricing information by provider
        """
        return {
            "openai": self.OPENAI_PRICING,
            "ollama": {"free": {"input": 0.0, "output": 0.0}}
        }
