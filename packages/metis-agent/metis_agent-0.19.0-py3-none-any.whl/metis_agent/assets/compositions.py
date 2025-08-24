"""
Composition Asset Type - Defines saved combinations of other assets.

Compositions allow saving and reusing specific combinations of personas,
instruction sets, modes, workflows, and skills.
"""

from typing import Dict, Any, List
from .base import Asset, AssetType


class Composition(Asset):
    """
    Composition asset defining saved combinations of other assets.
    
    A composition defines:
    - Referenced assets by type and ID
    - Composition-specific overrides
    - Usage documentation and examples
    """
    
    @property
    def asset_type(self) -> AssetType:
        return AssetType.COMPOSITION
    
    def validate(self) -> List[str]:
        """Validate composition configuration."""
        errors = []
        
        # Check required sections
        required_sections = ['composition']
        for section in required_sections:
            if section not in self.content:
                errors.append(f"Missing required section: {section}")
        
        # TODO: Add specific validation for compositions
        
        return errors
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities this composition provides."""
        composition_config = self.content.get('composition', {})
        assets = composition_config.get('assets', {})
        
        return {
            'asset_count': sum(len(v) if isinstance(v, list) else 1 for v in assets.values()),
            'asset_types': list(assets.keys()),
            'has_overrides': 'overrides' in composition_config,
            'complexity': composition_config.get('metadata', {}).get('complexity', 'simple')
        }