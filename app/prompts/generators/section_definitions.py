"""
Section definitions for Toulmin model essay sections.
Provides metadata and descriptions for different essay sections.
"""
from typing import Dict, Any
from app.models.types import Section


class SectionDefinitions:
    """Manages section definitions and metadata."""
    
    def __init__(self):
        """Initialize section definitions."""
        self.sections: Dict[str, Dict[str, Any]] = {
            "claim": {
                "description": "The main argument or thesis statement",
                "purpose": "Present the central argument that the essay will defend",
                "key_elements": ["clarity", "debatability", "specificity", "strength"]
            },
            "reasoning": {
                "description": "The logical justification for the claim",
                "purpose": "Explain why the claim is valid through logical reasoning",
                "key_elements": ["logical flow", "coherence", "connection to claim"]
            },
            "evidence": {
                "description": "Facts, data, examples that support the reasoning",
                "purpose": "Provide concrete support for the reasoning through facts and examples",
                "key_elements": ["relevance", "credibility", "specificity", "variety"]
            },
            "backing": {
                "description": "Additional support or authority that reinforces the claim",
                "purpose": "Strengthen the argument with additional context or authority",
                "key_elements": ["authority", "context", "reinforcement"]
            },
            "reservation": {
                "description": "Limitations or conditions that acknowledge counter-arguments",
                "purpose": "Show awareness of limitations and strengthen credibility",
                "key_elements": ["honesty", "self-awareness", "scope definition"]
            },
            "rebuttal": {
                "description": "Response to counter-arguments or objections",
                "purpose": "Address potential opposing viewpoints and strengthen the argument",
                "key_elements": ["anticipation", "response", "refutation"]
            }
        }
    
    def get_section_info(self, section: Section) -> Dict[str, Any]:
        """
        Get information about a specific section.
        
        Args:
            section: Section to get info for
            
        Returns:
            Dictionary with section information
        """
        return self.sections.get(section, self.sections["claim"])
    
    def get_description(self, section: Section) -> str:
        """Get description for a section."""
        return self.get_section_info(section).get("description", "")
    
    def get_purpose(self, section: Section) -> str:
        """Get purpose for a section."""
        return self.get_section_info(section).get("purpose", "")
    
    def get_key_elements(self, section: Section) -> list:
        """Get key elements for a section."""
        return self.get_section_info(section).get("key_elements", [])
    
    def is_valid_section(self, section: Section) -> bool:
        """Check if section is valid."""
        return section in self.sections
