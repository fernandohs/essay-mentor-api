"""
Guidance service for essay section guidance and checking.

This module provides business logic for guiding students on essay structure
and providing specific feedback on essay sections based on the Toulmin model.
"""

from typing import Optional
from fastapi import HTTPException

from app.adapters.llm_adapter import get_llm_adapter
from app.prompts.factory import (
    generate_prompt_for_guidance,
    generate_prompt_for_section_check
)
from app.utils.json_parse import safe_json_parse
from app.core.config import settings
from app.models.types import Section
from app.models.guide import GuidanceResponse, SectionAdviceResponse


def get_section_guidance(section: Section, language: str = "en") -> GuidanceResponse:  # type: ignore
    """
    Get general guidance for writing a specific essay section.
    
    Args:
        section: The essay section (claim, reasoning, evidence, etc.)
        language: Language for the response (en=English, es=Spanish)
        
    Returns:
        GuidanceResponse with purpose, steps, checklist, examples, and tips
        
    Raises:
        HTTPException: If guidance generation fails
    """
    # Use default language from config if not provided
    if language is None:
        language = settings.DEFAULT_LANGUAGE
    
    try:
        # 1. Generate prompt using factory
        prompt = generate_prompt_for_guidance(section, language)
        
        # 2. Call LLM with creative temperature and more tokens for guidance responses
        llm_adapter = get_llm_adapter()
        llm_response = llm_adapter.generate(
            prompt, 
            temperature=settings.LLM_TEMP_CREATIVE,
            num_predict=1024  # Need more tokens for structured guidance output
        )
        
        # 3. Parse JSON response
        parsed_data = safe_json_parse(llm_response)
        
        # 4. Check if parsed_data is a dict
        if not isinstance(parsed_data, dict):
            raise ValueError(f"Expected dict but got {type(parsed_data).__name__}")
        
        # 5. Validate with Pydantic model
        return GuidanceResponse(**parsed_data)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to parse LLM response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating guidance: {str(e)}"
        )


def check_section_quality(section: Section, text: str, language: Optional[str] = None) -> SectionAdviceResponse:  # type: ignore
    """
    Analyze and provide feedback on a student's essay section.
    
    Args:
        section: The essay section being checked
        text: The student's text for this section
        language: Language for the feedback (en=English, es=Spanish)
        
    Returns:
        SectionAdviceResponse with strengths, issues, questions, and strategies
        
    Raises:
        HTTPException: If section checking fails
    """
    # Use default language from config if not provided
    if language is None:
        language = settings.DEFAULT_LANGUAGE
    
    try:
        # 1. Generate prompt using factory
        prompt = generate_prompt_for_section_check(section, text, language)
        
        # 2. Call LLM with creative temperature for feedback and more tokens
        llm_adapter = get_llm_adapter()
        llm_response = llm_adapter.generate(
            prompt, 
            temperature=settings.LLM_TEMP_CREATIVE,
            num_predict=1024  # Need more tokens for structured feedback
        )
        
        # 3. Parse JSON response
        parsed_data = safe_json_parse(llm_response)
        
        # 4. Debug: Check if parsed_data is a dict
        if not isinstance(parsed_data, dict):
            raise ValueError(f"Expected dict but got {type(parsed_data).__name__}")
        
        # 5. Validate with Pydantic model
        return SectionAdviceResponse(**parsed_data)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to parse LLM response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error checking section: {str(e)}"
        )

