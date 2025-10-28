"""
Criteria Data - Default essay evaluation criteria definitions.

This module contains the default rubric criteria and their configurations.
All criteria follow the Extended Toulmin Model structure.
"""

from typing import Dict, Any


# Essay Rubric Criteria (Extended Toulmin Model)
# Each criterion must have maxPoints and description
ESSAY_RUBRIC_CRITERIA: Dict[str, Dict[str, Any]] = {
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
TOTAL_POINTS = sum(
    criterion["maxPoints"] 
    for criterion in ESSAY_RUBRIC_CRITERIA.values()
)
