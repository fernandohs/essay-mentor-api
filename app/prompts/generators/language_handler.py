"""
Language handling for prompt generation.
Manages language detection, formatting, and validation.
"""
from typing import Optional
from app.core.config import settings
from .constants import SUPPORTED_LANGUAGES


class LanguageHandler:
    """Handles language operations for prompts."""
    
    def __init__(self):
        """Initialize language handler."""
        self.supported_languages = SUPPORTED_LANGUAGES
    
    def get_language_name(self, language_code: Optional[str] = None) -> str:
        """
        Get language name from language code.
        
        Args:
            language_code: Language code (en, es), defaults to config
            
        Returns:
            Language name in native format
        """
        if language_code is None:
            language_code = settings.DEFAULT_LANGUAGE
        
        return self.supported_languages.get(language_code, "English")
    
    def is_supported(self, language_code: str) -> bool:
        """
        Check if language code is supported.
        
        Args:
            language_code: Language code to check
            
        Returns:
            True if language is supported
        """
        return language_code in self.supported_languages
    
    def get_language_code(self, language: Optional[str] = None) -> str:
        """
        Get language code, defaulting to config if not provided.
        
        Args:
            language: Language code (en, es), defaults to config
            
        Returns:
            Language code
        """
        if language is None:
            return settings.DEFAULT_LANGUAGE
        return language
    
    def format_language_directive(self, language_code: Optional[str] = None) -> str:
        """
        Format language directive for prompts.
        
        Args:
            language_code: Language code (en, es), defaults to config
            
        Returns:
            Formatted language directive string
        """
        lang_name = self.get_language_name(language_code)
        lang_code = self.get_language_code(language_code)
        return f"ENGLISH language" if lang_code == "en" else f"{lang_name} language"
