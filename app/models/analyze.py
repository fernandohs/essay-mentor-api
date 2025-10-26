from pydantic import BaseModel, Field
from typing import Annotated, List, Optional
from .types import MAX_LEN, Rating

#Requests
class AILikelihoodRequest(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=MAX_LEN, strip_whitespace=True)]

class FeedbackRequest(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=MAX_LEN, strip_whitespace=True)]
    criteria: Optional[List[str]] = None

#Responses
class AILikelihoodResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    rationale: str
    caveats: List[str]

class CriterionFeedback(BaseModel):
    criterion: str
    rating: Rating
    comments: str
    suggestions: List[str]

class FeedbackResponse(BaseModel):
    overview: str
    per_criterion: List[CriterionFeedback]
    prioritized_actions: List[str]
