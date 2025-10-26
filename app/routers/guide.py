from fastapi import APIRouter
from app.models import (
    GuideRequest, GuidanceResponse,
    SectionCheckRequest, SectionAdviceResponse,
)

router = APIRouter(prefix="/guide", tags=["guide"])

@router.post("/", response_model=GuidanceResponse)
def guide(req: GuideRequest):
    return GuidanceResponse(
        section=req.section,
        purpose="(placeholder)",
        steps=[],
        checklist=[],
        examples_do=[],
        examples_dont=[],
        tips=[],
    )

@router.post("/check-section", response_model=SectionAdviceResponse)
def check_section(req: SectionCheckRequest):
    return SectionAdviceResponse(
        section=req.section,
        strengths=[],
        issues=[],
        questions_to_refine=[],
        revision_strategies=[],
    )
