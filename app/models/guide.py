from typing import List, Dict, Annotated
from pydantic import BaseModel, Field

from app.models.types import MAX_LEN, Section

# Requests
class GuideRequest(BaseModel):
    section: Section

class SectionCheckRequest(BaseModel):
    section: Section
    text: Annotated[str, Field(min_length=1, max_length=MAX_LEN, strip_whitespace=True)]
    
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