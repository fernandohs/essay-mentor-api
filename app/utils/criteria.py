"""
Criteria Utilities - Helper functions for working with criteria.

This module provides utility functions for validating, formatting, and managing
essay evaluation criteria.
"""

from typing import Dict, Any, cast
from app.models.criterion import CriterionDefinition
from app.prompts.criteria_data import ESSAY_RUBRIC_CRITERIA, DEFAULT_CRITERIA


def get_criteria_list() -> list[str]:
    """
    Get list of all criteria keys.
    
    Returns:
        List of criterion names
    """
    return DEFAULT_CRITERIA


def get_criterion_info(criterion: str) -> Dict[str, Any]:
    """
    Get information about a specific criterion.
    
    Args:
        criterion: The criterion name
        
    Returns:
        Dictionary with maxPoints and description
    """
    return ESSAY_RUBRIC_CRITERIA.get(criterion, {})


def validate_criterion(criterion_name: str, maxPoints: int, description: str) -> CriterionDefinition:
    """
    Validate and create a criterion definition.
    
    Args:
        criterion_name: Name of the criterion (for error reporting)
        maxPoints: Maximum points for this criterion
        description: Description of the criterion
        
    Returns:
        Validated CriterionDefinition
        
    Raises:
        ValueError: If the criterion structure is invalid
    """
    try:
        return CriterionDefinition(maxPoints=maxPoints, description=description)
    except Exception as e:
        raise ValueError(f"Invalid criterion '{criterion_name}': {str(e)}")


def add_criterion(criterion_name: str, maxPoints: int, description: str) -> None:
    """
    Add a new criterion to ESSAY_RUBRIC_CRITERIA with validation.
    
    Args:
        criterion_name: Name/key for the criterion
        maxPoints: Maximum points for this criterion
        description: Description of the criterion
        
    Raises:
        ValueError: If the criterion structure is invalid or name already exists
    """
    if criterion_name in ESSAY_RUBRIC_CRITERIA:
        raise ValueError(f"Criterion '{criterion_name}' already exists")
    
    # Validate the criterion structure
    validate_criterion(criterion_name, maxPoints, description)
    
    # Add to dictionary (note: this modifies the shared dictionary)
    ESSAY_RUBRIC_CRITERIA[criterion_name] = {
        "maxPoints": maxPoints,
        "description": description
    }


def validate_all_criteria() -> bool:
    """
    Validate that all criteria in ESSAY_RUBRIC_CRITERIA follow the correct structure.
    
    Returns:
        True if all criteria are valid
        
    Raises:
        ValueError: If any criterion has an invalid structure
    """
    for criterion_name, criterion_data in ESSAY_RUBRIC_CRITERIA.items():
        try:
            # Type cast to ensure proper typing for Pesyantic model
            data: Dict[str, Any] = {
                "maxPoints": criterion_data.get("maxPoints"),
                "description": criterion_data.get("description")
            }
            CriterionDefinition(**cast(Dict[str, Any], data))
        except Exception as e:
            raise ValueError(f"Invalid criterion '{criterion_name}': {str(e)}")
    return True


def get_default_criteria_description() -> str:
    """
    Generate a formatted description of default criteria for use in field descriptions.
    
    Returns:
        Formatted string listing all criteria with their point values
    """
    descriptions = []
    for criterion in DEFAULT_CRITERIA:
        info = ESSAY_RUBRIC_CRITERIA[criterion]
        descriptions.append(f"{criterion} ({info['maxPoints']}pts)")
    return ", ".join(descriptions)


def get_default_criteria_summary() -> str:
    """
    Generate a summary of all default criteria with descriptions for API documentation.
    
    Returns:
        Formatted string with criteria details suitable for endpoint documentation
    """
    summary_lines = []
    for criterion in DEFAULT_CRITERIA:
        info = ESSAY_RUBRIC_CRITERIA[criterion]
        # Extract short description without the question mark
        desc = str(info.get('description', ''))
        short_desc = desc.replace("¿", "").replace("?", "")
        summary_lines.append(f"- {criterion} ({info['maxPoints']}pts): {short_desc}")
    return "\n".join(summary_lines)


# Validate all criteria at module load time
try:
    validate_all_criteria()
except ValueError as e:
    raise RuntimeError(f"Invalid criteria configuration: {str(e)}") from e

