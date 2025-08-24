"""
Base classes for the Metis Asset System.

Provides foundation for all composable assets including validation, 
loading, and composition capabilities.
"""

import os
import yaml
import json
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Union, Set
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AssetType(Enum):
    """Types of composable assets in Metis."""
    PERSONA = "persona"
    INSTRUCTION_SET = "instructions"
    CHAT_MODE = "mode" 
    WORKFLOW = "workflow"
    SKILL = "skill"
    COMPOSITION = "composition"


@dataclass
class AssetMetadata:
    """Metadata for all assets."""
    name: str
    id: str
    version: str
    author: str = "unknown"
    description: str = ""
    category: str = "general"
    tags: List[str] = None
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class Asset(ABC):
    """
    Base class for all composable assets.
    
    All assets (personas, instructions, modes, workflows, skills) inherit from this.
    """
    
    def __init__(self, metadata: AssetMetadata, content: Dict[str, Any]):
        self.metadata = metadata
        self.content = content
        self._validated = False
        
    @property 
    @abstractmethod
    def asset_type(self) -> AssetType:
        """Return the type of this asset."""
        pass
        
    @abstractmethod
    def validate(self) -> List[str]:
        """
        Validate the asset configuration.
        
        Returns:
            List of validation error messages. Empty list if valid.
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities this asset provides.
        
        Returns:
            Dictionary describing what this asset can do.
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert asset to dictionary representation."""
        return {
            'metadata': asdict(self.metadata),
            'content': self.content,
            'type': self.asset_type.value
        }
    
    def save(self, path: Path) -> None:
        """Save asset to YAML file."""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
    
    @classmethod
    def load(cls, path: Path) -> 'Asset':
        """Load asset from YAML file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        metadata = AssetMetadata(**data['metadata'])
        content = data['content']
        
        # Create appropriate asset subclass
        asset_type = AssetType(data['type'])
        
        if asset_type == AssetType.PERSONA:
            from .personas import Persona
            return Persona(metadata, content)
        elif asset_type == AssetType.INSTRUCTION_SET:
            from .instructions import InstructionSet
            return InstructionSet(metadata, content)
        elif asset_type == AssetType.CHAT_MODE:
            from .modes import ChatMode
            return ChatMode(metadata, content)
        elif asset_type == AssetType.WORKFLOW:
            from .workflows import Workflow
            return Workflow(metadata, content)
        elif asset_type == AssetType.SKILL:
            from .skills import Skill
            return Skill(metadata, content)
        elif asset_type == AssetType.COMPOSITION:
            from .compositions import Composition
            return Composition(metadata, content)
        else:
            raise ValueError(f"Unknown asset type: {asset_type}")
    
    def get_hash(self) -> str:
        """Get content hash for versioning and caching."""
        content_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]


class AssetRegistry:
    """
    Registry for discovering, loading, and managing assets.
    
    Handles asset discovery across multiple directories and provides
    caching and indexing capabilities.
    """
    
    def __init__(self, base_paths: List[Path] = None):
        """
        Initialize asset registry.
        
        Args:
            base_paths: List of directories to search for assets.
                       If None, uses default paths.
        """
        if base_paths is None:
            home = Path.home()
            base_paths = [
                home / '.metis' / 'assets',
                Path(__file__).parent / 'builtin_assets'
            ]
        
        self.base_paths = base_paths
        self._cache: Dict[str, Asset] = {}
        self._index: Dict[AssetType, Dict[str, Path]] = {
            asset_type: {} for asset_type in AssetType
        }
        self._build_index()
    
    def _build_index(self) -> None:
        """Build index of all available assets."""
        logger.info("Building asset index...")
        
        for base_path in self.base_paths:
            if not base_path.exists():
                logger.debug(f"Asset path does not exist: {base_path}")
                continue
                
            for asset_type in AssetType:
                type_dir = base_path / (asset_type.value + 's')  # personas, instructions, etc.
                if type_dir.exists():
                    for asset_file in type_dir.glob('*.yaml'):
                        try:
                            # Extract asset ID from filename
                            asset_id = asset_file.stem
                            self._index[asset_type][asset_id] = asset_file
                            logger.debug(f"Indexed {asset_type.value}: {asset_id}")
                        except Exception as e:
                            logger.warning(f"Failed to index {asset_file}: {e}")
        
        logger.info(f"Asset index built: {sum(len(assets) for assets in self._index.values())} assets")
    
    def list_assets(self, asset_type: AssetType = None) -> Dict[AssetType, List[str]]:
        """
        List all available assets.
        
        Args:
            asset_type: If specified, only return assets of this type.
            
        Returns:
            Dictionary mapping asset types to lists of asset IDs.
        """
        if asset_type:
            return {asset_type: list(self._index[asset_type].keys())}
        else:
            return {
                asset_type: list(asset_ids.keys()) 
                for asset_type, asset_ids in self._index.items()
            }
    
    def get_asset(self, asset_type: AssetType, asset_id: str) -> Optional[Asset]:
        """
        Load and return an asset.
        
        Args:
            asset_type: Type of asset to load
            asset_id: ID of the asset
            
        Returns:
            Asset instance or None if not found
        """
        cache_key = f"{asset_type.value}:{asset_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Find asset path
        if asset_id not in self._index[asset_type]:
            logger.warning(f"Asset not found: {asset_type.value}:{asset_id}")
            return None
        
        asset_path = self._index[asset_type][asset_id]
        
        try:
            asset = Asset.load(asset_path)
            self._cache[cache_key] = asset
            return asset
        except Exception as e:
            logger.error(f"Failed to load asset {cache_key}: {e}")
            return None
    
    def search_assets(self, query: str, asset_type: AssetType = None) -> List[Asset]:
        """
        Search for assets by name, description, or tags.
        
        Args:
            query: Search query
            asset_type: Optionally filter by asset type
            
        Returns:
            List of matching assets
        """
        results = []
        query_lower = query.lower()
        
        asset_types = [asset_type] if asset_type else list(AssetType)
        
        for atype in asset_types:
            for asset_id in self._index[atype]:
                asset = self.get_asset(atype, asset_id)
                if asset:
                    # Search in name, description, and tags
                    searchable = [
                        asset.metadata.name.lower(),
                        asset.metadata.description.lower(),
                        asset.metadata.category.lower()
                    ] + [tag.lower() for tag in asset.metadata.tags]
                    
                    if any(query_lower in text for text in searchable):
                        results.append(asset)
        
        return results
    
    def validate_asset(self, asset_type: AssetType, asset_id: str) -> List[str]:
        """
        Validate an asset and return any errors.
        
        Args:
            asset_type: Type of asset
            asset_id: ID of asset to validate
            
        Returns:
            List of validation errors
        """
        asset = self.get_asset(asset_type, asset_id)
        if not asset:
            return [f"Asset not found: {asset_type.value}:{asset_id}"]
        
        return asset.validate()
    
    def refresh(self) -> None:
        """Refresh the asset index and clear cache."""
        self._cache.clear()
        self._index = {asset_type: {} for asset_type in AssetType}
        self._build_index()


class ComposedAgent:
    """
    Represents an agent composed of multiple assets.
    
    This class handles merging multiple assets into a unified configuration
    that can be used to create an agent instance.
    """
    
    def __init__(self):
        self.personas: List[Asset] = []
        self.instruction_sets: List[Asset] = []
        self.chat_modes: List[Asset] = []
        self.workflows: List[Asset] = []
        self.skills: List[Asset] = []
        self.compositions: List[Asset] = []
        
    def add_asset(self, asset: Asset) -> None:
        """Add an asset to this composition."""
        if asset.asset_type == AssetType.PERSONA:
            self.personas.append(asset)
        elif asset.asset_type == AssetType.INSTRUCTION_SET:
            self.instruction_sets.append(asset)
        elif asset.asset_type == AssetType.CHAT_MODE:
            self.chat_modes.append(asset)
        elif asset.asset_type == AssetType.WORKFLOW:
            self.workflows.append(asset)
        elif asset.asset_type == AssetType.SKILL:
            self.skills.append(asset)
        elif asset.asset_type == AssetType.COMPOSITION:
            # Expand composition into constituent assets
            self._expand_composition(asset)
    
    def _expand_composition(self, composition: Asset) -> None:
        """Expand a composition asset into its constituent assets."""
        # This would load the referenced assets from the composition
        # and add them to the appropriate lists
        pass  # TODO: Implement composition expansion
    
    def validate(self) -> List[str]:
        """Validate the composed agent configuration."""
        errors = []
        
        # Validate individual assets
        for asset_list in [self.personas, self.instruction_sets, self.chat_modes, self.workflows, self.skills]:
            for asset in asset_list:
                asset_errors = asset.validate()
                errors.extend([f"{asset.metadata.name}: {error}" for error in asset_errors])
        
        # Check for conflicts
        if len(self.chat_modes) > 1:
            errors.append("Multiple chat modes specified - only one is supported")
        
        # Validate compatibility
        # TODO: Add compatibility checking between different asset types
        
        return errors
    
    def build_agent_config(self) -> Dict[str, Any]:
        """
        Build unified agent configuration from all assets.
        
        Returns:
            Dictionary containing merged configuration for agent creation.
        """
        config = {
            'personas': [asset.content for asset in self.personas],
            'instruction_sets': [asset.content for asset in self.instruction_sets],
            'chat_mode': self.chat_modes[0].content if self.chat_modes else None,
            'workflows': [asset.content for asset in self.workflows],
            'skills': [asset.content for asset in self.skills]
        }
        
        return config


class AssetComposer:
    """
    Composer for creating unified agent configurations from multiple assets.
    """
    
    def __init__(self, registry: AssetRegistry):
        self.registry = registry
    
    def compose(self, asset_specs: List[str]) -> ComposedAgent:
        """
        Compose assets into unified configuration.
        
        Args:
            asset_specs: List of asset specifications like:
                        ["persona:senior-dev", "instructions:code-review+security", 
                         "mode:pair-programming", "skills:api-testing"]
        
        Returns:
            ComposedAgent instance ready for validation and use
        """
        composition = ComposedAgent()
        
        for spec in asset_specs:
            if ':' not in spec:
                raise ValueError(f"Invalid asset spec format: {spec}. Expected 'type:name' or 'type:name+name2'")
            
            asset_type_str, asset_names = spec.split(':', 1)
            
            try:
                asset_type = AssetType(asset_type_str)
            except ValueError:
                raise ValueError(f"Unknown asset type: {asset_type_str}")
            
            # Handle multiple assets (e.g., "name1+name2+name3")
            for asset_name in asset_names.split('+'):
                asset_name = asset_name.strip()
                asset = self.registry.get_asset(asset_type, asset_name)
                
                if not asset:
                    raise ValueError(f"Asset not found: {asset_type.value}:{asset_name}")
                
                composition.add_asset(asset)
        
        return composition
    
    def compose_from_file(self, composition_path: Path) -> ComposedAgent:
        """
        Load composition from a saved composition file.
        
        Args:
            composition_path: Path to composition YAML file
            
        Returns:
            ComposedAgent instance
        """
        with open(composition_path, 'r', encoding='utf-8') as f:
            composition_data = yaml.safe_load(f)
        
        # Convert composition data to asset specs
        asset_specs = []
        for asset_type, asset_names in composition_data.get('assets', {}).items():
            if isinstance(asset_names, list):
                asset_specs.append(f"{asset_type}:{'+'.join(asset_names)}")
            else:
                asset_specs.append(f"{asset_type}:{asset_names}")
        
        return self.compose(asset_specs)


# Global asset registry instance
_registry = None

def get_asset_registry() -> AssetRegistry:
    """Get the global asset registry instance."""
    global _registry
    if _registry is None:
        _registry = AssetRegistry()
    return _registry