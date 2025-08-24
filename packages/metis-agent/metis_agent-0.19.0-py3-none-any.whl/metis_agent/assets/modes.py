"""
Chat Mode Asset Type - Defines interaction patterns and UI behavior.

Chat modes define how the agent interacts with users, including response timing,
interface features, and interaction workflows.
"""

from typing import Dict, Any, List
from .base import Asset, AssetType


class ChatMode(Asset):
    """
    Chat mode asset defining interaction patterns and UI behavior.
    
    A chat mode defines:
    - Interaction style and timing
    - UI features and settings
    - Workflow phases and actions
    - Keybindings and shortcuts
    - Memory and context settings
    """
    
    @property
    def asset_type(self) -> AssetType:
        return AssetType.CHAT_MODE
    
    def validate(self) -> List[str]:
        """Validate chat mode configuration."""
        errors = []
        
        # Check required sections
        required_sections = ['mode_config']
        for section in required_sections:
            if section not in self.content:
                errors.append(f"Missing required section: {section}")
        
        # TODO: Add specific validation for chat modes
        
        return errors
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities this chat mode provides."""
        mode_config = self.content.get('mode_config', {})
        
        return {
            'interaction_style': mode_config.get('interaction_style', 'standard'),
            'features': mode_config.get('features', {}),
            'ui_settings': mode_config.get('ui_settings', {}),
            'workflow_phases': len(mode_config.get('workflow', [])),
            'keybindings': len(mode_config.get('keybindings', {}))
        }