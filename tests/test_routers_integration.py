"""
Integration tests for routers.
"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_endpoint_success(self):
        """Test successful health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "version" in data
        assert "llm_provider" in data


class TestAnalyzeEndpoints:
    """Tests for /analyze endpoints."""

    @patch('app.services.analyzer.get_llm_adapter')
    @patch('app.services.analyzer.safe_json_parse')
    def test_ai_likelihood_endpoint_success(
        self,
        mock_parse,
        mock_get_adapter,
        mock_ai_likelihood_response
    ):
        """Test successful AI likelihood endpoint call."""
        # Setup mocks
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_ai_likelihood_response

        # Execute
        response = client.post(
            "/analyze/ai-likelihood",
            json={"text": "Test essay text for AI analysis."}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "rationale" in data
        assert "caveats" in data

    @patch('app.services.analyzer.get_llm_adapter')
    @patch('app.services.analyzer.safe_json_parse')
    def test_ai_likelihood_endpoint_language_spanish(
        self,
        mock_parse,
        mock_get_adapter
    ):
        """Test AI likelihood endpoint with Spanish language."""
        mock_response = {
            "score": 80,
            "rationale": "El texto muestra patrones de IA.",
            "caveats": ["Análisis aproximado"]
        }
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_response

        response = client.post(
            "/analyze/ai-likelihood",
            json={
                "text": "Texto de prueba para análisis.",
                "language": "es"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "patrones" in data["rationale"].lower() or "ia" in data["rationale"].lower()

    def test_ai_likelihood_endpoint_empty_text(self):
        """Test AI likelihood endpoint with empty text."""
        response = client.post(
            "/analyze/ai-likelihood",
            json={"text": ""}
        )

        assert response.status_code == 422  # Validation error

    @patch('app.services.analyzer.get_llm_adapter')
    @patch('app.services.analyzer.safe_json_parse')
    def test_feedback_endpoint_success(
        self,
        mock_parse,
        mock_get_adapter,
        mock_feedback_response
    ):
        """Test successful feedback endpoint call."""
        # Setup mocks
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_feedback_response

        # Execute
        response = client.post(
            "/analyze/feedback",
            json={"text": "Test essay text for feedback."}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "overview" in data
        assert "per_criterion" in data
        assert len(data["per_criterion"]) > 0

    @patch('app.services.analyzer.get_llm_adapter')
    @patch('app.services.analyzer.safe_json_parse')
    def test_feedback_endpoint_custom_criteria(
        self,
        mock_parse,
        mock_get_adapter
    ):
        """Test feedback endpoint with custom criteria."""
        mock_response = {
            "overview": "Good essay",
            "per_criterion": [{
                "etiqueta": "logica",
                "criterio": "Custom",
                "valorMaximo": 8,
                "logro": "Bien",
                "evaluacion": "Good",
                "puntuacion": 6
            }]
        }
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_response

        response = client.post(
            "/analyze/feedback",
            json={
                "text": "Test essay.",
                "criteria": ["logica"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["per_criterion"]) == 1


class TestGuideEndpoints:
    """Tests for /guide endpoints."""

    @patch('app.services.guidance.get_llm_adapter')
    @patch('app.services.guidance.safe_json_parse')
    def test_guide_endpoint_success(
        self,
        mock_parse,
        mock_get_adapter,
        mock_guidance_response
    ):
        """Test successful guide endpoint call."""
        # Setup mocks
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_guidance_response

        # Execute
        response = client.post(
            "/guide/",
            json={"section": "claim"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "section" in data
        assert "purpose" in data
        assert "steps" in data
        assert "checklist" in data

    def test_guide_endpoint_invalid_section(self):
        """Test guide endpoint with invalid section."""
        response = client.post(
            "/guide/",
            json={"section": "invalid_section"}
        )

        assert response.status_code == 422  # Validation error

    @patch('app.services.guidance.get_llm_adapter')
    @patch('app.services.guidance.safe_json_parse')
    def test_check_section_endpoint_success(
        self,
        mock_parse,
        mock_get_adapter,
        mock_section_advice_response
    ):
        """Test successful check-section endpoint call."""
        # Setup mocks
        mock_adapter = Mock()
        mock_adapter.generate.return_value = '{"response": "test"}'
        mock_get_adapter.return_value = mock_adapter
        mock_parse.return_value = mock_section_advice_response

        # Execute
        response = client.post(
            "/guide/check-section",
            json={
                "section": "claim",
                "text": "This is my claim statement."
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "section" in data
        assert "strengths" in data
        assert "issues" in data
        assert "questions_to_refine" in data

    def test_check_section_endpoint_empty_text(self):
        """Test check-section endpoint with empty text."""
        response = client.post(
            "/guide/check-section",
            json={
                "section": "claim",
                "text": ""
            }
        )

        assert response.status_code == 422  # Validation error


class TestRouteNotFound:
    """Tests for non-existent routes."""

    def test_nonexistent_route(self):
        """Test accessing a non-existent route."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404


class TestRequestValidation:
    """Tests for request validation."""

    def test_analyze_feedback_too_long_text(self):
        """Test feedback endpoint with text exceeding limit."""
        long_text = "a" * 9000
        
        response = client.post(
            "/analyze/feedback",
            json={"text": long_text}
        )

        assert response.status_code == 422  # Validation error

    def test_check_section_invalid_section_type(self):
        """Test check-section with invalid section."""
        response = client.post(
            "/guide/check-section",
            json={
                "section": "not_a_section",
                "text": "Some text"
            }
        )

        assert response.status_code == 422  # Validation error

