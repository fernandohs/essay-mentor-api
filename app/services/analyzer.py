"""
Analysis service for essay evaluation and AI detection.

This module provides business logic for analyzing student essays,
including AI likelihood detection and structured feedback generation.
"""

from typing import List, Optional, Dict, Any
from fastapi import HTTPException

from app.adapters.llm_adapter import get_llm_adapter
from app.prompts.factory import (
    generate_prompt_for_ai_detection,
    generate_prompt_for_feedback
)
from app.utils.json_parse import safe_json_parse
from app.utils import get_default_criteria_summary
from app.prompts.criteria_data import TOTAL_POINTS
from app.core.config import settings
from app.models.analyze import AILikelihoodResponse, FeedbackResponse


def analyze_ai_likelihood(text: str, language: Optional[str] = None) -> AILikelihoodResponse:  # type: ignore
    """
    Analyze text to estimate likelihood that it was AI-generated.
    
    Args:
        text: Text to analyze
        language: Language for the response (en=English, es=Spanish)
        
    Returns:
        AILikelihoodResponse with score, rationale, and caveats
        
    Raises:
        HTTPException: If analysis fails
    """
    # Use default language from config if not provided
    if language is None:
        language = settings.DEFAULT_LANGUAGE
    
    try:
        # 1. Generate prompt using factory
        prompt = generate_prompt_for_ai_detection(text, language)
        
        # 2. Get specific model for AI detection function
        provider, model = settings.get_model_for_function("ai_detection")
        llm_adapter = get_llm_adapter(provider=provider, model=model)
        
        # 3. Call LLM with focused temperature for precision
        llm_response = llm_adapter.generate(
            prompt, 
            temperature=settings.LLM_TEMP_FOCUSED,
            function="ai_detection",
            use_fallback=True
        )
        
        # 3. Parse JSON response
        parsed_data = safe_json_parse(llm_response)
        
        # 4. Debug: Check if parsed_data is a dict
        if not isinstance(parsed_data, dict):
            raise ValueError(f"Expected dict but got {type(parsed_data).__name__}")
        
        # 5. Validate with Pydantic model
        return AILikelihoodResponse(**parsed_data)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to parse LLM response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error analyzing AI likelihood: {str(e)}"
        )


def generate_essay_feedback(text: str, criteria: Optional[List[str]] = None, language: Optional[str] = None) -> FeedbackResponse:  # type: ignore
    """
    Generate structured feedback for an essay based on evaluation criteria.
    
    Args:
        text: Essay text to evaluate
        criteria: Optional list of criteria to evaluate. If None, uses defaults.
        language: Language for the response (en=English, es=Spanish)
        
    Returns:
        FeedbackResponse with overview, per-criterion feedback, and actions
        
    Raises:
        HTTPException: If feedback generation fails
    """
    # Use default language from config if not provided
    if language is None:
        language = settings.DEFAULT_LANGUAGE
    
    try:
        # 1. Generate prompt using factory
        prompt = generate_prompt_for_feedback(text, criteria, language)
        
        # 2. Get specific model for feedback function
        provider, model = settings.get_model_for_function("feedback")
        llm_adapter = get_llm_adapter(provider=provider, model=model)
        
        # 3. Call LLM with balanced temperature and extended tokens for detailed feedback
        llm_response = llm_adapter.generate(
            prompt, 
            temperature=settings.LLM_TEMP_BALANCED,
            num_predict=settings.LLM_TOKENS_EXTENDED,
            function="feedback",
            use_fallback=True
        )
        
        # 3. Parse JSON response
        parsed_data = safe_json_parse(llm_response)
        
        # 4. Debug: Check if parsed_data is a dict
        if not isinstance(parsed_data, dict):
            raise ValueError(f"Expected dict but got {type(parsed_data).__name__}")
        
        # 5. Validate with Pydantic model
        return FeedbackResponse(**parsed_data)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to parse LLM response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating feedback: {str(e)}"
        )


def get_criteria_metadata() -> Dict[str, Any]:
    """
    Get criteria metadata for API documentation.
    
    Returns:
        Dictionary containing criteria summary and total points
    """
    return {
        "summary": get_default_criteria_summary(),
        "total_points": TOTAL_POINTS
    }

