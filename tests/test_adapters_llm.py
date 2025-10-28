"""
Tests for adapters/llm_adapter.py
"""
import pytest
import requests
import json
from unittest.mock import patch, Mock

from app.adapters.llm_adapter import LLMAdapter, get_llm_adapter
from app.core.config import settings


class TestLLMAdapter:
    """Tests for LLMAdapter class."""

    def test_init_default_provider(self):
        """Test adapter initialization with default provider."""
        adapter = LLMAdapter()
        
        assert adapter.provider == settings.LLM_PROVIDER
        assert adapter.model == settings.LLM_MODEL
        assert adapter.base_url == settings.OLLAMA_URL

    def test_init_custom_provider(self):
        """Test adapter initialization with custom provider."""
        adapter = LLMAdapter(provider="ollama")
        
        assert adapter.provider == "ollama"

    @patch('app.adapters.llm_adapter.requests.post')
    def test_generate_ollama_success(self, mock_post):
        """Test successful text generation with Ollama."""
        # Setup mock response
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            b'{"response": "{\\"score\\":75"}',
            b'{"response":",\\"rationale\\":\\"Strong AI"}"}'
        ]
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Execute
        adapter = LLMAdapter()
        result = adapter.generate("Test prompt", temperature=0.3)

        # Assert
        assert result is not None
        assert "score" in result or "75" in result
        mock_post.assert_called_once()

    @patch('app.adapters.llm_adapter.requests.post')
    def test_generate_ollama_with_temperature(self, mock_post):
        """Test generation with custom temperature."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [b'{"response":"Test response"}']
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        adapter = LLMAdapter()
        adapter.generate("Test", temperature=0.8)

        # Verify temperature was passed
        call_args = mock_post.call_args
        assert call_args[1]['json']['options']['temperature'] == 0.8

    @patch('app.adapters.llm_adapter.requests.post')
    def test_generate_ollama_with_num_predict(self, mock_post):
        """Test generation with custom num_predict."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [b'{"response":"Test"}']
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        adapter = LLMAdapter()
        adapter.generate("Test", num_predict=1024)

        # Verify num_predict was passed
        call_args = mock_post.call_args
        assert call_args[1]['json']['options']['num_predict'] == 1024

    @patch('app.adapters.llm_adapter.requests.post')
    def test_generate_ollama_connection_error(self, mock_post):
        """Test handling of connection error."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        adapter = LLMAdapter()
        
        with pytest.raises(ConnectionError) as exc_info:
            adapter.generate("Test")

        assert "Connection failed" in str(exc_info.value)

    @patch('app.adapters.llm_adapter.requests.post')
    def test_generate_ollama_timeout(self, mock_post):
        """Test handling of timeout error."""
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")

        adapter = LLMAdapter()
        
        with pytest.raises(ConnectionError):
            adapter.generate("Test")

    @patch('app.adapters.llm_adapter.requests.post')
    def test_generate_ollama_empty_response(self, mock_post):
        """Test handling of empty response."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = []
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        adapter = LLMAdapter()
        result = adapter.generate("Test")

        assert result == ""

    def test_generate_unsupported_provider(self):
        """Test error with unsupported provider."""
        adapter = LLMAdapter(provider="unsupported")
        
        with pytest.raises(ValueError) as exc_info:
            adapter.generate("Test")
        
        assert "Unsupported LLM provider" in str(exc_info.value)

    @patch('app.adapters.llm_adapter.requests.post')
    def test_generate_uses_default_config(self, mock_post):
        """Test that default config values are used when not specified."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [b'{"response":"Test"}']
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        adapter = LLMAdapter()
        adapter.generate("Test")

        # Verify default values were used
        call_args = mock_post.call_args
        options = call_args[1]['json']['options']
        assert options['temperature'] == settings.LLM_TEMPERATURE
        assert options['num_predict'] == settings.LLM_NUM_PREDICT


class TestGetLLMAdapter:
    """Tests for get_llm_adapter function."""

    def test_get_llm_adapter_singleton(self):
        """Test that get_llm_adapter returns singleton instance."""
        # Clear any existing singleton
        import app.adapters.llm_adapter as llm_module
        llm_module._llm_adapter = None

        adapter1 = get_llm_adapter()
        adapter2 = get_llm_adapter()

        assert adapter1 is adapter2

    def test_get_llm_adapter_multiple_calls_same_instance(self):
        """Test multiple calls return the same instance."""
        # Clear singleton
        import app.adapters.llm_adapter as llm_module
        llm_module._llm_adapter = None

        adapters = [get_llm_adapter() for _ in range(5)]

        # All should be the same instance
        assert all(adapter is adapters[0] for adapter in adapters[1:])

