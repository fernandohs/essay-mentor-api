"""
Tests for utils/text_format.py
"""
import pytest
from app.utils.text_format import (
    normalize_text,
    escape_for_json,
    validate_text_length,
    clean_and_validate_text,
    format_text_for_api
)


class TestNormalizeText:
    """Tests for normalize_text function."""

    def test_normalize_text_trims_whitespace(self):
        """Test trimming leading/trailing whitespace."""
        text = "   Hello World   "
        result = normalize_text(text)
        
        assert result == "Hello World"

    def test_normalize_text_handles_line_breaks(self):
        """Test handling different line break types."""
        text = "Line1\r\nLine2\rLine3\nLine4"
        result = normalize_text(text)
        
        assert "\r" not in result
        assert "Line1" in result

    def test_normalize_text_removes_multiple_line_breaks(self):
        """Test removing excessive line breaks."""
        text = "Para1\n\n\nPara2\n\n\n\nPara3"
        result = normalize_text(text)
        
        assert "\n\n\n\n" not in result
        assert "Para1" in result and "Para3" in result

    def test_normalize_text_removes_multiple_spaces(self):
        """Test removing multiple consecutive spaces."""
        text = "Hello    World    Test"
        result = normalize_text(text)
        
        assert "  " not in result

    def test_normalize_text_empty_string(self):
        """Test handling empty string."""
        text = ""
        result = normalize_text(text)
        
        assert result == ""


class TestEscapeForJson:
    """Tests for escape_for_json function."""

    def test_escape_for_json_backslash(self):
        """Test escaping backslashes."""
        text = "Path\\to\\file"
        result = escape_for_json(text)
        
        assert "\\\\" in result

    def test_escape_for_json_quotes(self):
        """Test escaping quotes."""
        text = 'He said "Hello"'
        result = escape_for_json(text)
        
        assert '\\"' in result

    def test_escape_for_json_newlines(self):
        """Test escaping newlines."""
        text = "Line1\nLine2"
        result = escape_for_json(text)
        
        assert "\\n" in result
        assert "\n" not in result

    def test_escape_for_json_carriage_return(self):
        """Test escaping carriage returns."""
        text = "Line1\rLine2"
        result = escape_for_json(text)
        
        assert "\\r" in result

    def test_escape_for_json_tabs(self):
        """Test escaping tabs."""
        text = "Col1\tCol2"
        result = escape_for_json(text)
        
        assert "\\t" in result

    def test_escape_for_json_plain_text(self):
        """Test plain text without special characters."""
        text = "Simple text"
        result = escape_for_json(text)
        
        assert result == text


class TestValidateTextLength:
    """Tests for validate_text_length function."""

    def test_validate_text_length_valid(self):
        """Test valid text length."""
        text = "This is a valid text."
        is_valid, message = validate_text_length(text, max_length=100)
        
        assert is_valid is True
        assert "valid" in message.lower() or "length" in message.lower()

    def test_validate_text_length_too_long(self):
        """Test text that exceeds maximum length."""
        text = "a" * 200
        is_valid, message = validate_text_length(text, max_length=100)
        
        assert is_valid is False
        assert "exceeds" in message

    def test_validate_text_length_empty(self):
        """Test empty text."""
        text = ""
        is_valid, message = validate_text_length(text)
        
        assert is_valid is False
        assert "empty" in message

    def test_validate_text_length_at_limit(self):
        """Test text at the limit."""
        text = "a" * 100
        is_valid, _ = validate_text_length(text, max_length=100)
        
        assert is_valid is True


class TestCleanAndValidateText:
    """Tests for clean_and_validate_text function."""

    def test_clean_and_validate_text_success(self):
        """Test successful cleaning and validation."""
        text = "   Clean text   "
        cleaned, issues = clean_and_validate_text(text, max_length=100)
        
        assert cleaned is not None
        assert len(issues) >= 1
        assert cleaned == "Clean text"

    def test_clean_and_validate_text_too_long(self):
        """Test text that is too long."""
        text = "a" * 9000
        cleaned, issues = clean_and_validate_text(text, max_length=8000)
        
        assert cleaned is None
        assert len(issues) >= 1

    def test_clean_and_validate_text_short_warning(self):
        """Test warning for very short text."""
        text = "Short"
        cleaned, issues = clean_and_validate_text(text)
        
        assert cleaned is not None
        assert any("short" in issue.lower() for issue in issues)

    def test_clean_and_validate_text_normalizes(self):
        """Test that text is normalized."""
        text = "Line1\n\n\nLine2"
        cleaned, _ = clean_and_validate_text(text)
        
        assert "\n\n\n" not in cleaned


class TestFormatTextForApi:
    """Tests for format_text_for_api function."""

    def test_format_text_for_api_success(self):
        """Test successful text formatting."""
        text = "   Valid text   "
        result = format_text_for_api(text, max_length=100)
        
        assert result == "Valid text"

    def test_format_text_for_api_too_long_error(self):
        """Test error when text is too long."""
        text = "a" * 9000
        
        with pytest.raises(ValueError) as exc_info:
            format_text_for_api(text, max_length=8000)
        
        assert "Cannot format text" in str(exc_info.value)

    def test_format_text_for_api_empty_error(self):
        """Test error when text is empty."""
        text = ""
        
        with pytest.raises(ValueError):
            format_text_for_api(text)

    def test_format_text_for_api_clean_whitespace(self):
        """Test cleaning whitespace."""
        text = "   Line1    Line2   "
        result = format_text_for_api(text)
        
        assert result == "Line1 Line2"

    def test_format_text_for_api_normalizes(self):
        """Test normalization."""
        text = "Para1\n\n\nPara2"
        result = format_text_for_api(text)
        
        assert "\n\n\n" not in result

