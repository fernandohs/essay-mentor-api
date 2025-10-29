"""
Advanced analysis service using LangChain features.
Provides multi-step analysis, memory, and advanced LLM workflows.
"""

from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from langchain.chains import LLMChain, SequentialChain
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from app.adapters.llm_adapter import get_llm_adapter
from app.utils.json_parse import safe_json_parse
from app.core.config import settings


# Define output models for structured parsing with Pydantic
# Using the same criteria as analyzer.py (Extended Toulmin Model)

class CriterionEvaluation(BaseModel):
    """Evaluation of a single criterion from the Extended Toulmin Model"""
    etiqueta: str = Field(description="Criterion name")
    criterio: str = Field(description="Criterion description")
    valorMaximo: int = Field(description="Maximum points for this criterion")
    logro: str = Field(description="Achievement level")
    evaluacion: str = Field(description="Qualitative evaluation")
    puntuacion: int = Field(description="Points awarded")
    
    @classmethod
    def model_validate(cls, obj):
        if isinstance(obj, dict):
            # Convert float to int for numeric fields
            if 'valorMaximo' in obj and isinstance(obj['valorMaximo'], float):
                obj['valorMaximo'] = int(obj['valorMaximo'])
            if 'puntuacion' in obj and isinstance(obj['puntuacion'], float):
                obj['puntuacion'] = int(obj['puntuacion'])
        return super().model_validate(obj)


class CompleteFeedbackAnalysis(BaseModel):
    """Complete feedback analysis using Extended Toulmin Model criteria"""
    overview: str = Field(description="Overall essay assessment")
    per_criterion: List[CriterionEvaluation] = Field(description="Evaluation per criterion")
    
    @classmethod
    def model_validate(cls, obj):
        if isinstance(obj, dict) and 'per_criterion' in obj:
            # Ensure per_criterion is a list
            if not isinstance(obj['per_criterion'], list):
                obj['per_criterion'] = [obj['per_criterion']]
        return super().model_validate(obj)


def _parse_with_pydantic(response_content: str, parser: PydanticOutputParser, step_name: str) -> Dict[str, Any]:
    """
    Parse LLM response using PydanticOutputParser for structured output.
    
    Args:
        response_content: Raw response from LLM
        parser: PydanticOutputParser instance to parse the response
        step_name: Name of the analysis step for error context
        
    Returns:
        Parsed data as dictionary
        
    Raises:
        HTTPException: If parsing fails
    """
    try:
        # Clean markdown code fences if present
        import re
        cleaned_response = re.sub(r'```json\s*', '', response_content)
        cleaned_response = re.sub(r'```\s*$', '', cleaned_response, flags=re.MULTILINE)
        cleaned_response = cleaned_response.strip()
        
        # Remove trailing commas before closing braces/brackets (common JSON error)
        cleaned_response = re.sub(r',\s*}', '}', cleaned_response)
        cleaned_response = re.sub(r',\s*\]', ']', cleaned_response)
        
        # Use PydanticOutputParser for structured parsing
        parsed = parser.parse(cleaned_response)
        # Convert Pydantic model to dict
        return parsed.model_dump()
    except Exception as e:
        # Log the problematic response for debugging
        print(f"Error parsing {step_name} response with Pydantic:")
        print(f"Raw response: {response_content[:500]}...")
        print(f"Error: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing {step_name} response: {str(e)}"
        )


def _parse_llm_response(response_content: str, step_name: str) -> Dict[str, Any]:
    """
    Parse LLM response using safe_json_parse (fallback method).
    
    Args:
        response_content: Raw response from LLM
        step_name: Name of the analysis step for error context
        
    Returns:
        Parsed data as dictionary
        
    Raises:
        HTTPException: If parsing fails
    """
    try:
        parsed_data = safe_json_parse(response_content)
        if not isinstance(parsed_data, dict):
            raise ValueError(f"Expected dict but got {type(parsed_data).__name__}")
        return parsed_data
    except Exception as e:
        print(f"Error parsing {step_name} response:")
        print(f"Raw response: {response_content[:500]}...")
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing {step_name} response: {str(e)}"
        )


class AdvancedEssayAnalyzer:
    """
    Advanced essay analyzer using LangChain chains.
    Provides multi-step analysis, memory, and complex reasoning.
    """
    
    def __init__(self):
        """Initialize advanced analyzer."""
        # Use LangChain adapter for advanced features
        self.adapter = get_llm_adapter(provider="langchain", model=settings.LLM_MODEL)
        # Access the internal LangChain adapter
        self.llm = self.adapter._adapter.get_llm()
    
    def analyze_with_chain(
        self,
        text: str,
        criteria: Optional[List[str]] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze essay using LangChain with Extended Toulmin Model criteria.
        
        This uses the SAME criteria as /analyze/feedback endpoint:
        - originalidad (22 points): Creative approaches, metaphors
        - profundidad (18 points): Deep vs superficial analysis
        - integralidad (16 points): Multidimensional perspective
        - conciliacion (14 points): Integration of agreement points
        - refutacion (12 points): Counter-argument recognition
        - evidencia (10 points): Verifiable, relevant data
        - logica (8 points): Solid connection between claim and evidence
        
        Args:
            text: Essay text to analyze
            criteria: Optional list of criteria (uses all if None)
            language: Language for the response
            
        Returns:
            Dict with comprehensive feedback using Toulmin Model
        """
        if language is None:
            language = settings.DEFAULT_LANGUAGE
        
        try:
            from app.prompts.criteria_data import ESSAY_RUBRIC_CRITERIA, DEFAULT_CRITERIA, TOTAL_POINTS
            
            lang_name = "Spanish" if language == "es" else "English"
            used_criteria = criteria if criteria else DEFAULT_CRITERIA
            
            # Step 1: Generate overview
            overview_prompt = f"""
            Proporciona una evaluación general de este ensayo en {lang_name}:
            
            Texto: {text}
            
            Responde en máximo 150 palabras con una visión general del ensayo, destacando sus fortalezas principales y áreas de mejora.
            """
            
            overview_response = self.llm.invoke([HumanMessage(content=overview_prompt)])
            overview_text = overview_response.content.strip()
            
            # Step 2: Evaluate each criterion using LangChain chains
            criterion_evaluations = []
            
            for criterion_key in used_criteria:
                if criterion_key not in ESSAY_RUBRIC_CRITERIA:
                    continue
                
                criterion_info = ESSAY_RUBRIC_CRITERIA[criterion_key]
                max_points = criterion_info["maxPoints"]
                description = criterion_info["description"]
                
                # Create parser for this criterion
                criterion_parser = PydanticOutputParser(pydantic_object=CriterionEvaluation)
                
                # Generate prompt for this specific criterion
                criterion_prompt = f"""
                Evalúa este ensayo según el siguiente criterio del Modelo de Toulmin Extendido:
                
                Criterio: {criterion_key}
                Descripción: {description}
                Puntos máximos: {max_points}
                
                Texto del ensayo:
                {text}
                
                Responde con un JSON que contenga EXACTAMENTE estos campos:
                - etiqueta: "{criterion_key}"
                - criterio: "{description}"
                - valorMaximo: {max_points}
                - logro: texto describiendo el nivel de logro (50-80 palabras)
                - evaluacion: "excelente", "bueno", "regular", o "insuficiente"
                - puntuacion: número entre 0 y {max_points}
                
                Ejemplo:
                {{
                    "etiqueta": "{criterion_key}",
                    "criterio": "{description}",
                    "valorMaximo": {max_points},
                    "logro": "El ensayo demuestra...",
                    "evaluacion": "bueno",
                    "puntuacion": {int(max_points * 0.7)}
                }}
                
                IMPORTANTE: Completa TODOS los campos. La puntuación debe estar entre 0 y {max_points}.
                """
                
                criterion_response = self.llm.invoke([HumanMessage(content=criterion_prompt)])
                criterion_data = _parse_with_pydantic(criterion_response.content, criterion_parser, f"criterion_{criterion_key}")
                
                criterion_evaluations.append(criterion_data)
            
            # Step 3: Calculate total score and prepare result
            total_score = sum(c.get("puntuacion", 0) if isinstance(c, dict) else 0 for c in criterion_evaluations)
            max_possible = sum(ESSAY_RUBRIC_CRITERIA[criterion]["maxPoints"] for criterion in used_criteria if criterion in ESSAY_RUBRIC_CRITERIA)
            
            result = {
                "overview": overview_text,
                "per_criterion": criterion_evaluations,
                "total_score": total_score,
                "max_possible_score": max_possible,
                "percentage": round((total_score / max_possible) * 100, 1) if max_possible > 0 else 0
            }
            
            return result
            
        except Exception as e:
            import traceback
            error_detail = f"Error in advanced analysis chain: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)  # Log to console for debugging
            raise HTTPException(
                status_code=500,
                detail=f"Error in advanced analysis chain: {str(e)}"
            )
    
    def analyze_feedback_with_chains(
        self,
        text: str,
        criteria: Optional[List[str]] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze essay feedback using chains for each criterion.
        
        Chain flow:
        1. Overview analysis
        2. Individual criterion analysis (one chain per criterion)
        3. Final synthesis
        
        Args:
            text: Essay text to analyze
            criteria: List of criteria to evaluate (uses defaults if None)
            language: Language for the response
            
        Returns:
            Dict with comprehensive feedback results
        """
        if language is None:
            language = settings.DEFAULT_LANGUAGE
        
        try:
            from app.prompts.criteria_data import ESSAY_RUBRIC_CRITERIA, DEFAULT_CRITERIA
            
            lang_name = "Spanish" if language == "es" else "English"
            
            # Use provided criteria or defaults
            used_criteria = criteria if criteria else DEFAULT_CRITERIA
            
            # Step 1: Overview analysis
            overview_prompt = f"""
            Analiza el ENSAYO GENERAL en {lang_name}:
            
            Texto: {text}
            
            Proporciona una evaluación general del ensayo.
            
            Responde SOLO en JSON válido:
            {{
                "overview": "<evaluación general en 2-3 oraciones, máximo 150 palabras>",
                "overall_strengths": ["<fortaleza 1>", "<fortaleza 2>", "<fortaleza 3>"],
                "overall_weaknesses": ["<debilidad 1>", "<debilidad 2>", "<debilidad 3>"]
            }}
            """
            
            overview_response = self.llm.invoke([HumanMessage(content=overview_prompt)])
            overview_data = _parse_llm_response(overview_response.content, "overview")
            
            # Step 2: Analyze each criterion individually
            per_criterion_results = []
            
            for criterion in used_criteria:
                criterion_info = ESSAY_RUBRIC_CRITERIA.get(criterion, {})
                criterion_desc = criterion_info.get('description', '')
                max_points = criterion_info.get('maxPoints', 0)
                
                criterion_prompt = f"""
                Analiza el criterio "{criterion}" en {lang_name}:
                
                Criterio: {criterion_desc}
                Puntos máximos: {max_points}
                
                Evaluación general previa: {overview_data.get('overview', '')}
                
                Texto del ensayo: {text}
                
                Evalúa específicamente este criterio.
                
                Responde SOLO en JSON válido:
                {{
                    "etiqueta": "{criterion}",
                    "criterio": "{criterion_desc}",
                    "valorMaximo": {max_points},
                    "logro": "<Excepcional|Muy Bien|Bien|Regular|Insuficiente>",
                    "evaluacion": "<evaluación específica del criterio, máximo 100 palabras>",
                    "puntuacion": <puntuación numérica entre 0 y {max_points}>
                }}
                """
                
                criterion_response = self.llm.invoke([HumanMessage(content=criterion_prompt)])
                criterion_data = _parse_llm_response(criterion_response.content, f"criterion_{criterion}")
                per_criterion_results.append(criterion_data)
            
            # Step 3: Final synthesis
            synthesis_prompt = f"""
            Sintetiza el análisis final en {lang_name}:
            
            Evaluación general: {overview_data.get('overview', '')}
            
            Criterios evaluados: {len(per_criterion_results)} criterios
            
            Responde SOLO en JSON válido:
            {{
                "total_score": <suma de todas las puntuaciones>,
                "max_possible": <suma de todos los puntos máximos>,
                "percentage": <porcentaje de logro>,
                "grade_level": "<Nivel de logro general>",
                "key_recommendations": ["<recomendación 1>", "<recomendación 2>", "<recomendación 3>"]
            }}
            """
            
            synthesis_response = self.llm.invoke([HumanMessage(content=synthesis_prompt)])
            synthesis_data = _parse_llm_response(synthesis_response.content, "synthesis")
            
            # Combine all results
            result = {
                "overview": overview_data.get("overview", ""),
                "overall_strengths": overview_data.get("overall_strengths", []),
                "overall_weaknesses": overview_data.get("overall_weaknesses", []),
                "per_criterion": per_criterion_results,
                "total_score": synthesis_data.get("total_score", 0),
                "max_possible": synthesis_data.get("max_possible", 0),
                "percentage": synthesis_data.get("percentage", 0),
                "grade_level": synthesis_data.get("grade_level", ""),
                "key_recommendations": synthesis_data.get("key_recommendations", [])
            }
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error in feedback analysis chains: {str(e)}"
            )


# Factory function for easy access
_analyzer = None

def get_advanced_analyzer() -> AdvancedEssayAnalyzer:
    """
    Get or create advanced analyzer instance.
    
    Returns:
        AdvancedEssayAnalyzer instance
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = AdvancedEssayAnalyzer()
    return _analyzer


__all__ = ["AdvancedEssayAnalyzer", "get_advanced_analyzer"]
