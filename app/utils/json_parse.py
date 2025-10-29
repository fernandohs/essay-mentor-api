import json
import re
from typing import Any, Dict, Optional


def clean_json_string(json_str: str) -> str:
    """
    Clean JSON string from common formatting issues.
    Removes markdown code fences, extra whitespace, and fixes common issues.
    
    Args:
        json_str: Raw JSON string that may contain formatting issues
        
    Returns:
        Cleaned JSON string ready for parsing
    """
    # Remove markdown code fences
    json_str = re.sub(r'```json\s*', '', json_str)
    json_str = re.sub(r'```\s*$', '', json_str, flags=re.MULTILINE)
    
    # Remove leading/trailing whitespace
    json_str = json_str.strip()
    
    # Remove any remaining code fences
    json_str = json_str.strip('`')
    
    return json_str


def extract_json_from_text(raw_text: str) -> Optional[str]:
    """
    Extract JSON content from text that may contain surrounding text or markdown.
    
    Args:
        raw_text: Text that may contain JSON within markdown or other content
        
    Returns:
        Extracted JSON string, or None if not found
    """
    # Try to find JSON in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', raw_text, re.DOTALL)
    if json_match:
        return clean_json_string(json_match.group(1))
    
    # Try to find JSON object or array directly
    json_match = re.search(r'(\{.*\}|\[.*\])', raw_text, re.DOTALL)
    if json_match:
        return clean_json_string(json_match.group(1))
    
    return None


def extract_valid_json_from_truncated(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract valid JSON from truncated text by progressively removing incomplete fields.
    
    Args:
        text: Potentially truncated JSON text
        
    Returns:
        Parsed JSON dict if possible, None otherwise
    """
    # Try to parse progressively smaller chunks
    # Look for the opening brace and try to find a valid closing brace
    start_idx = text.find('{')
    if start_idx == -1:
        return None
    
    # Try to find matching closing brace
    depth = 0
    last_valid_pos = -1
    
    for i in range(start_idx, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                last_valid_pos = i
                break
    
    # If we found a complete JSON object, try to parse it
    if last_valid_pos > 0:
        json_str = text[start_idx:last_valid_pos + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try to manually close the JSON by removing trailing incomplete fields
    # Look for the last complete field (ends with } or , followed by key)
    for match in re.finditer(r'"\s*:\s*[^,}]+,', text[start_idx:]):
        # Get text up to this point and close it
        potential_json = text[start_idx:start_idx + match.end() - 1] + '}'
        try:
            return json.loads(potential_json)
        except json.JSONDecodeError:
            continue
    
    return None


def safe_json_parse(text: str) -> Dict[str, Any]:
    """
    Safely parse JSON from text with multiple fallback strategies.
    
    This function tries several strategies to parse JSON:
    1. Direct parsing
    2. Extracting JSON from markdown
    3. Cleaning and parsing
    4. Finding first JSON object/array in text
    
    Args:
        text: Text containing JSON
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        ValueError: If JSON cannot be parsed after all attempts
        json.JSONDecodeError: If all parsing attempts fail
    """
    # Strategy 1: Try direct parsing
    cleaned = text.strip()
    try:
        parsed = json.loads(cleaned)
        # If it's a list, wrap it in a dict or return error
        if isinstance(parsed, list):
            # If it's a list, try to use first element if it's a dict
            if len(parsed) > 0 and isinstance(parsed[0], dict):
                return parsed[0]
            # If it's a list of strings or other types, wrap it
            # This handles cases where LLM returns something like ["response"]
            if len(parsed) == 1 and isinstance(parsed[0], str):
                # Try to parse the string as JSON
                try:
                    inner_json = json.loads(parsed[0])
                    if isinstance(inner_json, dict):
                        return inner_json
                except (json.JSONDecodeError, TypeError):
                    pass
            # Debug: log what we got
            print(f"DEBUG: Got a list with {len(parsed)} items")
            if len(parsed) > 0:
                print(f"DEBUG: First item type: {type(parsed[0])}")
                print(f"DEBUG: First item: {parsed[0]}")
            raise ValueError(f"Parsed JSON is a list (length {len(parsed)}), expected dict. First item type: {type(parsed[0]).__name__ if parsed else 'empty list'}")
        return parsed
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Try extracting JSON from text
    extracted = extract_json_from_text(text)
    if extracted:
        try:
            parsed = json.loads(extracted)
            if isinstance(parsed, list):
                if len(parsed) > 0 and isinstance(parsed[0], dict):
                    return parsed[0]
                raise ValueError("Parsed JSON is a list, expected dict")
            return parsed
        except json.JSONDecodeError:
            pass
    
    # Strategy 3: Clean and try again
    try:
        cleaned_json = clean_json_string(text)
        parsed = json.loads(cleaned_json)
        if isinstance(parsed, list):
            if len(parsed) > 0 and isinstance(parsed[0], dict):
                return parsed[0]
            raise ValueError("Parsed JSON is a list, expected dict")
        return parsed
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Strategy 4: Find JSON object or array boundaries and extract
    # Look for first { or [ and find matching } or ]
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start_idx = text.find(start_char)
        if start_idx != -1:
            depth = 0
            for i in range(start_idx, len(text)):
                if text[i] == start_char:
                    depth += 1
                elif text[i] == end_char:
                    depth -= 1
                    if depth == 0:
                        json_str = text[start_idx:i+1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            break
    
    # Strategy 5: Try to extract valid JSON from potentially truncated text
    truncated_json = extract_valid_json_from_truncated(text)
    if truncated_json:
        return truncated_json
    
    # All strategies failed
    raise ValueError(f"Could not parse JSON from text: {text[:200]}...")


def parse_ollama_streaming_response(response_lines: list[str]) -> str:
    """
    Parse Ollama streaming response chunks and extract the full text.
    
    Args:
        response_lines: List of lines from Ollama streaming response
        
    Returns:
        Complete text output from the LLM
    """
    full_output = ""
    for line in response_lines:
        if not line:
            continue
        try:
            chunk_data = json.loads(line.decode("utf-8") if isinstance(line, bytes) else line)
            if "response" in chunk_data:
                full_output += chunk_data["response"]
        except (json.JSONDecodeError, KeyError, AttributeError):
            continue
    
    return full_output.strip()

