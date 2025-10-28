"""
Tests for services/analyzer.py
"""
import pytest
from unittest.mock import patch, Mock
from fastapi import HTTPException

from app.services.analyzer import (
    analyze_ai_likelihood,
    generate_essay_feedback,
    get_criteria_metadata
)
from app.models.analyze import AILikelihoodResponse, FeedbackResponse


class TestAnalyzeAILikelihood:
    """Tests for analyze_ai_likelihood function."""

    @patch('app.services.analyzer.get_llm_adapter')
    @patch('app.services.analyzer.safe_json_parse')
    def test_analyze_ai_likelihood_success(
        self, 
        mock_parse, 
        mock_get_adapter,
        mock_ai_likelihood_response,
        sample_essay_text
    ):
        """Test successful AI likelihood analysis."""
        # Setup mocks
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_ai_likelihood_response

        # Execute
        result = analyze_ai_likelihood(sample_essay_text, "en")

        # Assert
        assert isinstance(result, AILikelihoodResponse)
        assert result.score == 75
        assert len(result.caveats) == 2
        mock_get_adapter.assert_called_once()
        mock_adapter.generate.assert_called_once()

    @patch('app.services.analyzer.get_llm_adapter')
    @patch('app.services.analyzer.safe_json_parse')
    def test_analyze_ai_likelihood_spanish(
        self,
        mock_parse,
        mock_get_adapter,
        sample_essay_text
    ):
        """Test AI likelihood analysis in Spanish."""
        mock_response = {
            "score": 80,
            "rationale": "El texto muestra patrones de IA.",
            "caveats": ["Análisis aproximado"]
        }
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_response

        result = analyze_ai_likelihood(sample_essay_text, "es")

        assert result.score == 80
        assert "IA" in result.rationale

    @patch('app.services.analyzer.get_llm_adapter')
    @patch('app.services.analyzer.safe_json_parse')
    def test_analyze_ai_likelihood_parse_error(
        self,
        mock_parse,
        mock_get_adapter,
        sample_essay_text
    ):
        """Test AI likelihood analysis with parse error."""
        # Setup mocks
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.side_effect = ValueError("Parse error")

        # Execute and assert
        with pytest.raises(HTTPException) as exc_info:
            analyze_ai_likelihood(sample_essay_text)

        assert exc_info.value.status_code == 400
        assert "Failed to parse" in exc_info.value.detail

    @patch('app.services.analyzer.get_llm_adapter')
    def test_analyze_ai_likelihood_connection_error(
        self,
        mock_get_adapter,
        sample_essay_text
    ):
        """Test AI likelihood analysis with connection error."""
        mock_adapter = Mock()
        mock_adapter.generate.side_effect = ConnectionError("Connection failed")
        mock_get_adapter.return_value = mock_adapter

        with pytest.raises(HTTPException) as exc_info:
            analyze_ai_likelihood(sample_essay_text)

        assert exc_info.value.status_code == 500


class TestGenerateEssayFeedback:
    """Tests for generate_essay_feedback function."""

    @patch('app.services.analyzer.get_llm_adapter')
    @patch('app.services.analyzer.safe_json_parse')
    def test_generate_essay_feedback_success(
        self,
        mock_parse,
        mock_get_adapter,
        mock_feedback_response,
        sample_essay_text
    ):
        """Test successful essay feedback generation."""
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_feedback_response

        result = generate_essay_feedback(sample_essay_text, None, "en")

        assert isinstance(result, FeedbackResponse)
        assert len(result.per_criterion) == 2
        assert result.per_criterion[0].etiqueta == "originalidad"

    @patch('app.services.analyzer.get_llm_adapter')
    @patch('app.services.analyzer.safe_json_parse')
    def test_generate_essay_feedback_custom_criteria(
        self,
        mock_parse,
        mock_get_adapter,
        sample_essay_text
    ):
        """Test feedback generation with custom criteria."""
        custom_response = {
            "overview": "Good essay",
            "per_criterion": [{
                "etiqueta": "logica",
                "criterio": "Custom criterion",
                "valorMaximo": 8,
                "logro": "Bien",
                "evaluacion": "Good logic",
                "puntuacion": 6
            }]
        }
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = custom_response

        result = generate_essay_feedback(
            sample_essay_text, 
            ["logica"], 
            "en"
        )

        assert len(result.per_criterion) == 1
        assert result.per_criterion[0].etiqueta == "logica"

    @patch('app.services.analyzer.get_llm_adapter')
    def test_generate_essay_feedback_invalid_response(
        self,
        mock_get_adapter,
        sample_essay_text
    ):
        """Test feedback generation with invalid LLM response."""
        mock_adapter = Mock()
        mock_adapter.generate.side_effect = ValueError("Invalid JSON")
        mock_get_adapter.return_value = mock_adapter

        with pytest.raises(HTTPException) as exc_info:
            generate_essay_feedback(sample_essay_text)

        assert exc_info.value.status_code == 400


class TestGetCriteriaMetadata:
    """Tests for get_criteria_metadata function."""

    def test_get_criteria_metadata_success(self):
        """Test successful criteria metadata retrieval."""
        result = get_criteria_metadata()

        assert "summary" in result
        assert "total_points" in result
        assert isinstance(result["summary"], str)
        assert isinstance(result["total_points"], int)
        assert result["total_points"] > 0

