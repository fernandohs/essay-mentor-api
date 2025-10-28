"""
Usage tracking models for token consumption and cost monitoring.
"""
from datetime import datetime, date
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Provider(str, Enum):
    """LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"


class Function(str, Enum):
    """API functions that use LLM."""
    AI_DETECTION = "ai_detection"
    FEEDBACK = "feedback"
    GUIDANCE = "guidance"
    SECTION_CHECK = "section_check"


class UsageStatus(str, Enum):
    """Usage status."""
    SUCCESS = "success"
    FAILED = "failed"
    FALLBACK_USED = "fallback_used"


class TokenUsage(BaseModel):
    """Individual token usage record."""
    id: Optional[str] = Field(None, description="Unique identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    provider: Provider
    model: str = Field(description="Model name (e.g., gpt-4o, llama3.1)")
    function: Function
    tokens_input: int = Field(ge=0, description="Input tokens used")
    tokens_output: int = Field(ge=0, description="Output tokens generated")
    tokens_total: int = Field(ge=0, description="Total tokens used")
    cost_usd: float = Field(ge=0.0, description="Cost in USD")
    response_time_ms: int = Field(ge=0, description="Response time in milliseconds")
    status: UsageStatus
    error_message: Optional[str] = Field(None, description="Error message if failed")
    fallback_model: Optional[str] = Field(None, description="Fallback model used")
    retry_count: int = Field(default=0, ge=0, description="Number of retries attempted")
    
    def __init__(self, **data):
        if 'tokens_total' not in data:
            data['tokens_total'] = data.get('tokens_input', 0) + data.get('tokens_output', 0)
        super().__init__(**data)


class DailyUsage(BaseModel):
    """Daily aggregated usage."""
    date: date
    provider: Provider
    function: Function
    total_tokens: int = Field(ge=0)
    total_cost_usd: float = Field(ge=0.0)
    call_count: int = Field(ge=0)
    success_count: int = Field(ge=0)
    failure_count: int = Field(ge=0)
    fallback_count: int = Field(ge=0)
    avg_response_time_ms: float = Field(ge=0.0)
    avg_tokens_per_call: float = Field(ge=0.0)


class MonthlyUsage(BaseModel):
    """Monthly aggregated usage."""
    year: int
    month: int
    provider: Provider
    function: Function
    total_tokens: int = Field(ge=0)
    total_cost_usd: float = Field(ge=0.0)
    call_count: int = Field(ge=0)
    success_count: int = Field(ge=0)
    failure_count: int = Field(ge=0)
    fallback_count: int = Field(ge=0)
    avg_response_time_ms: float = Field(ge=0.0)
    avg_tokens_per_call: float = Field(ge=0.0)


class UsageReport(BaseModel):
    """Usage report response."""
    period: str = Field(description="Report period (daily, weekly, monthly)")
    start_date: date
    end_date: date
    total_cost_usd: float = Field(ge=0.0)
    total_tokens: int = Field(ge=0)
    total_calls: int = Field(ge=0)
    success_rate: float = Field(ge=0.0, le=100.0)
    fallback_rate: float = Field(ge=0.0, le=100.0)
    avg_response_time_ms: float = Field(ge=0.0)
    usage_by_function: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    usage_by_provider: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    cost_trend: Dict[str, float] = Field(default_factory=dict)


class FallbackConfig(BaseModel):
    """Fallback configuration for a function."""
    function: Function
    primary_model: str = Field(description="Primary model to use")
    fallback_chain: list[str] = Field(description="Ordered list of fallback models")
    max_retries_per_model: int = Field(default=3, ge=1, le=10)
    base_delay_seconds: float = Field(default=1.0, ge=0.1, le=10.0)
    max_delay_seconds: float = Field(default=10.0, ge=1.0, le=60.0)
    exponential_backoff: bool = Field(default=True)


class RetryConfig(BaseModel):
    """Retry configuration for a model."""
    model: str
    max_retries: int = Field(ge=1, le=10)
    base_delay: float = Field(ge=0.1, le=10.0)
    max_delay: float = Field(ge=1.0, le=60.0)
    exponential_backoff: bool = Field(default=True)
    retryable_errors: list[str] = Field(default_factory=list)


class ModelCost(BaseModel):
    """Cost configuration for a model."""
    provider: Provider
    model: str
    input_cost_per_1k: float = Field(ge=0.0, description="Cost per 1K input tokens")
    output_cost_per_1k: float = Field(ge=0.0, description="Cost per 1K output tokens")
    priority: str = Field(description="Priority level (high, medium, low)")
    max_tokens_per_minute: Optional[int] = Field(None, description="Rate limit")
    max_requests_per_minute: Optional[int] = Field(None, description="Rate limit")
