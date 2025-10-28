"""
Token usage tracking and logging system.
Simplified version using separated concerns.
"""
import time
from datetime import date
from typing import Optional, List

from app.models.usage import (
    TokenUsage, DailyUsage, UsageReport,
    Provider, Function, UsageStatus
)
from app.core.config import settings

from .database_manager import DatabaseManager
from .cost_calculator import CostCalculator
from .report_generator import ReportGenerator


class TokenTracker:
    """Tracks token usage and costs - simplified version."""
    
    def __init__(self, db_path: str = "usage_tracking.db"):
        """Initialize token tracker with SQLite database."""
        self.db_path = db_path
        self.db_manager = DatabaseManager(db_path)
        self.cost_calculator = CostCalculator()
        self.report_generator = ReportGenerator(db_path)
    
    def log_usage(
        self,
        provider: str,
        model: str,
        function: str,
        tokens_input: int,
        tokens_output: int,
        response_time_ms: int,
        status: str = "success",
        error_message: Optional[str] = None,
        fallback_model: Optional[str] = None,
        retry_count: int = 0
    ) -> str:
        """
        Log token usage to database.
        
        Returns:
            Usage ID for tracking
        """
        usage_id = f"{provider}_{model}_{function}_{int(time.time() * 1000)}"
        cost_usd = self.cost_calculator.calculate_cost(provider, model, tokens_input, tokens_output)
        
        usage = TokenUsage(
            id=usage_id,
            provider=Provider(provider),
            model=model,
            function=Function(function),
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            response_time_ms=response_time_ms,
            status=UsageStatus(status),
            error_message=error_message,
            fallback_model=fallback_model,
            retry_count=retry_count,
            cost_usd=cost_usd
        )
        
        self.db_manager.insert_usage(usage)
        return usage_id
    
    def get_daily_usage(self, target_date: date, function: Optional[str] = None) -> List[DailyUsage]:
        """Get daily usage aggregated data."""
        return self.report_generator.get_daily_usage(target_date, function)
    
    def get_usage_report(
        self,
        start_date: date,
        end_date: date,
        function: Optional[str] = None,
        provider: Optional[str] = None
    ) -> UsageReport:
        """Generate comprehensive usage report."""
        return self.report_generator.get_usage_report(start_date, end_date, function, provider)


# Global token tracker instance
_token_tracker = None

def get_token_tracker() -> TokenTracker:
    """Get or create global token tracker instance."""
    global _token_tracker
    if _token_tracker is None:
        _token_tracker = TokenTracker()
    return _token_tracker


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.
    Rough estimation: ~4 characters per token for English text.
    """
    return len(text) // 4


def track_token_usage(function_name: str):
    """
    Decorator to track token usage for a function.
    
    Usage:
        @track_token_usage("ai_detection")
        def analyze_ai_likelihood(text: str):
            # function implementation
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            tracker = get_token_tracker()
            
            try:
                # Estimate input tokens
                text_arg = args[0] if args else ""
                tokens_input = estimate_tokens(str(text_arg))
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Estimate output tokens
                tokens_output = estimate_tokens(str(result))
                response_time_ms = int((time.time() - start_time) * 1000)
                
                # Log successful usage
                tracker.log_usage(
                    provider="openai",  # Will be updated by actual adapter
                    model="unknown",    # Will be updated by actual adapter
                    function=function_name,
                    tokens_input=tokens_input,
                    tokens_output=tokens_output,
                    response_time_ms=response_time_ms,
                    status="success"
                )
                
                return result
                
            except Exception as e:
                response_time_ms = int((time.time() - start_time) * 1000)
                
                # Log failed usage
                tracker.log_usage(
                    provider="openai",
                    model="unknown",
                    function=function_name,
                    tokens_input=estimate_tokens(str(args[0]) if args else ""),
                    tokens_output=0,
                    response_time_ms=response_time_ms,
                    status="failed",
                    error_message=str(e)
                )
                
                raise
        
        return wrapper
    return decorator
