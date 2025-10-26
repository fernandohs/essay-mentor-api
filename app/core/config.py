from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Essay Mentor API"
    APP_VERSION: str = "0.1.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "*"
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama3.1"
    OLLAMA_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields instead of raising an error

settings = Settings()
