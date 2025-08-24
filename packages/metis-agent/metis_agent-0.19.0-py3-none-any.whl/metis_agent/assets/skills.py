"""
Skill Asset Type - Defines reusable capabilities and expertise areas.

Skills define specific capabilities that can be attached to any agent
configuration to provide domain expertise.
"""

from typing import Dict, Any, List
from .base import Asset, AssetType


class Skill(Asset):
    """
    Skill asset defining reusable capabilities and expertise.
    
    A skill defines:
    - Domain expertise and capabilities
    - Knowledge base and standards
    - Response templates and patterns
    - Tool integrations and commands
    """
    
    @property
    def asset_type(self) -> AssetType:
        return AssetType.SKILL
    
    def validate(self) -> List[str]:
        """Validate skill configuration."""
        errors = []
        
        # Check required sections
        required_sections = ['skill_definition']
        for section in required_sections:
            if section not in self.content:
                errors.append(f"Missing required section: {section}")
        
        # TODO: Add specific validation for skills
        
        return errors
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities this skill provides."""
        skill_config = self.content.get('skill_definition', {})
        
        return {
            'domain': skill_config.get('domain', 'general'),
            'expertise_level': skill_config.get('expertise_level', 'intermediate'),
            'capabilities': skill_config.get('capabilities', []),
            'tools_required': self.content.get('tools_integration', {}).get('required', []),
            'knowledge_areas': len(skill_config.get('knowledge_base', {}))
        }