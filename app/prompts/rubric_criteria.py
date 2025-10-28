"""
Rubric Criteria - Backward compatibility wrapper.

This module is deprecated and kept for backward compatibility.
All functionality has been modularized following project structure:
- app/models/criterion.py (Pydantic models and types)
- app/prompts/criteria_data.py (Data definitions)
- app/utils/criteria.py (Utility functions)

Please update imports to use the new modules directly.
"""

from app.models.criterion import CriterionDefinition, AchievementLevel
from .criteria_data import ESSAY_RUBRIC_CRITERIA, DEFAULT_CRITERIA, TOTAL_POINTS
from app.utils.criteria import (
    get_criteria_list,
    get_criterion_info,
    validate_criterion,
    add_criterion,
    validate_all_criteria,
    get_default_criteria_description,
    get_default_criteria_summary,
)


__all__ = [
    "AchievementLevel",
    "CriterionDefinition",
    "ESSAY_RUBRIC_CRITERIA",
    "DEFAULT_CRITERIA",
    "TOTAL_POINTS",
    "get_criteria_list",
    "get_criterion_info",
    "validate_criterion",
    "add_criterion",
    "validate_all_criteria",
    "get_default_criteria_description",
    "get_default_criteria_summary",
]
