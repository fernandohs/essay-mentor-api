from fastapi import APIRouter, HTTPException
from app.models import (
    GuideRequest, GuidanceResponse,
    SectionCheckRequest, SectionAdviceResponse,
)
from app.models.types import Section
from app.services import get_section_guidance, check_section_quality

router = APIRouter(prefix="/guide", tags=["guide"])

@router.post("/", response_model=GuidanceResponse)
def guide(req: GuideRequest):
    """
    Get guidance for writing a specific essay section.
    
    Returns purpose, steps, checklist, examples, and tips for the requested section.
    
    Valid sections: claim, reasoning, evidence, backing, reservation, rebuttal
    """
    # Validate section (Pydantic already validates, but add explicit check for clarity)
    valid_sections = {"claim", "reasoning", "evidence", "backing", "reservation", "rebuttal"}
    if req.section not in valid_sections:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid section '{req.section}'. Valid sections are: {', '.join(valid_sections)}"
        )
    
    return get_section_guidance(req.section, str(req.language))

@router.post("/check-section", response_model=SectionAdviceResponse)
def check_section(req: SectionCheckRequest):
    """
    Analyze a student's essay section and provide constructive feedback.
    
    Returns strengths, issues, guiding questions, and revision strategies.
    
    Valid sections: claim, reasoning, evidence, backing, reservation, rebuttal
    """
    # Validate section
    valid_sections = {"claim", "reasoning", "evidence", "backing", "reservation", "rebuttal"}
    if req.section not in valid_sections:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid section '{req.section}'. Valid sections are: {', '.join(valid_sections)}"
        )
    
    return check_section_quality(req.section, req.text, str(req.language))
