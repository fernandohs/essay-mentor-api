"""
Essay Rubric Criteria based on Extended Toulmin Model.

This module defines the evaluation criteria for essay scoring with their
respective weightings and descriptions.
"""

from typing import Any, Literal


# Achievement levels in Spanish
AchievementLevel = Literal[
    "Excepcional",
    "Muy Bien",
    "Bien",
    "Regular",
    "Insuficiente"
]

# Essay Rubric Criteria (Extended Toulmin Model)
ESSAY_RUBRIC_CRITERIA = {
    "originalidad": {
        "maxPoints": 22,
        "description": "¿Se usan enfoques creativos, metáforas o comparaciones inesperadas?"
    },
    "profundidad": {
        "maxPoints": 18,
        "description": "¿La respuesta es superficial o explora el tema de manera profunda?"
    },
    "integralidad": {
        "maxPoints": 16,
        "description": "¿Aborda el tema desde una perspectiva multi dimensional, eclectica, plural, con sus elementos centrales?"
    },
    "conciliacion": {
        "maxPoints": 14,
        "description": "¿El argumento integra puntos de acuerdo para reducir polarización?"
    },
    "refutacion": {
        "maxPoints": 12,
        "description": "¿Se reconocen y responden eficazmente los contraargumentos?"
    },
    "evidencia": {
        "maxPoints": 10,
        "description": "¿Los datos son verificables y relevantes para respaldar la afirmación?"
    },
    "logica": {
        "maxPoints": 8,
        "description": "¿Existe una relación sólida y moderada (certeza) entre afirmacion y evidencia?"
    }
}

# Default criteria list (Spanish)
DEFAULT_CRITERIA = list(ESSAY_RUBRIC_CRITERIA.keys())

# Total possible points (calculated sum of all max points)
TOTAL_POINTS = 22 + 18 + 16 + 14 + 12 + 10 + 8  # Sum of all maxPoints


def get_criteria_list() -> list[str]:
    """
    Get list of all criteria keys.
    
    Returns:
        List of criterion names
    """
    return DEFAULT_CRITERIA


def get_criterion_info(criterion: str) -> Any:
    """
    Get information about a specific criterion.
    
    Args:
        criterion: The criterion name
        
    Returns:
        Dictionary with maxPoints and description
    """
    return ESSAY_RUBRIC_CRITERIA.get(criterion, {})

