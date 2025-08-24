"""
Metis Asset System - First-class composable assets.

This module provides the foundation for personas, instruction sets, chat modes, 
workflows, and skills as composable assets.
"""

from .base import Asset, AssetType, AssetRegistry, AssetComposer, get_asset_registry
from .personas import Persona
from .instructions import InstructionSet
from .modes import ChatMode
from .workflows import Workflow
from .skills import Skill
from .compositions import Composition

__all__ = [
    'Asset',
    'AssetType', 
    'AssetRegistry',
    'AssetComposer',
    'get_asset_registry',
    'Persona',
    'InstructionSet',
    'ChatMode',
    'Workflow',
    'Skill',
    'Composition'
]