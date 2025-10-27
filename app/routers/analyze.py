from fastapi import APIRouter
from app.models import (
    AILikelihoodRequest, AILikelihoodResponse,
    FeedbackRequest, FeedbackResponse,
)
from app.services import analyze_ai_likelihood, generate_essay_feedback

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
    """
    Generate structured feedback on an essay based on evaluation criteria.
    
    **Default Criteria** (used if none specified):
    - originalidad (22pts): Creative approaches, metaphors, unexpected comparisons
    - profundidad (18pts): Deep vs superficial exploration
    - integralidad (16pts): Multi-dimensional, eclectic, plural perspective
    - conciliacion (14pts): Integration of agreement points to reduce polarization
    - refutacion (12pts): Recognition and response to counterarguments
    - evidencia (10pts): Verifiable, relevant data to support claims
    - logica (8pts): Strong, moderate relationship between claim and evidence
    
    **Total Points**: 100
    
    You can override by providing your own criteria list. Returns overview, per-criterion feedback.
    """
    return generate_essay_feedback(req.text, req.criteria, str(req.language))
