"""
Prompt factory for generating LLM prompts for different endpoints.
This module now delegates to the refactored components in app/prompts/generators/
"""
from app.prompts.generators import (
    generate_prompt_for_ai_detection,
    generate_prompt_for_feedback,
    generate_prompt_for_guidance,
    generate_prompt_for_section_check
)

# Re-export for backward compatibility
__all__ = [
    "generate_prompt_for_ai_detection",
    "generate_prompt_for_feedback",
    "generate_prompt_for_guidance",
    "generate_prompt_for_section_check"
]