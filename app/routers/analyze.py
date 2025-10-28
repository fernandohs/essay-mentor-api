from fastapi import APIRouter
from app.models import (
    AILikelihoodRequest, AILikelihoodResponse,
    FeedbackRequest, FeedbackResponse,
)
from app.services import analyze_ai_likelihood, generate_essay_feedback, get_criteria_metadata

# Get criteria metadata for documentation at module level
_criteria_metadata = get_criteria_metadata()
CRITERIA_DOC = _criteria_metadata["summary"]
TOTAL_POINTS = _criteria_metadata["total_points"]

router = APIRouter(prefix="/analyze", tags=["analyze"])

@router.post("/ai-likelihood", response_model=AILikelihoodResponse)
def ai_likelihood(req: AILikelihoodRequest):
    """
    Estimate the likelihood that the provided text was AI-generated.
    
    Returns a score from 0-100 along with rationale and caveats.
    """
    return analyze_ai_likelihood(req.text, str(req.language))

@router.post("/feedback", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest):
    f"""
    Generate structured feedback on an essay based on evaluation criteria.
    
    **Default Criteria** (used if none specified):
    {CRITERIA_DOC}
    
    **Total Points**: {TOTAL_POINTS}
    
    You can override by providing your own criteria list. Returns overview, per-criterion feedback.
    """
    return generate_essay_feedback(req.text, req.criteria, str(req.language))
