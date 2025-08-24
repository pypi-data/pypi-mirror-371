"""
Workflow Asset Type - Defines executable multi-step processes.

Workflows define repeatable, multi-step processes that can be executed
with parameters and validation.
"""

from typing import Dict, Any, List
from .base import Asset, AssetType


class Workflow(Asset):
    """
    Workflow asset defining executable multi-step processes.
    
    A workflow defines:
    - Metadata and parameters
    - Sequential steps with actions
    - Validation and conditions
    - Post-execution actions
    """
    
    @property
    def asset_type(self) -> AssetType:
        return AssetType.WORKFLOW
    
    def validate(self) -> List[str]:
        """Validate workflow configuration."""
        errors = []
        
        # Check required sections
        required_sections = ['workflow']
        for section in required_sections:
            if section not in self.content:
                errors.append(f"Missing required section: {section}")
        
        # TODO: Add specific validation for workflows
        
        return errors
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities this workflow provides."""
        workflow_config = self.content.get('workflow', {})
        
        return {
            'step_count': len(workflow_config.get('steps', [])),
            'has_parameters': 'parameters' in workflow_config,
            'has_validation': 'validation' in workflow_config,
            'estimated_time': workflow_config.get('metadata', {}).get('estimated_time', 'unknown'),
            'complexity': workflow_config.get('metadata', {}).get('complexity', 'unknown')
        }