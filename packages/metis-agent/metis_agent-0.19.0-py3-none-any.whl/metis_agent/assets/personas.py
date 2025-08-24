"""
Persona Asset Type - Defines agent character and behavior.

Personas encapsulate who the agent is, how it communicates, and its areas of expertise.
"""

from typing import Dict, Any, List
from .base import Asset, AssetType


class Persona(Asset):
    """
    Persona asset defining agent identity, behavior, and expertise.
    
    A persona defines:
    - Agent identity and role
    - Communication style and personality
    - Areas of expertise and knowledge domains
    - Response patterns and behavior traits
    """
    
    @property
    def asset_type(self) -> AssetType:
        return AssetType.PERSONA
    
    def validate(self) -> List[str]:
        """Validate persona configuration."""
        errors = []
        
        # Check required sections
        required_sections = ['persona']
        for section in required_sections:
            if section not in self.content:
                errors.append(f"Missing required section: {section}")
                continue
        
        persona_config = self.content.get('persona', {})
        
        # Validate identity section
        if 'identity' not in persona_config:
            errors.append("Missing persona.identity section")
        else:
            identity = persona_config['identity']
            if 'role' not in identity:
                errors.append("Missing persona.identity.role")
        
        # Validate behavior section
        if 'behavior' in persona_config:
            behavior = persona_config['behavior']
            valid_communication_styles = [
                'technical_precise', 'conversational', 'formal', 'casual', 
                'academic', 'creative', 'concise', 'detailed'
            ]
            
            if 'communication_style' in behavior:
                if behavior['communication_style'] not in valid_communication_styles:
                    errors.append(f"Invalid communication_style. Must be one of: {valid_communication_styles}")
        
        # Validate capabilities if present
        if 'capabilities' in self.content:
            capabilities = self.content['capabilities']
            if not isinstance(capabilities, list):
                errors.append("capabilities must be a list")
        
        return errors
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities this persona provides."""
        persona_config = self.content.get('persona', {})
        
        return {
            'role': persona_config.get('identity', {}).get('role', 'Unknown'),
            'expertise': persona_config.get('identity', {}).get('expertise', []),
            'knowledge_domains': persona_config.get('knowledge_domains', []),
            'capabilities': self.content.get('capabilities', []),
            'communication_style': persona_config.get('behavior', {}).get('communication_style', 'conversational')
        }
    
    def get_system_message(self) -> str:
        """
        Generate system message from persona configuration.
        
        Returns:
            System message string that defines the agent's identity and behavior.
        """
        persona_config = self.content.get('persona', {})
        identity = persona_config.get('identity', {})
        behavior = persona_config.get('behavior', {})
        
        # Build system message
        parts = []
        
        # Role and identity
        role = identity.get('role', 'AI Assistant')
        parts.append(f"You are a {role}.")
        
        # Expertise areas
        expertise = identity.get('expertise', [])
        if expertise:
            expertise_str = ', '.join(expertise)
            parts.append(f"Your areas of expertise include: {expertise_str}.")
        
        # Personality and communication style
        personality = identity.get('personality', {})
        if 'tone' in personality:
            parts.append(f"Your communication tone is {personality['tone']}.")
        
        if 'style' in personality:
            parts.append(f"Your communication style is {personality['style']}.")
        
        # Behavior traits
        traits = personality.get('traits', [])
        if traits:
            traits_str = ', '.join(traits)
            parts.append(f"Your key traits are: {traits_str}.")
        
        # Response patterns
        response_patterns = persona_config.get('response_patterns', {})
        if 'greeting' in response_patterns:
            parts.append(f"When greeting users, you typically say: '{response_patterns['greeting']}'")
        
        if 'problem_solving' in behavior:
            parts.append(f"Your problem-solving approach is {behavior['problem_solving']}.")
        
        # Knowledge domains
        knowledge_domains = persona_config.get('knowledge_domains', [])
        if knowledge_domains:
            domains_str = ', '.join(knowledge_domains)
            parts.append(f"Your knowledge spans: {domains_str}.")
        
        # Join all parts into system message
        system_message = ' '.join(parts)
        
        return system_message
    
    def get_response_modifiers(self) -> Dict[str, Any]:
        """
        Get response modification settings for this persona.
        
        Returns:
            Dictionary of settings that modify how the agent responds.
        """
        persona_config = self.content.get('persona', {})
        behavior = persona_config.get('behavior', {})
        
        return {
            'communication_style': behavior.get('communication_style', 'conversational'),
            'decision_making': behavior.get('decision_making', 'balanced'),
            'problem_solving': behavior.get('problem_solving', 'systematic'),
            'teaching_approach': behavior.get('teaching_approach', 'explanatory'),
            'response_length': behavior.get('response_length', 'appropriate'),
            'technical_depth': behavior.get('technical_depth', 'adaptive')
        }
    
    @classmethod
    def create_from_template(cls, name: str, template_type: str = 'expert') -> 'Persona':
        """
        Create a persona from a built-in template.
        
        Args:
            name: Name for the new persona
            template_type: Type of template (expert, beginner, specialist, mentor)
            
        Returns:
            New Persona instance
        """
        templates = {
            'expert': {
                'persona': {
                    'identity': {
                        'role': 'Expert Consultant',
                        'expertise': ['Problem Solving', 'Strategic Thinking', 'Technical Analysis'],
                        'personality': {
                            'tone': 'Professional and knowledgeable',
                            'style': 'Direct and solution-focused',
                            'traits': ['analytical', 'thorough', 'experienced']
                        }
                    },
                    'behavior': {
                        'communication_style': 'technical_precise',
                        'decision_making': 'evidence_based',
                        'problem_solving': 'systematic_analysis',
                        'teaching_approach': 'comprehensive_explanation'
                    },
                    'knowledge_domains': ['general_expertise'],
                    'response_patterns': {
                        'greeting': 'I\'m here to provide expert guidance and analysis.',
                        'question_handling': 'Let me analyze this systematically...',
                        'problem_solving': 'I\'ll break this down into key components...'
                    }
                },
                'capabilities': [
                    'expert_analysis',
                    'strategic_planning',
                    'comprehensive_research',
                    'detailed_explanations'
                ]
            },
            
            'mentor': {
                'persona': {
                    'identity': {
                        'role': 'Mentor and Guide',
                        'expertise': ['Teaching', 'Mentoring', 'Skill Development'],
                        'personality': {
                            'tone': 'Encouraging and supportive',
                            'style': 'Patient and instructive',
                            'traits': ['patient', 'encouraging', 'wise']
                        }
                    },
                    'behavior': {
                        'communication_style': 'conversational',
                        'decision_making': 'collaborative',
                        'problem_solving': 'guided_discovery',
                        'teaching_approach': 'socratic_method'
                    },
                    'knowledge_domains': ['education', 'skill_development'],
                    'response_patterns': {
                        'greeting': 'I\'m excited to help you learn and grow!',
                        'question_handling': 'That\'s a great question! Let\'s explore this together...',
                        'problem_solving': 'What do you think might be the first step here?'
                    }
                },
                'capabilities': [
                    'guided_learning',
                    'skill_assessment',
                    'personalized_instruction',
                    'encouraging_feedback'
                ]
            },
            
            'specialist': {
                'persona': {
                    'identity': {
                        'role': 'Domain Specialist',
                        'expertise': ['Specialized Knowledge', 'Deep Technical Understanding'],
                        'personality': {
                            'tone': 'Knowledgeable and precise',
                            'style': 'Detail-oriented and thorough',
                            'traits': ['meticulous', 'specialized', 'authoritative']
                        }
                    },
                    'behavior': {
                        'communication_style': 'technical_precise',
                        'decision_making': 'data_driven',
                        'problem_solving': 'domain_specific_analysis',
                        'teaching_approach': 'detailed_explanation'
                    },
                    'knowledge_domains': ['specialized_domain'],
                    'response_patterns': {
                        'greeting': 'I\'m here to provide specialized expertise in this domain.',
                        'question_handling': 'From a technical perspective...',
                        'problem_solving': 'Based on domain-specific principles...'
                    }
                },
                'capabilities': [
                    'domain_expertise',
                    'technical_analysis',
                    'specialized_problem_solving',
                    'authoritative_guidance'
                ]
            }
        }
        
        if template_type not in templates:
            raise ValueError(f"Unknown template type: {template_type}")
        
        from .base import AssetMetadata
        metadata = AssetMetadata(
            name=name,
            id=name.lower().replace(' ', '-'),
            version='1.0.0',
            description=f"Persona created from {template_type} template",
            category='template',
            tags=[template_type, 'generated']
        )
        
        return cls(metadata, templates[template_type])