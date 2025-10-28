"""
Criterion Models - Pydantic models and type definitions for essay evaluation criteria.

This module defines the structure and types used for rubric criteria,
ensuring type safety and validation.
"""

from typing import Literal
from pydantic import BaseModel, Field


# Achievement levels in Spanish (used in feedback responses)
AchievementLevel = Literal[
    "Excepcional",
    "Muy Bien",
    "Bien",
    "Regular",
    "Insuficiente"
]


class CriterionDefinition(BaseModel):
    """
    Model defining the structure of an essay evaluation criterion.
    
    All criteria must have:
    - maxPoints: Maximum points that can be awarded (must be > 0)
    - description: Question or description of what is being evaluated
    
    Example:
        ```python
        criterion = CriterionDefinition(
            maxPoints=22,
            description="¿Se usan enfoques creativos, metáforas o comparaciones inesperadas?"
        )
        ```
    """
    maxPoints: int = Field(
        gt=0,
        description="Maximum points that can be awarded for this criterion"
    )
    description: str = Field(
        min_length=1,
        description="Question or description of what is being evaluated"
    )

