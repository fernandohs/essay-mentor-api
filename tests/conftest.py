"""
Pytest configuration and shared fixtures for Essay Mentor API tests.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app


# Test client fixture
@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


# Mock LLM response fixtures
@pytest.fixture
def mock_ai_likelihood_response():
    """Mock response for AI likelihood detection."""
    return {
        "score": 75,
        "rationale": "The text shows strong AI generation patterns with formulaic phrasing.",
        "caveats": ["Analysis is approximate", "Limited sample size"]
    }


@pytest.fixture
def mock_feedback_response():
    """Mock response for essay feedback."""
    return {
        "overview": "The essay demonstrates good structure and argumentation.",
        "per_criterion": [
            {
                "etiqueta": "originalidad",
                "criterio": "¿Se usan enfoques creativos, metáforas o comparaciones inesperadas?",
                "valorMaximo": 22,
                "logro": "Muy Bien",
                "evaluacion": "El estudiante usa enfoques creativos con metáforas interesantes.",
                "puntuacion": 17
            },
            {
                "etiqueta": "profundidad",
                "criterio": "¿La respuesta es superficial o explora el tema de manera profunda?",
                "valorMaximo": 18,
                "logro": "Bien",
                "evaluacion": "Buena exploración del tema con algunas áreas superficiales.",
                "puntuacion": 12
            }
        ]
    }


@pytest.fixture
def mock_guidance_response():
    """Mock response for section guidance."""
    return {
        "section": "claim",
        "purpose": "Present the central argument",
        "steps": ["Define your main point", "Make it debatable", "Be specific"],
        "checklist": ["Clear statement", "Debatable", "Specific", "Relevant"],
        "examples_do": ["Technology enhances learning"],
        "examples_dont": ["Technology is good"],
        "tips": ["escapar", "definir", "afinar"]
    }


@pytest.fixture
def mock_section_advice_response():
    """Mock response for section checking."""
    return {
        "section": "claim",
        "strengths": ["Clear main point", "Well positioned"],
        "issues": ["Could be more specific"],
        "questions_to_refine": ["What evidence supports this?"],
        "revision_strategies": ["Add specific examples"]
    }


@pytest.fixture
def mock_llm_adapter():
    """Mock LLM adapter for testing."""
    mock_adapter = Mock()
    mock_adapter.generate = Mock(return_value='{"test": "response"}')
    return mock_adapter


@pytest.fixture
def sample_essay_text():
    """Sample essay text for testing."""
    return """
    El avance de la tecnología ha transformado profundamente la educación.
    Las herramientas digitales permiten un aprendizaje más interactivo y 
    personalizado. Sin embargo, es importante considerar los desafíos que 
    presenta esta transformación.
    """


@pytest.fixture
def sample_section_text():
    """Sample section text for testing."""
    return "La tecnología educativa facilita el aprendizaje personalizado."


@pytest.fixture
def mock_ollama_streaming_response():
    """Mock Ollama streaming response for testing."""
    return [
        b'{"response":"{\\"score\\":75"}',
        b'{"response":",\\"rationale\\":\\"Strong AI',
        b'{"response":" patterns\\"}"}'
    ]


@pytest.fixture
def mock_ollama_complete_response():
    """Mock complete Ollama response after streaming."""
    return '{"score": 75, "rationale": "Strong AI patterns", "caveats": ["Approximate"]}'

