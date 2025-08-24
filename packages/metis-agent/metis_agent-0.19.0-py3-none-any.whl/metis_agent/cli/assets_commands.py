"""
CLI commands for managing composable assets.

Provides commands for creating, listing, validating, and composing
personas, instruction sets, chat modes, workflows, and skills.
"""

import os
import click
import yaml
from pathlib import Path
from typing import Dict, Any, List
from ..assets import (
    AssetType, AssetRegistry, AssetComposer, get_asset_registry,
    Persona, InstructionSet, ChatMode, Workflow, Skill, Composition
)
from ..assets.base import AssetMetadata

# Try to import Rich for enhanced visuals
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


@click.group()
def assets():
    """Manage composable assets (personas, instructions, modes, workflows, skills)."""
    pass


@assets.command()
@click.option('--type', 'asset_type', type=click.Choice([t.value for t in AssetType]), 
              help='Filter by asset type')
@click.option('--category', help='Filter by category')
@click.option('--tag', help='Filter by tag')
def list(asset_type, category, tag):
    """List all available assets."""
    registry = get_asset_registry()
    
    if asset_type:
        asset_type_enum = AssetType(asset_type)
        assets_dict = registry.list_assets(asset_type_enum)
    else:
        assets_dict = registry.list_assets()
    
    if RICH_AVAILABLE:
        table = Table(title="Available Assets")
        table.add_column("Type", style="cyan")
        table.add_column("ID", style="magenta") 
        table.add_column("Name", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Tags", style="dim")
        
        for atype, asset_ids in assets_dict.items():
            for asset_id in asset_ids:
                asset = registry.get_asset(atype, asset_id)
                if asset:
                    # Apply filters
                    if category and asset.metadata.category != category:
                        continue
                    if tag and tag not in asset.metadata.tags:
                        continue
                    
                    tags_str = ", ".join(asset.metadata.tags[:3])  # Show first 3 tags
                    if len(asset.metadata.tags) > 3:
                        tags_str += "..."
                    
                    table.add_row(
                        atype.value,
                        asset_id,
                        asset.metadata.name,
                        asset.metadata.category,
                        tags_str
                    )
        
        console.print(table)
    else:
        # Fallback text output
        for atype, asset_ids in assets_dict.items():
            click.echo(f"\n{atype.value.upper()}:")
            for asset_id in asset_ids:
                asset = registry.get_asset(atype, asset_id)
                if asset:
                    # Apply filters
                    if category and asset.metadata.category != category:
                        continue
                    if tag and tag not in asset.metadata.tags:
                        continue
                    
                    click.echo(f"  {asset_id}: {asset.metadata.name}")


@assets.command()
@click.argument('asset_spec')  # format: type:id
def info(asset_spec):
    """Show detailed information about an asset."""
    try:
        asset_type_str, asset_id = asset_spec.split(':', 1)
        asset_type = AssetType(asset_type_str)
    except (ValueError, KeyError):
        click.echo(f"Invalid asset specification: {asset_spec}")
        click.echo("Format: type:id (e.g., persona:senior-developer)")
        return
    
    registry = get_asset_registry()
    asset = registry.get_asset(asset_type, asset_id)
    
    if not asset:
        click.echo(f"Asset not found: {asset_spec}")
        return
    
    if RICH_AVAILABLE:
        # Create info panel
        info_text = f"""[bold]Name:[/bold] {asset.metadata.name}
[bold]ID:[/bold] {asset.metadata.id}
[bold]Version:[/bold] {asset.metadata.version}
[bold]Author:[/bold] {asset.metadata.author}
[bold]Category:[/bold] {asset.metadata.category}
[bold]Tags:[/bold] {', '.join(asset.metadata.tags)}

[bold]Description:[/bold]
{asset.metadata.description}

[bold]Capabilities:[/bold]"""
        
        capabilities = asset.get_capabilities()
        for key, value in capabilities.items():
            info_text += f"\n• {key}: {value}"
        
        panel = Panel(info_text, title=f"{asset_type.value.title()}: {asset.metadata.name}")
        console.print(panel)
    else:
        # Fallback text output
        click.echo(f"Name: {asset.metadata.name}")
        click.echo(f"ID: {asset.metadata.id}")
        click.echo(f"Version: {asset.metadata.version}")
        click.echo(f"Author: {asset.metadata.author}")
        click.echo(f"Category: {asset.metadata.category}")
        click.echo(f"Tags: {', '.join(asset.metadata.tags)}")
        click.echo(f"Description: {asset.metadata.description}")
        
        click.echo("\nCapabilities:")
        capabilities = asset.get_capabilities()
        for key, value in capabilities.items():
            click.echo(f"  {key}: {value}")


@assets.command()
@click.argument('query')
@click.option('--type', 'asset_type', type=click.Choice([t.value for t in AssetType]),
              help='Filter by asset type')
def search(query, asset_type):
    """Search for assets by name, description, or tags."""
    registry = get_asset_registry()
    
    asset_type_enum = AssetType(asset_type) if asset_type else None
    results = registry.search_assets(query, asset_type_enum)
    
    if not results:
        click.echo(f"No assets found matching: {query}")
        return
    
    if RICH_AVAILABLE:
        table = Table(title=f"Search Results for '{query}'")
        table.add_column("Type", style="cyan")
        table.add_column("ID", style="magenta")
        table.add_column("Name", style="green")
        table.add_column("Match", style="yellow")
        
        for asset in results:
            # Determine what matched
            match_reasons = []
            query_lower = query.lower()
            if query_lower in asset.metadata.name.lower():
                match_reasons.append("name")
            if query_lower in asset.metadata.description.lower():
                match_reasons.append("description") 
            if any(query_lower in tag.lower() for tag in asset.metadata.tags):
                match_reasons.append("tags")
            
            table.add_row(
                asset.asset_type.value,
                asset.metadata.id,
                asset.metadata.name,
                ", ".join(match_reasons)
            )
        
        console.print(table)
    else:
        # Fallback text output
        click.echo(f"Search results for '{query}':")
        for asset in results:
            click.echo(f"  {asset.asset_type.value}:{asset.metadata.id} - {asset.metadata.name}")


@assets.command()
@click.argument('asset_type', type=click.Choice([t.value for t in AssetType]))
@click.argument('name')
@click.option('--template', help='Create from template')
@click.option('--interactive', '-i', is_flag=True, help='Interactive creation mode')
def create(asset_type, name, template, interactive):
    """Create a new asset."""
    asset_type_enum = AssetType(asset_type)
    
    # Generate asset ID from name
    asset_id = name.lower().replace(' ', '-').replace('_', '-')
    
    # Create metadata
    metadata = AssetMetadata(
        name=name,
        id=asset_id,
        version='1.0.0',
        description=f"Custom {asset_type} asset",
        category='custom'
    )
    
    # Create asset based on type
    if asset_type_enum == AssetType.PERSONA:
        if template:
            asset = Persona.create_from_template(name, template)
        else:
            # Create basic persona
            content = {
                'persona': {
                    'identity': {
                        'role': 'Custom Assistant',
                        'expertise': [],
                        'personality': {
                            'tone': 'Professional',
                            'style': 'Helpful',
                            'traits': ['knowledgeable']
                        }
                    },
                    'behavior': {
                        'communication_style': 'conversational',
                        'decision_making': 'balanced',
                        'problem_solving': 'systematic'
                    }
                }
            }
            asset = Persona(metadata, content)
    
    elif asset_type_enum == AssetType.INSTRUCTION_SET:
        if template:
            asset = InstructionSet.create_from_template(name, template)
        else:
            # Create basic instruction set
            content = {
                'instructions': {
                    'pre_analysis': [
                        'Analyze the request carefully',
                        'Consider multiple approaches'
                    ],
                    'output_format': {
                        'structure': 'clear and organized',
                        'include_examples': True
                    }
                }
            }
            asset = InstructionSet(metadata, content)
    
    else:
        click.echo(f"Asset creation for {asset_type} not yet implemented")
        return
    
    # Save asset
    assets_dir = Path.home() / '.metis' / 'assets' / (asset_type + 's')
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    asset_path = assets_dir / f"{asset_id}.yaml"
    asset.save(asset_path)
    
    click.echo(f"Created {asset_type} asset: {asset_path}")
    
    if interactive:
        click.echo("Opening asset file for editing...")
        click.launch(str(asset_path))


@assets.command()
@click.argument('asset_spec')  # format: type:id
def validate(asset_spec):
    """Validate an asset configuration."""
    try:
        asset_type_str, asset_id = asset_spec.split(':', 1)
        asset_type = AssetType(asset_type_str)
    except (ValueError, KeyError):
        click.echo(f"Invalid asset specification: {asset_spec}")
        return
    
    registry = get_asset_registry()
    errors = registry.validate_asset(asset_type, asset_id)
    
    if not errors:
        if RICH_AVAILABLE:
            console.print(f"✅ Asset [green]{asset_spec}[/green] is valid")
        else:
            click.echo(f"✅ Asset {asset_spec} is valid")
    else:
        if RICH_AVAILABLE:
            console.print(f"❌ Asset [red]{asset_spec}[/red] has validation errors:")
            for error in errors:
                console.print(f"  • {error}")
        else:
            click.echo(f"❌ Asset {asset_spec} has validation errors:")
            for error in errors:
                click.echo(f"  • {error}")


@assets.command()
def init():
    """Initialize the asset system and create default directory structure."""
    base_path = Path.home() / '.metis'
    
    # Create directory structure
    directories = [
        'assets/personas',
        'assets/instructions', 
        'assets/modes',
        'assets/workflows',
        'assets/skills',
        'assets/compositions',
        'config',
        'cache'
    ]
    
    for dir_path in directories:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        click.echo(f"Created: {full_path}")
    
    # Create basic config file
    config_path = base_path / 'config' / 'global.yaml'
    if not config_path.exists():
        config_data = {
            'version': '1.0.0',
            'asset_paths': [
                str(base_path / 'assets')
            ],
            'cache_enabled': True,
            'auto_update': False
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        click.echo(f"Created config: {config_path}")
    
    click.echo("Asset system initialized successfully!")


# Composition commands
@click.group()
def compose():
    """Compose assets into unified agent configurations."""
    pass


@compose.command()
@click.argument('name')
@click.option('--persona', help='Persona to include (e.g., senior-developer)')
@click.option('--instructions', help='Instruction sets to include (e.g., code-review+security)')
@click.option('--mode', help='Chat mode to use')
@click.option('--skills', help='Skills to include (e.g., api-testing+performance)')
@click.option('--workflow', help='Workflow to include')
@click.option('--save', is_flag=True, help='Save this composition')
def session(name, persona, instructions, mode, skills, workflow, save):
    """Create a composed agent session."""
    registry = get_asset_registry()
    composer = AssetComposer(registry)
    
    # Build asset specifications
    asset_specs = []
    
    if persona:
        asset_specs.append(f"persona:{persona}")
    if instructions:
        asset_specs.append(f"instructions:{instructions}")
    if mode:
        asset_specs.append(f"mode:{mode}")
    if skills:
        asset_specs.append(f"skill:{skills}")
    if workflow:
        asset_specs.append(f"workflow:{workflow}")
    
    if not asset_specs:
        click.echo("No assets specified. Use options like --persona, --instructions, etc.")
        return
    
    try:
        composition = composer.compose(asset_specs)
        errors = composition.validate()
        
        if errors:
            click.echo("❌ Composition validation errors:")
            for error in errors:
                click.echo(f"  • {error}")
            return
        
        # Build agent config
        agent_config = composition.build_agent_config()
        
        if RICH_AVAILABLE:
            console.print(f"✅ Successfully composed [green]{name}[/green]")
            
            # Show composition summary
            summary_text = f"[bold]Composition Summary:[/bold]\n"
            if composition.personas:
                personas_list = [p.metadata.name for p in composition.personas]
                summary_text += f"• Personas: {', '.join(personas_list)}\n"
            if composition.instruction_sets:
                instructions_list = [i.metadata.name for i in composition.instruction_sets]
                summary_text += f"• Instructions: {', '.join(instructions_list)}\n"
            if composition.chat_modes:
                modes_list = [m.metadata.name for m in composition.chat_modes]
                summary_text += f"• Chat Mode: {', '.join(modes_list)}\n"
            if composition.skills:
                skills_list = [s.metadata.name for s in composition.skills]
                summary_text += f"• Skills: {', '.join(skills_list)}\n"
            
            console.print(Panel(summary_text, title="Composition Ready"))
        else:
            click.echo(f"✅ Successfully composed {name}")
        
        if save:
            # Save composition for reuse
            compositions_dir = Path.home() / '.metis' / 'assets' / 'compositions'
            compositions_dir.mkdir(parents=True, exist_ok=True)
            
            composition_data = {
                'metadata': {
                    'name': name,
                    'id': name.lower().replace(' ', '-'),
                    'version': '1.0.0',
                    'description': f"Saved composition: {name}",
                    'type': 'composition'
                },
                'content': {
                    'composition': {
                        'assets': {}
                    }
                }
            }
            
            # Add assets to composition
            if composition.personas:
                composition_data['content']['composition']['assets']['persona'] = [p.metadata.id for p in composition.personas]
            if composition.instruction_sets:
                composition_data['content']['composition']['assets']['instructions'] = [i.metadata.id for i in composition.instruction_sets]
            if composition.chat_modes:
                composition_data['content']['composition']['assets']['mode'] = composition.chat_modes[0].metadata.id
            if composition.skills:
                composition_data['content']['composition']['assets']['skill'] = [s.metadata.id for s in composition.skills]
            
            composition_path = compositions_dir / f"{name.lower().replace(' ', '-')}.yaml"
            with open(composition_path, 'w', encoding='utf-8') as f:
                yaml.dump(composition_data, f, default_flow_style=False)
            
            click.echo(f"Saved composition: {composition_path}")
        
        # TODO: Actually start agent session with this configuration
        click.echo(f"Ready to start agent session with composition: {name}")
        
    except Exception as e:
        click.echo(f"❌ Error composing assets: {e}")


# Add subcommands to main CLI
def register_asset_commands(cli):
    """Register asset commands with the main CLI."""
    cli.add_command(assets)
    cli.add_command(compose)