"""
Tests for services/guidance.py
"""
import pytest
from unittest.mock import patch, Mock
from fastapi import HTTPException

from app.services.guidance import (
    get_section_guidance,
    check_section_quality
)
from app.models.guide import GuidanceResponse, SectionAdviceResponse


class TestGetSectionGuidance:
    """Tests for get_section_guidance function."""

    @patch('app.services.guidance.get_llm_adapter')
    @patch('app.services.guidance.safe_json_parse')
    def test_get_section_guidance_success(
        self,
        mock_parse,
        mock_get_adapter,
        mock_guidance_response
    ):
        """Test successful section guidance generation."""
        # Setup mocks
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_guidance_response

        # Execute
        result = get_section_guidance("claim", "en")

        # Assert
        assert isinstance(result, GuidanceResponse)
        assert result.section == "claim"
        assert len(result.steps) == 3
        assert len(result.checklist) == 4
        mock_get_adapter.assert_called_once()

    @patch('app.services.guidance.get_llm_adapter')
    @patch('app.services.guidance.safe_json_parse')
    def test_get_section_guidance_all_sections(
        self,
        mock_parse,
        mock_get_adapter,
        mock_guidance_response
    ):
        """Test guidance generation for different sections."""
        sections = ["claim", "reasoning", "evidence", "backing", "reservation", "rebuttal"]
        
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_guidance_response

        for section in sections:
            mock_guidance_response["section"] = section
            result = get_section_guidance(section, "en")
            assert result.section == section

    @patch('app.services.guidance.get_llm_adapter')
    @patch('app.services.guidance.safe_json_parse')
    def test_get_section_guidance_spanish(
        self,
        mock_parse,
        mock_get_adapter
    ):
        """Test guidance generation in Spanish."""
        spanish_response = {
            "section": "claim",
            "purpose": "Presentar el argumento central",
            "steps": ["Paso 1", "Paso 2", "Paso 3"],
            "checklist": ["Item 1", "Item 2", "Item 3"],
            "examples_do": ["Ejemplo bueno"],
            "examples_dont": ["Ejemplo malo"],
            "tips": ["Consejo 1", "Consejo 2"]
        }
        
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = spanish_response

        result = get_section_guidance("claim", "es")

        assert "argumento" in result.purpose

    @patch('app.services.guidance.get_llm_adapter')
    def test_get_section_guidance_parse_error(
        self,
        mock_get_adapter
    ):
        """Test guidance generation with parse error."""
        mock_adapter = Mock()
        mock_adapter.generate.side_effect = ValueError("Parse error")
        mock_get_adapter.return_value = mock_adapter

        with pytest.raises(HTTPException) as exc_info:
            get_section_guidance("claim", "en")

        assert exc_info.value.status_code == 400


class TestCheckSectionQuality:
    """Tests for check_section_quality function."""

    @patch('app.services.guidance.get_llm_adapter')
    @patch('app.services.guidance.safe_json_parse')
    def test_check_section_quality_success(
        self,
        mock_parse,
        mock_get_adapter,
        mock_section_advice_response,
        sample_section_text
    ):
        """Test successful section quality check."""
        # Setup mocks
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_section_advice_response

        # Execute
        result = check_section_quality("claim", sample_section_text, "en")

        # Assert
        assert isinstance(result, SectionAdviceResponse)
        assert result.section == "claim"
        assert len(result.strengths) > 0
        assert len(result.issues) > 0
        mock_get_adapter.assert_called_once()

    @patch('app.services.guidance.get_llm_adapter')
    @patch('app.services.guidance.safe_json_parse')
    def test_check_section_quality_all_sections(
        self,
        mock_parse,
        mock_get_adapter,
        sample_section_text
    ):
        """Test section checking for different sections."""
        sections = ["claim", "reasoning", "evidence"]
        
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        
        advice = {
            "section": "claim",
            "strengths": ["Good"],
            "issues": ["Needs work"],
            "questions_to_refine": ["Question?"],
            "revision_strategies": ["Strategy"]
        }
        mock_parse.return_value = advice

        for section in sections:
            advice["section"] = section
            result = check_section_quality(section, sample_section_text, "en")
            assert result.section == section

    @patch('app.services.guidance.get_llm_adapter')
    def test_check_section_quality_invalid_response(
        self,
        mock_get_adapter,
        sample_section_text
    ):
        """Test section checking with invalid LLM response."""
        mock_adapter = Mock()
        mock_adapter.generate.side_effect = ValueError("Invalid JSON")
        mock_get_adapter.return_value = mock_adapter

        with pytest.raises(HTTPException) as exc_info:
            check_section_quality("claim", sample_section_text, "en")

        assert exc_info.value.status_code == 400

