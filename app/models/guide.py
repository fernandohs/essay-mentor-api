from typing import List, Dict, Annotated, Optional, Literal
from pydantic import BaseModel, Field

from app.models.types import MAX_LEN, Section
from app.core.config import settings as app_settings

# Language types
Language = Literal["en", "es"]

# Requests
class GuideRequest(BaseModel):
    section: Section
    language: Language = Field(default=app_settings.DEFAULT_LANGUAGE, description="Language for the response (en=English, es=Spanish)")

class SectionCheckRequest(BaseModel):
    section: Section
    text: Annotated[str, Field(min_length=1, max_length=MAX_LEN, strip_whitespace=True)]
    language: Language = Field(default=app_settings.DEFAULT_LANGUAGE, description="Language for the feedback (en=English, es=Spanish)")
    
# Responses
class GuidanceResponse(BaseModel):
    section: Section
    purpose: str
    steps: List[str]
    checklist: List[str]
    examples_do: List[str]
    examples_dont: List[str]
    tips: List[str]

class SectionAdviceResponse(BaseModel):
    section: Section
    strengths: List[str]
    issues: List[str]
    questions_to_refine: List[str]
    revision_strategies: List[str]