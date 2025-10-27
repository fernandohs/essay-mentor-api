from pydantic import BaseModel, Field
from typing import Annotated, List, Optional, Literal
from .types import MAX_LEN, Rating
from .guide import Language
from app.core.config import settings as app_settings

#Requests
class AILikelihoodRequest(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=MAX_LEN, strip_whitespace=True)]
    language: Language = Field(default=app_settings.DEFAULT_LANGUAGE, description="Language for the response (en=English, es=Spanish)")

class FeedbackRequest(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=MAX_LEN, strip_whitespace=True)]
    criteria: Optional[List[str]] = Field(
        default=None,
        description="Optional list of criteria to evaluate. If not provided, uses default criteria: originalidad (22pts), profundidad (18pts), integralidad (16pts), conciliacion (14pts), refutacion (12pts), evidencia (10pts), logica (8pts)"
    )
    language: Language = Field(default=app_settings.DEFAULT_LANGUAGE, description="Language for the feedback (en=English, es=Spanish)")

#Responses
class AILikelihoodResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    rationale: str
    caveats: List[str]

class CriterionFeedback(BaseModel):
    etiqueta: str = Field(description="One-word lowercase label for the criterion (e.g., 'originalidad')")
    criterio: str = Field(description="Full description of the criterion being evaluated")
    valorMaximo: int = Field(description="Maximum possible points for this criterion")
    logro: str = Field(description="Achievement level: Excepcional, Muy Bien, Bien, Regular, Insuficiente")
    evaluacion: str = Field(description="Qualitative assessment of student performance on this criterion")
    puntuacion: int = Field(ge=0, description="Numerical score obtained (between 0 and valorMaximo)")

class FeedbackResponse(BaseModel):
    overview: str = Field(description="Overall assessment of the essay")
    per_criterion: List[CriterionFeedback] = Field(description="Detailed feedback for each criterion")
