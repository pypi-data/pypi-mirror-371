"""
Instruction Set Asset Type - Defines behavioral directives and guidelines.

Instruction sets provide specific behavioral modifications, guidelines, and
constraints that modify how an agent operates.
"""

from typing import Dict, Any, List
from .base import Asset, AssetType


class InstructionSet(Asset):
    """
    Instruction set asset defining behavioral modifications and guidelines.
    
    An instruction set defines:
    - Pre-analysis instructions
    - Specific behavioral constraints
    - Output format requirements
    - Quality and validation criteria
    - Processing workflows
    """
    
    @property
    def asset_type(self) -> AssetType:
        return AssetType.INSTRUCTION_SET
    
    def validate(self) -> List[str]:
        """Validate instruction set configuration."""
        errors = []
        
        # Check required sections
        required_sections = ['instructions']
        for section in required_sections:
            if section not in self.content:
                errors.append(f"Missing required section: {section}")
                continue
        
        instructions_config = self.content['instructions']
        
        # Validate review criteria if present
        if 'review_criteria' in instructions_config:
            criteria = instructions_config['review_criteria']
            if not isinstance(criteria, list):
                errors.append("review_criteria must be a list")
            else:
                for i, criterion in enumerate(criteria):
                    if not isinstance(criterion, dict):
                        errors.append(f"review_criteria[{i}] must be a dictionary")
                        continue
                    
                    if 'name' not in criterion:
                        errors.append(f"review_criteria[{i}] missing required 'name' field")
                    
                    if 'priority' in criterion:
                        valid_priorities = ['critical', 'high', 'medium', 'low']
                        if criterion['priority'] not in valid_priorities:
                            errors.append(f"review_criteria[{i}] invalid priority. Must be one of: {valid_priorities}")
        
        # Validate output format if present
        if 'output_format' in instructions_config:
            output_format = instructions_config['output_format']
            if 'severity_levels' in output_format:
                if not isinstance(output_format['severity_levels'], list):
                    errors.append("output_format.severity_levels must be a list")
        
        # Validate constraints if present
        if 'constraints' in instructions_config:
            constraints = instructions_config['constraints']
            if 'max_response_length' in constraints:
                try:
                    int(constraints['max_response_length'])
                except (ValueError, TypeError):
                    errors.append("constraints.max_response_length must be a number")
        
        return errors
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities this instruction set provides."""
        instructions_config = self.content.get('instructions', {})
        
        capabilities = {
            'type': 'behavioral_modification',
            'modifies_analysis': 'pre_analysis' in instructions_config,
            'modifies_output': 'output_format' in instructions_config,
            'adds_constraints': 'constraints' in instructions_config,
            'adds_criteria': 'review_criteria' in instructions_config
        }
        
        # Add specific capability flags
        if 'review_criteria' in instructions_config:
            criteria_names = [c.get('name', 'unknown') for c in instructions_config['review_criteria']]
            capabilities['review_types'] = criteria_names
        
        return capabilities
    
    def get_pre_analysis_instructions(self) -> List[str]:
        """
        Get pre-analysis instructions that should be applied before processing.
        
        Returns:
            List of instruction strings to apply before analysis.
        """
        instructions_config = self.content.get('instructions', {})
        return instructions_config.get('pre_analysis', [])
    
    def get_review_criteria(self) -> List[Dict[str, Any]]:
        """
        Get review criteria for evaluating outputs.
        
        Returns:
            List of review criteria with priorities and checks.
        """
        instructions_config = self.content.get('instructions', {})
        return instructions_config.get('review_criteria', [])
    
    def get_output_format(self) -> Dict[str, Any]:
        """
        Get output format requirements.
        
        Returns:
            Dictionary defining how outputs should be structured.
        """
        instructions_config = self.content.get('instructions', {})
        return instructions_config.get('output_format', {})
    
    def get_constraints(self) -> Dict[str, Any]:
        """
        Get processing constraints.
        
        Returns:
            Dictionary of constraints that limit or guide processing.
        """
        instructions_config = self.content.get('instructions', {})
        return instructions_config.get('constraints', {})
    
    def apply_to_prompt(self, base_prompt: str) -> str:
        """
        Apply instruction set to a base prompt.
        
        Args:
            base_prompt: The original prompt to modify
            
        Returns:
            Modified prompt with instructions applied
        """
        instructions_config = self.content.get('instructions', {})
        
        # Start with base prompt
        enhanced_prompt = base_prompt
        
        # Add pre-analysis instructions
        pre_analysis = self.get_pre_analysis_instructions()
        if pre_analysis:
            pre_analysis_text = '\n'.join([f"• {instruction}" for instruction in pre_analysis])
            enhanced_prompt = f"{enhanced_prompt}\n\nBefore responding, please:\n{pre_analysis_text}"
        
        # Add review criteria
        review_criteria = self.get_review_criteria()
        if review_criteria:
            criteria_text = []
            for criterion in review_criteria:
                name = criterion.get('name', 'Unknown')
                priority = criterion.get('priority', 'medium')
                checks = criterion.get('checks', [])
                
                criterion_text = f"• {name} ({priority} priority)"
                if checks:
                    checks_text = ', '.join(checks)
                    criterion_text += f": {checks_text}"
                
                criteria_text.append(criterion_text)
            
            if criteria_text:
                criteria_section = '\n'.join(criteria_text)
                enhanced_prompt = f"{enhanced_prompt}\n\nEvaluate your response against these criteria:\n{criteria_section}"
        
        # Add output format requirements
        output_format = self.get_output_format()
        if output_format:
            format_requirements = []
            
            if 'structure' in output_format:
                format_requirements.append(f"Structure: {output_format['structure']}")
            
            if 'severity_levels' in output_format:
                levels = ', '.join(output_format['severity_levels'])
                format_requirements.append(f"Use severity levels: {levels}")
            
            if 'include_examples' in output_format and output_format['include_examples']:
                format_requirements.append("Include concrete examples")
            
            if 'provide_fixes' in output_format and output_format['provide_fixes']:
                format_requirements.append("Provide specific fixes or solutions")
            
            if format_requirements:
                format_text = '\n'.join([f"• {req}" for req in format_requirements])
                enhanced_prompt = f"{enhanced_prompt}\n\nFormat your response with:\n{format_text}"
        
        # Add constraints
        constraints = self.get_constraints()
        if constraints:
            constraint_text = []
            
            if 'max_response_length' in constraints:
                constraint_text.append(f"Keep response under {constraints['max_response_length']} words")
            
            if 'min_detail_level' in constraints:
                constraint_text.append(f"Provide {constraints['min_detail_level']} level of detail")
            
            if 'required_sections' in constraints:
                sections = ', '.join(constraints['required_sections'])
                constraint_text.append(f"Include these sections: {sections}")
            
            if constraint_text:
                constraints_section = '\n'.join([f"• {constraint}" for constraint in constraint_text])
                enhanced_prompt = f"{enhanced_prompt}\n\nConstraints:\n{constraints_section}"
        
        return enhanced_prompt
    
    @classmethod
    def create_from_template(cls, name: str, template_type: str = 'code_review') -> 'InstructionSet':
        """
        Create an instruction set from a built-in template.
        
        Args:
            name: Name for the new instruction set
            template_type: Type of template (code_review, security_focused, performance_audit)
            
        Returns:
            New InstructionSet instance
        """
        templates = {
            'code_review': {
                'instructions': {
                    'pre_analysis': [
                        "Read through the entire code carefully",
                        "Identify the main purpose and functionality",
                        "Look for potential issues or improvements"
                    ],
                    'review_criteria': [
                        {
                            'name': 'Code Quality',
                            'priority': 'high',
                            'checks': ['readability', 'maintainability', 'structure']
                        },
                        {
                            'name': 'Best Practices',
                            'priority': 'high',
                            'checks': ['naming_conventions', 'error_handling', 'documentation']
                        },
                        {
                            'name': 'Performance',
                            'priority': 'medium',
                            'checks': ['efficiency', 'optimization_opportunities']
                        }
                    ],
                    'output_format': {
                        'structure': 'summary + detailed_findings + recommendations',
                        'severity_levels': ['critical', 'high', 'medium', 'low'],
                        'include_examples': True,
                        'provide_fixes': True
                    },
                    'constraints': {
                        'max_response_length': 2000,
                        'required_sections': ['quality', 'best_practices', 'recommendations']
                    }
                }
            },
            
            'security_focused': {
                'instructions': {
                    'pre_analysis': [
                        "Analyze code for security vulnerabilities first",
                        "Check for common attack vectors",
                        "Validate input handling and data flow"
                    ],
                    'review_criteria': [
                        {
                            'name': 'Security Vulnerabilities',
                            'priority': 'critical',
                            'checks': ['injection_attacks', 'xss', 'auth_bypass', 'data_exposure']
                        },
                        {
                            'name': 'Input Validation',
                            'priority': 'high',
                            'checks': ['sanitization', 'validation', 'encoding']
                        },
                        {
                            'name': 'Authentication & Authorization',
                            'priority': 'high',
                            'checks': ['access_control', 'session_management', 'privilege_escalation']
                        }
                    ],
                    'output_format': {
                        'structure': 'security_summary + vulnerability_details + mitigation_steps',
                        'severity_levels': ['critical', 'high', 'medium', 'low'],
                        'include_examples': True,
                        'provide_fixes': True
                    },
                    'constraints': {
                        'required_sections': ['vulnerabilities', 'mitigations', 'recommendations']
                    }
                }
            },
            
            'performance_audit': {
                'instructions': {
                    'pre_analysis': [
                        "Identify performance-critical sections",
                        "Look for algorithmic inefficiencies",
                        "Check resource usage patterns"
                    ],
                    'review_criteria': [
                        {
                            'name': 'Algorithmic Efficiency',
                            'priority': 'high',
                            'checks': ['time_complexity', 'space_complexity', 'algorithm_choice']
                        },
                        {
                            'name': 'Resource Usage',
                            'priority': 'high',
                            'checks': ['memory_leaks', 'cpu_usage', 'io_efficiency']
                        },
                        {
                            'name': 'Optimization Opportunities',
                            'priority': 'medium',
                            'checks': ['caching', 'batching', 'lazy_loading']
                        }
                    ],
                    'output_format': {
                        'structure': 'performance_summary + bottleneck_analysis + optimization_recommendations',
                        'severity_levels': ['critical', 'high', 'medium', 'low'],
                        'include_examples': True,
                        'provide_fixes': True
                    },
                    'constraints': {
                        'required_sections': ['performance_analysis', 'bottlenecks', 'optimizations']
                    }
                }
            }
        }
        
        if template_type not in templates:
            raise ValueError(f"Unknown template type: {template_type}")
        
        from .base import AssetMetadata
        metadata = AssetMetadata(
            name=name,
            id=name.lower().replace(' ', '-'),
            version='1.0.0',
            description=f"Instruction set created from {template_type} template",
            category='template',
            tags=[template_type, 'generated']
        )
        
        return cls(metadata, templates[template_type])