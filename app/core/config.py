from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Essay Mentor API"
    APP_VERSION: str = "0.1.0"
    HOST: str = "0.0.0.0"  # nosec B104 - API needs to be accessible from other interfaces
    PORT: int = 8000
    CORS_ORIGINS: str = "*"
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama3.1"
    OLLAMA_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # LLM Generation Parameters - Default settings
    LLM_TEMPERATURE: float = 0.3  # Default temperature for general use cases
    LLM_NUM_PREDICT: int = 512    # Maximum number of tokens to generate (increased for complete responses)
    
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

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields instead of raising an error

settings = Settings()
