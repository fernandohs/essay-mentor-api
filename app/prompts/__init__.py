from .factory import (
    generate_prompt_for_ai_detection,
    generate_prompt_for_feedback,
    generate_prompt_for_guidance,
    generate_prompt_for_section_check,
)
from .generators.constants import EDUCATIONAL_RULE
from .criteria_data import ESSAY_RUBRIC_CRITERIA, DEFAULT_CRITERIA, TOTAL_POINTS

__all__ = [
    # Factory exports
    "generate_prompt_for_ai_detection",
    "generate_prompt_for_feedback",
    "generate_prompt_for_guidance",
    "generate_prompt_for_section_check",
    "EDUCATIONAL_RULE",
    # Data exports (only data, not models or utils)
    "ESSAY_RUBRIC_CRITERIA",
    "DEFAULT_CRITERIA",
    "TOTAL_POINTS",
]

