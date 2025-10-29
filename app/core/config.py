from pydantic_settings import BaseSettings
from typing import Tuple

class Settings(BaseSettings):
    APP_NAME: str = "Essay Mentor API"
    APP_VERSION: str = "0.1.0"
    HOST: str = "0.0.0.0"  # nosec B104 - API needs to be accessible from other interfaces
    PORT: int = 8000
    CORS_ORIGINS: str = "*"
    # Default LLM Provider and Model
    # Supported providers: ollama, openai, qwen2.5 (qwen2.5 runs through Ollama)
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama3.1"
    
    # Ollama Configuration
    OLLAMA_URL: str = "http://localhost:11434"
    
    # OpenAI API Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # Model Selection by Function - Use specific models for different tasks to optimize costs
    # Format: "provider:model" or just "model" (will use default provider)
    LLM_MODEL_AI_DETECTION: str = ""      # Empty = use LLM_MODEL (AI likelihood detection - high precision needed)
    LLM_MODEL_FEEDBACK: str = ""           # Empty = use LLM_MODEL (Essay feedback - detailed analysis needed)
    LLM_MODEL_GUIDANCE: str = ""           # Empty = use LLM_MODEL (Section guidance - can use cheaper models)
    LLM_MODEL_SECTION_CHECK: str = ""      # Empty = use LLM_MODEL (Section checking - moderate complexity)
    
    # LLM Generation Parameters - Default settings
    LLM_TEMPERATURE: float = 0.3  # Default temperature for general use cases
    LLM_NUM_PREDICT: int = 4096    # Maximum number of tokens to generate (increased for complete responses)
    
    # LLM Temperature Presets (creativity levels)
    # Use these semantic constants to control AI creativity vs precision
    LLM_TEMP_FOCUSED: float = 0.1        # Maximum precision, minimal randomness (AI detection, factual analysis)
    LLM_TEMP_BALANCED: float = 0.3       # Balanced precision with some variability (feedback, structured analysis)
    LLM_TEMP_CREATIVE: float = 0.6       # Balanced creativity for guidance and suggestions (essay improvement tips)
    LLM_TEMP_HIGHLY_CREATIVE: float = 0.9  # High creativity, maximum randomness (brainstorming, idea generation)
    
    # LLM Token Limits (use case specific)
    # Use these semantic constants for consistent token limits across the application
    LLM_TOKENS_SHORT: int = 256      # Short responses (status messages, brief confirmations)
    LLM_TOKENS_DEFAULT: int = 512    # Default for general responses (AI likelihood detection)
    LLM_TOKENS_STRUCTURED: int = 1024 # Structured data responses (guidance, section advice)
    LLM_TOKENS_EXTENDED: int = 2048   # Extended responses (essay feedback with multiple criteria)
    LLM_TOKENS_LONG: int = 4096      # Long-form content (comprehensive analysis, detailed reports)
    
    # Language Settings
    DEFAULT_LANGUAGE: str = "es"  # Default language for LLM responses (en=English, es=Spanish)
    
    # Fallback Configuration - OpenAI models only
    LLM_FALLBACK_AI_DETECTION: str = "gpt-4o,gpt-4o-mini,gpt-3.5-turbo"
    LLM_FALLBACK_FEEDBACK: str = "gpt-4o,gpt-4o-mini,gpt-3.5-turbo"
    LLM_FALLBACK_GUIDANCE: str = "gpt-4o-mini,gpt-3.5-turbo"
    LLM_FALLBACK_SECTION_CHECK: str = "gpt-4o-mini,gpt-3.5-turbo"
    
    # Retry Configuration
    GPT4O_MAX_RETRIES: int = 2
    GPT4O_MINI_MAX_RETRIES: int = 3
    GPT35_TURBO_MAX_RETRIES: int = 5
    
    # Circuit Breaker Configuration
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 300  # 5 minutes
    
    # Token Tracking Configuration
    ENABLE_TOKEN_TRACKING: bool = True
    TOKEN_TRACKING_DB_PATH: str = "usage_tracking.db"
    
    def get_model_for_function(self, function_name: str) -> Tuple[str, str]:
        """
        Get the appropriate model configuration for a specific function.
        
        Args:
            function_name: Name of the function (ai_detection, feedback, guidance, section_check)
            
        Returns:
            Tuple of (provider, model) to use for this function
            
        Examples:
            >>> settings.get_model_for_function("ai_detection")
            ('ollama', 'llama3.1')  # Uses default
            
            >>> settings.LLM_MODEL_FEEDBACK = "openai:gpt-4o-mini"
            >>> settings.get_model_for_function("feedback")
            ('openai', 'gpt-4o-mini')  # Uses specific model
        """
        # Map function names to their specific model settings
        model_mapping = {
            "ai_detection": self.LLM_MODEL_AI_DETECTION or self.LLM_MODEL,
            "feedback": self.LLM_MODEL_FEEDBACK or self.LLM_MODEL,
            "guidance": self.LLM_MODEL_GUIDANCE or self.LLM_MODEL,
            "section_check": self.LLM_MODEL_SECTION_CHECK or self.LLM_MODEL,
        }
        
        model = model_mapping.get(function_name, self.LLM_MODEL)
        
        # Parse model string to extract provider and model name
        # Format can be: "provider:model" or just "model"
        # Special case: if model contains ":" but starts with a known model name, treat as model only
        known_model_prefixes = ["qwen2.5", "llama3", "mistral", "phi3", "deepseek"]
        
        if ":" in model:
            # Check if it's a known model prefix (not a provider)
            model_prefix = model.split(":")[0]
            if model_prefix in known_model_prefixes:
                # This is a model name with version/tag, not provider:model
                return self.LLM_PROVIDER, model
            else:
                # This is provider:model format
                provider, actual_model = model.split(":", 1)
                return provider, actual_model
        else:
            return self.LLM_PROVIDER, model

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields instead of raising an error

settings = Settings()
