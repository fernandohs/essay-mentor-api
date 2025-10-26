from fastapi import APIRouter
from app.models import (
    AILikelihoodRequest, AILikelihoodResponse,
    FeedbackRequest, FeedbackResponse,
)

router = APIRouter(prefix="/analyze", tags=["analyze"])

@router.post("/ai-likelihood", response_model=AILikelihoodResponse)
def ai_likelihood(req: AILikelihoodRequest):
    # TODO: Implement AI likelihood detection
    return AILikelihoodResponse(
        score=0,
        rationale="(placeholder) Not implemented yet",
        caveats=["Dummy response for Phase A."]
    )

@router.post("/feedback", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest):
    # TODO: Implement feedback generation
    return FeedbackResponse(
        overview="(placeholder) Not implemented yet",
        per_criterion=[],
        prioritized_actions=[]
    )
