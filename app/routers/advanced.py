"""
Advanced analysis endpoints using LangChain features.
Provides multi-step analysis, chains, and advanced LLM workflows.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.services.advanced_analyzer import get_advanced_analyzer

router = APIRouter(prefix="/advanced", tags=["Advanced Analysis"])


class AdvancedAnalysisRequest(BaseModel):
    """Request model for advanced analysis using Extended Toulmin Model."""
    text: str = Field(..., description="Essay text to analyze", max_length=8000)
    criteria: Optional[List[str]] = Field(default=None, description="Specific criteria to evaluate (uses all if None)")
    language: Optional[str] = Field(default="es", description="Language for the response (en=English, es=Spanish)")


class AdvancedAnalysisResponse(BaseModel):
    """Response model for advanced analysis using Extended Toulmin Model criteria."""
    overview: str = Field(..., description="Overall essay assessment")
    per_criterion: List['CriterionResult'] = Field(..., description="Evaluation for each criterion")
    total_score: int = Field(..., description="Total score across all criteria")
    max_possible_score: int = Field(..., description="Maximum possible score")
    percentage: float = Field(..., description="Percentage score (0-100)")


class AdvancedFeedbackRequest(BaseModel):
    """Request model for advanced feedback analysis."""
    text: str = Field(..., description="Essay text to analyze", max_length=8000)
    criteria: Optional[List[str]] = Field(default=None, description="Specific criteria to evaluate (uses defaults if None)")
    language: Optional[str] = Field(default="es", description="Language for the response (en=English, es=Spanish)")


class CriterionResult(BaseModel):
    """Individual criterion evaluation result."""
    etiqueta: str = Field(..., description="Criterion name")
    criterio: str = Field(..., description="Criterion description")
    valorMaximo: int = Field(..., description="Maximum possible points")
    logro: str = Field(..., description="Achievement level")
    evaluacion: str = Field(..., description="Qualitative evaluation")
    puntuacion: int = Field(..., description="Numerical score")


class AdvancedFeedbackResponse(BaseModel):
    """Response model for advanced feedback analysis."""
    overview: str = Field(..., description="Overall essay assessment")
    overall_strengths: List[str] = Field(..., description="Overall strengths")
    overall_weaknesses: List[str] = Field(..., description="Overall weaknesses")
    per_criterion: List[CriterionResult] = Field(..., description="Individual criterion evaluations")
    total_score: int = Field(..., description="Total score achieved")
    max_possible: int = Field(..., description="Maximum possible points")
    percentage: float = Field(..., description="Percentage of achievement")
    grade_level: str = Field(..., description="Overall grade level")
    key_recommendations: List[str] = Field(..., description="Key recommendations for improvement")


@router.post("/analyze-chain", response_model=AdvancedAnalysisResponse)
def analyze_with_chain(req: AdvancedAnalysisRequest):
    """
    Analyze essay using LangChain with Extended Toulmin Model criteria.
    
    This endpoint evaluates essays using the SAME criteria as /analyze/feedback:
    - **originalidad** (22 points): Creative approaches, metaphors
    - **profundidad** (18 points): Deep vs superficial analysis
    - **integralidad** (16 points): Multidimensional perspective
    - **conciliacion** (14 points): Integration of agreement points
    - **refutacion** (12 points): Counter-argument recognition
    - **evidencia** (10 points): Verifiable, relevant data
    - **logica** (8 points): Solid connection between claim and evidence
    
    **Total: 100 points**
    
    **Example request:**
    ```json
    {
        "text": "Essay text here...",
        "criteria": ["originalidad", "profundidad", "evidencia"],
        "language": "es"
    }
    ```
    
    **Example response:**
    ```json
    {
        "overview": "Overall assessment...",
        "per_criterion": [
            {
                "etiqueta": "originalidad",
                "criterio": "¿Se usan enfoques creativos...?",
                "valorMaximo": 22,
                "logro": "El ensayo demuestra...",
                "evaluacion": "bueno",
                "puntuacion": 18
            }
        ],
        "total_score": 75,
        "max_possible_score": 100,
        "percentage": 75.0
    }
    ```
    """
    try:
        analyzer = get_advanced_analyzer()
        result = analyzer.analyze_with_chain(
            text=req.text,
            criteria=req.criteria,
            language=req.language
        )
        
        return AdvancedAnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in advanced analysis: {str(e)}"
        )


@router.post("/feedback-chains", response_model=AdvancedFeedbackResponse)
def analyze_feedback_with_chains(req: AdvancedFeedbackRequest):
    """
    Analyze essay feedback using LangChain chains for each criterion.
    
    This endpoint uses LangChain chains to perform:
    1. Overview analysis
    2. Individual criterion analysis (one chain per criterion)
    3. Final synthesis with recommendations
    
    **Available criteria:**
    - originalidad (22 points): Creative approaches, metaphors, unexpected comparisons
    - profundidad (18 points): Depth of exploration vs superficial treatment
    - integralidad (16 points): Multi-dimensional, eclectic, plural perspective
    - conciliacion (14 points): Integration of agreement points to reduce polarization
    - refutacion (12 points): Recognition and effective response to counterarguments
    - evidencia (10 points): Verifiable and relevant data to support claims
    - logica (8 points): Solid and moderate relationship between claim and evidence
    
    **Example request:**
    ```json
    {
        "text": "Essay text here...",
        "criteria": ["originalidad", "profundidad", "evidencia"],
        "language": "es"
    }
    ```
    
    **Example response:**
    ```json
    {
        "overview": "El ensayo demuestra comprensión básica...",
        "overall_strengths": ["Estructura clara", "Argumentos válidos"],
        "overall_weaknesses": ["Falta evidencia", "Vocabulario limitado"],
        "per_criterion": [
            {
                "etiqueta": "originalidad",
                "criterio": "¿Se usan enfoques creativos...?",
                "valorMaximo": 22,
                "logro": "Bien",
                "evaluacion": "Muestra creatividad básica...",
                "puntuacion": 15
            }
        ],
        "total_score": 45,
        "max_possible": 100,
        "percentage": 45.0,
        "grade_level": "Regular",
        "key_recommendations": ["Mejorar evidencia", "Ampliar vocabulario"]
    }
    ```
    """
    try:
        analyzer = get_advanced_analyzer()
        result = analyzer.analyze_feedback_with_chains(req.text, req.criteria, req.language)
        
        return AdvancedFeedbackResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in advanced feedback analysis: {str(e)}"
        )


@router.post("/analyze-memory")
def analyze_with_memory(req: AdvancedAnalysisRequest, student_id: str):
    """
    Analyze essay with conversational memory (coming soon).
    
    This endpoint will track student progress over time.
    """
    raise HTTPException(
        status_code=501,
        detail="Memory-based analysis coming soon"
    )


__all__ = ["router"]