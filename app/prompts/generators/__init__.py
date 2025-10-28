"""
Prompt generation functions.
Main entry point for generating prompts for different use cases.
"""
from typing import List, Optional
from app.models.types import Section
from app.prompts.criteria_data import ESSAY_RUBRIC_CRITERIA, DEFAULT_CRITERIA

from .language_handler import LanguageHandler
from .section_definitions import SectionDefinitions
from .templates import PromptTemplates


class PromptGenerator:
    """Main prompt generator that orchestrates all components."""
    
    def __init__(self):
        """Initialize prompt generator."""
        self.language_handler = LanguageHandler()
        self.section_definitions = SectionDefinitions()
        self.templates = PromptTemplates()
    
    def generate_for_ai_detection(self, text: str, language: Optional[str] = None) -> str:
        """Generate prompt for AI likelihood detection."""
        lang_name = self.language_handler.get_language_name(language)
        return self.templates.get_ai_detection_template(text, lang_name)
    
    def generate_for_feedback(
        self,
        text: str,
        criteria: Optional[List[str]] = None,
        language: Optional[str] = None
    ) -> str:
        """Generate prompt for essay feedback generation."""
        lang_name = self.language_handler.get_language_name(language)
        
        # Use Extended Toulmin Model criteria
        used_criteria = criteria if criteria else DEFAULT_CRITERIA
        
        # Build criteria description
        criteria_descriptions = []
        for crit in used_criteria:
            crit_info = ESSAY_RUBRIC_CRITERIA.get(crit, {})
            desc = crit_info.get('description', '')
            max_pts = crit_info.get('maxPoints', 0)
            criteria_descriptions.append(
                f"- '{crit}': {desc} (valor máximo {max_pts} puntos)"
            )
        
        criteria_text = "\n      ".join(criteria_descriptions)
        return self.templates.get_feedback_template(text, criteria_text, lang_name)
    
    def generate_for_guidance(self, section: Section, language: Optional[str] = None) -> str:
        """Generate prompt for essay section guidance."""
        lang_name = self.language_handler.get_language_name(language)
        lang_code = self.language_handler.get_language_code(language)
        
        section_info = self.section_definitions.get_section_info(section)
        return self.templates.get_guidance_template(section, section_info, lang_name, lang_code)
    
    def generate_for_section_check(
        self,
        section: Section,
        text: str,
        language: Optional[str] = None
    ) -> str:
        """Generate prompt for checking and improving a specific essay section."""
        lang_name = self.language_handler.get_language_name(language)
        lang_code = self.language_handler.get_language_code(language)
        
        return self.templates.get_section_check_template(section, text, lang_name, lang_code)


# Global generator instance
_generator = None

def get_generator() -> PromptGenerator:
    """Get or create global prompt generator instance."""
    global _generator
    if _generator is None:
        _generator = PromptGenerator()
    return _generator


# Public functions for backward compatibility
def generate_prompt_for_ai_detection(text: str, language: Optional[str] = None) -> str:
    """Generate prompt for AI likelihood detection."""
    return get_generator().generate_for_ai_detection(text, language)


def generate_prompt_for_feedback(
    text: str,
    criteria: Optional[List[str]] = None,
    language: Optional[str] = None
) -> str:
    """Generate prompt for essay feedback generation."""
    return get_generator().generate_for_feedback(text, criteria, language)


def generate_prompt_for_guidance(section: Section, language: Optional[str] = None) -> str:
    """Generate prompt for essay section guidance."""
    return get_generator().generate_for_guidance(section, language)


def generate_prompt_for_section_check(
    section: Section,
    text: str,
    language: Optional[str] = None
) -> str:
    """Generate prompt for checking and improving a specific essay section."""
    return get_generator().generate_for_section_check(section, text, language)
