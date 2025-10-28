"""
Constants for prompt generation.
Contains educational rules and configuration constants.
"""

# Educational rule to prevent LLM from doing student's work
EDUCATIONAL_RULE = """
CRITICAL: You are an educational assistant helping students learn. 
- NEVER generate complete essays, sentences, or paragraphs for the student.
- Your role is to GUIDE and PROVIDE FEEDBACK, not to write their content.
- Suggest improvements and ask questions, but let the student write their own work.
"""

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Español"
}

# Default language
DEFAULT_LANGUAGE = "en"
