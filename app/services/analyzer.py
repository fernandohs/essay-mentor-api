"""
Analysis service for essay evaluation and AI detection.

This module provides business logic for analyzing student essays,
including AI likelihood detection and structured feedback generation.
"""

from typing import List, Optional
from fastapi import HTTPException

from app.adapters.llm_adapter import get_llm_adapter
from app.prompts.factory import (
    generate_prompt_for_ai_detection,
    generate_prompt_for_feedback
)
from app.utils.json_parse import safe_json_parse
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
        
        # 2. Call LLM with focused temperature for precision
        llm_adapter = get_llm_adapter()
        llm_response = llm_adapter.generate(
            prompt, 
            temperature=settings.LLM_TEMP_FOCUSED
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
        
        # 2. Call LLM with balanced temperature and more tokens for detailed feedback
        llm_adapter = get_llm_adapter()
        llm_response = llm_adapter.generate(
            prompt, 
            temperature=settings.LLM_TEMP_BALANCED,
            num_predict=1024  # Need more tokens for structured feedback on long essays
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

