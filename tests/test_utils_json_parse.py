"""
Tests for utils/json_parse.py
"""
import pytest
import json
from app.utils.json_parse import (
    clean_json_string,
    extract_json_from_text,
    safe_json_parse,
    parse_ollama_streaming_response
)


class TestCleanJsonString:
    """Tests for clean_json_string function."""

    def test_clean_json_string_removes_markdown_fences(self):
        """Test removing markdown code fences."""
        dirty = '```json\n{"key": "value"}\n```'
        result = clean_json_string(dirty)
        
        assert '```' not in result
        assert '"key"' in result

    def test_clean_json_string_removes_backticks(self):
        """Test removing backticks."""
        dirty = '`{"key": "value"}`'
        result = clean_json_string(dirty)
        
        assert '`' not in result
        assert '"key"' in result

    def test_clean_json_string_strips_whitespace(self):
        """Test stripping leading/trailing whitespace."""
        dirty = '   {"key": "value"}   '
        result = clean_json_string(dirty)
        
        assert result.startswith('{')
        assert result.endswith('}')

    def test_clean_json_string_already_clean(self):
        """Test already clean JSON string."""
        clean = '{"key": "value"}'
        result = clean_json_string(clean)
        
        assert result == clean

    def test_clean_json_string_nested_structure(self):
        """Test cleaning nested structure."""
        dirty = '```json\n{"nested": {"key": "value"}}\n```'
        result = clean_json_string(dirty)
        
        try:
            parsed = json.loads(result)
            assert parsed["nested"]["key"] == "value"
        except json.JSONDecodeError:
            pytest.fail("Failed to parse cleaned JSON")


class TestExtractJsonFromText:
    """Tests for extract_json_from_text function."""

    def test_extract_json_from_markdown_block(self):
        """Test extracting JSON from markdown code block."""
        text = '''Some text before
        ```json
        {"key": "value"}
        ```
        Some text after'''
        
        result = extract_json_from_text(text)
        
        assert result is not None
        parsed = json.loads(result)
        assert parsed["key"] == "value"

    def test_extract_json_direct_object(self):
        """Test extracting JSON object directly."""
        text = 'Some text {"key": "value"} more text'
        
        result = extract_json_from_text(text)
        
        assert result is not None
        parsed = json.loads(result)
        assert parsed["key"] == "value"

    def test_extract_json_array(self):
        """Test extracting JSON array."""
        text = 'Prefix [{"item": 1}, {"item": 2}] suffix'
        
        result = extract_json_from_text(text)
        
        assert result is not None
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_extract_json_none_when_not_found(self):
        """Test returning None when no JSON found."""
        text = 'This is plain text with no JSON'
        
        result = extract_json_from_text(text)
        
        assert result is None

    def test_extract_json_multiline(self):
        """Test extracting multiline JSON."""
        text = '''
        ```json
        {
            "key": "value",
            "nested": {
                "inner": "data"
            }
        }
        ```
        '''
        
        result = extract_json_from_text(text)
        
        assert result is not None
        parsed = json.loads(result)
        assert parsed["nested"]["inner"] == "data"


class TestSafeJsonParse:
    """Tests for safe_json_parse function."""

    def test_safe_json_parse_valid_json(self):
        """Test parsing valid JSON."""
        text = '{"score": 75, "rationale": "Good"}'
        
        result = safe_json_parse(text)
        
        assert isinstance(result, dict)
        assert result["score"] == 75

    def test_safe_json_parse_with_markdown(self):
        """Test parsing JSON with markdown formatting."""
        text = '```json\n{"key": "value"}\n```'
        
        result = safe_json_parse(text)
        
        assert result["key"] == "value"

    def test_safe_json_parse_nested_structure(self):
        """Test parsing nested JSON structure."""
        text = '''{"overview": "Good", "per_criterion": [
            {"etiqueta": "test", "score": 5}
        ]}'''
        
        result = safe_json_parse(text)
        
        assert result["overview"] == "Good"
        assert isinstance(result["per_criterion"], list)

    def test_safe_json_parse_error_with_invalid_json(self):
        """Test raising error with completely invalid JSON."""
        text = 'This is not JSON at all'
        
        with pytest.raises(ValueError):
            safe_json_parse(text)

    def test_safe_json_parse_list_returns_first_item(self):
        """Test that list returns first dict item."""
        text = '[{"item": 1}, {"item": 2}]'
        
        result = safe_json_parse(text)
        
        assert isinstance(result, dict)
        assert result["item"] == 1

    def test_safe_json_parse_list_error_when_empty(self):
        """Test error when list is empty."""
        text = '[]'
        
        with pytest.raises(ValueError):
            safe_json_parse(text)

    def test_safe_json_parse_list_error_when_not_dict_list(self):
        """Test error when list doesn't contain dicts."""
        text = '[1, 2, 3]'
        
        with pytest.raises(ValueError):
            safe_json_parse(text)


class TestParseOllamaStreamingResponse:
    """Tests for parse_ollama_streaming_response function."""

    def test_parse_ollama_streaming_response_success(self):
        """Test parsing successful streaming response."""
        lines = [
            b'{"response": "Hello"}',
            b'{"response": " World"}',
            b'{"response": "!"}'
        ]
        
        result = parse_ollama_streaming_response(lines)
        
        assert result == "Hello World!"

    def test_parse_ollama_streaming_response_empty_lines(self):
        """Test handling empty lines."""
        lines = [
            b'{"response": "Text"}',
            b'',
            b'{"response": "More"}'
        ]
        
        result = parse_ollama_streaming_response(lines)
        
        assert result == "TextMore"

    def test_parse_ollama_streaming_response_string_lines(self):
        """Test handling string lines."""
        lines = [
            '{"response": "Part1"}',
            '{"response": "Part2"}'
        ]
        
        result = parse_ollama_streaming_response(lines)
        
        assert result == "Part1Part2"

    def test_parse_ollama_streaming_response_invalid_json(self):
        """Test handling invalid JSON chunks."""
        lines = [
            b'{"response": "Valid"}',
            b'Invalid JSON',
            b'{"response": "Valid"}'
        ]
        
        result = parse_ollama_streaming_response(lines)
        
        assert result == "ValidValid"

    def test_parse_ollama_streaming_response_no_response_key(self):
        """Test handling chunks without response key."""
        lines = [
            b'{"response": "Text"}',
            b'{"status": "ok"}',
            b'{"response": "More"}'
        ]
        
        result = parse_ollama_streaming_response(lines)
        
        assert result == "TextMore"

    def test_parse_ollama_streaming_response_strips_result(self):
        """Test that result is stripped."""
        lines = [
            b'{"response": "  Text  "}'
        ]
        
        result = parse_ollama_streaming_response(lines)
        
        assert result == "Text"

