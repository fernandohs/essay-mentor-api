"""
Text Formatting Utilities

This module provides utilities for cleaning, formatting, and validating text
before processing in the API.
"""

import re
from typing import Optional
from .json_parse import clean_json_string


def normalize_text(text: str) -> str:
    """
    Normalize text by removing extra whitespace and cleaning common issues.
    
    Args:
        text: Raw text input
        
    Returns:
        Cleaned and normalized text
    """
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Normalize line breaks (handle different line ending types)
    text = re.sub(r'\r\n|\r', '\n', text)
    
    # Remove multiple consecutive line breaks (keep max 2 for paragraph breaks)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove multiple consecutive spaces
    text = re.sub(r'[ ]{2,}', ' ', text)
    
    return text.strip()


def escape_for_json(text: str) -> str:
    """
    Escape special characters for JSON encoding.
    
    Args:
        text: Text to escape
        
    Returns:
        Text with JSON-special characters escaped
    """
    # Replace problematic characters
    text = text.replace('\\', '\\\\')  # Backslash must be first
    text = text.replace('"', '\\"')    # Quotes
    text = text.replace('\n', '\\n')   # Newlines
    text = text.replace('\r', '\\r')   # Carriage returns
    text = text.replace('\t', '\\t')   # Tabs
    
    return text


def validate_text_length(text: str, max_length: int = 8000) -> tuple[bool, str]:
    """
    Validate text length and return status.
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, message)
    """
    length = len(text)
    
    if length > max_length:
        return False, f"Text exceeds maximum length of {max_length} characters (current: {length})"
    elif length == 0:
        return False, "Text is empty"
    else:
        return True, f"Text length: {length} characters (max: {max_length})"


def clean_and_validate_text(text: str, max_length: int = 8000) -> tuple[Optional[str], list[str]]:
    """
    Clean and validate text for API processing.
    
    Args:
        text: Raw text input
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (cleaned_text, list_of_issues)
    """
    issues = []
    
    # Normalize
    cleaned = normalize_text(text)
    
    # Check length
    is_valid, message = validate_text_length(cleaned, max_length)
    issues.append(message)
    
    if not is_valid:
        return None, issues
    
    # Detect and report potential issues
    if len(cleaned) < 100:
        issues.append("Warning: Text seems very short for an essay")
    
    # Check for common problematic patterns
    if re.search(r'[^\x20-\x7E\n\t]', cleaned):
        issues.append("Warning: Text contains non-ASCII characters")
    
    return cleaned, issues


def format_text_for_api(text: str, max_length: int = 8000) -> str:
    """
    Format text and prepare for API JSON payload.
    
    Args:
        text: Raw text input
        max_length: Maximum allowed length
        
    Returns:
        Cleaned and formatted text ready for API
        
    Raises:
        ValueError: If text cannot be formatted (too long, empty, etc.)
    """
    cleaned, issues = clean_and_validate_text(text, max_length)
    
    if cleaned is None:
        raise ValueError(f"Cannot format text: {', '.join(issues)}")
    
    # Return just the cleaned text for direct use in API
    return cleaned

