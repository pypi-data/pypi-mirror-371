"""Template file management - no hardcoded strings, only file operations."""

from pathlib import Path
import shutil
from rich.console import Console
from rich.prompt import Confirm


def create_standard_templates(templates_dir: Path) -> None:
    """Create/update all templates including Memory-Bank artifacts and PM workflow."""
    
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # First, ensure Memory-Bank artifact templates exist
    _copy_memory_bank_artifacts(templates_dir)
    
    # Then add/update PM workflow templates
    source_templates_dir = Path(__file__).parent / "template_sources"
    if source_templates_dir.exists():
        _copy_pm_workflow_templates(source_templates_dir, templates_dir)
    else:
        # Create basic structure if source doesn't exist
        _create_minimal_structure(templates_dir)
    
    # Create Claude Code agents directory for project-specific sub-agents
    _create_claude_agents(templates_dir)


def _copy_memory_bank_artifacts(templates_dir: Path) -> None:
    """Copy Memory-Bank artifact templates from claude-helpers templates directory."""
    
    # Source of Memory-Bank artifact templates
    artifacts_source = Path(__file__).parent / "templates"
    
    if not artifacts_source.exists():
        return
    
    # Copy artifact directories if they don't exist or need updating
    artifact_dirs = ["architecture", "implementation", "product", "prompts"]
    
    for artifact_dir in artifact_dirs:
        source_path = artifacts_source / artifact_dir
        target_path = templates_dir / artifact_dir
        
        if source_path.exists():
            if not target_path.exists():
                # Copy entire directory if it doesn't exist
                shutil.copytree(source_path, target_path)
            else:
                # Update individual files if directory exists
                for source_file in source_path.rglob("*"):
                    if source_file.is_file():
                        relative_path = source_file.relative_to(source_path)
                        target_file = target_path / relative_path
                        
                        # Copy if file doesn't exist or source is newer
                        if not target_file.exists() or source_file.stat().st_mtime > target_file.stat().st_mtime:
                            target_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source_file, target_file)


def _copy_pm_workflow_templates(source_dir: Path, target_dir: Path) -> None:
    """Copy only PM workflow templates, preserving existing artifacts."""
    
    # Define PM workflow template paths to copy
    pm_template_files = [
        "pm-workflow/claude-md-template.md",
        "pm-workflow/run-command-template.md", 
        "pm-workflow/slash-commands/progress.md",
        "pm-workflow/slash-commands/note.md",
        "pm-workflow/slash-commands/role.md",
        "sub-agents/dev-specialist.md",
        "sub-agents/qa-specialist.md"
    ]
    
    # Define directories to copy entirely  
    pm_template_dirs = [
        "mcp-prompts"  # MCP prompt templates for Memory-Bank operations
    ]
    
    # Copy individual template files
    for template_path in pm_template_files:
        source_file = source_dir / template_path
        target_file = target_dir / template_path
        
        if source_file.exists():
            # Create parent directory if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)
            # Copy file
            shutil.copy2(source_file, target_file)
    
    # Copy template directories using smart merge
    for template_dir in pm_template_dirs:
        source_dir_path = source_dir / template_dir
        target_dir_path = target_dir / template_dir
        
        if source_dir_path.exists():
            _smart_merge_directory(source_dir_path, target_dir_path)


def _create_claude_agents(templates_dir: Path) -> None:
    """Create Claude Code agents directory with sub-agents."""
    
    # Get the Memory-Bank root directory (parent of templates)
    memory_bank_root = templates_dir.parent
    claude_agents_dir = memory_bank_root / ".claude" / "agents"
    
    # Create .claude/agents directory
    claude_agents_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy sub-agents from templates to .claude/agents
    sub_agents_dir = templates_dir / "sub-agents"
    if sub_agents_dir.exists():
        for agent_file in sub_agents_dir.glob("*.md"):
            target_file = claude_agents_dir / agent_file.name
            shutil.copy2(agent_file, target_file)


def _create_minimal_structure(templates_dir: Path) -> None:
    """Create minimal template structure."""
    
    # Create directory structure
    dirs_to_create = [
        "pm-workflow",
        "pm-workflow/slash-commands", 
        "mcp-prompts",
        "sub-agents",
        "architecture",
        "product", 
        "implementation"
    ]
    
    for dir_name in dirs_to_create:
        (templates_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    # Create placeholder files
    placeholder_files = [
        "pm-workflow/claude-md-template.md",
        "pm-workflow/run-command-template.md", 
        "mcp-prompts/pm-focus-agent.md",
        "mcp-prompts/memory-bank-analyst.md",
        "sub-agents/dev-specialist.md",
        "sub-agents/qa-specialist.md"
    ]
    
    for file_path in placeholder_files:
        file_full_path = templates_dir / file_path
        if not file_full_path.exists():
            file_full_path.write_text(f"# {file_path}\n\nTemplate placeholder - to be customized.\n")


def update_templates_from_claude_helpers(memory_bank_templates_dir: Path) -> None:
    """Update Memory-Bank templates from claude-helpers source."""
    
    source_dir = Path(__file__).parent / "template_sources"
    if source_dir.exists():
        # Copy updated templates
        shutil.copytree(source_dir, memory_bank_templates_dir, dirs_exist_ok=True)


def _smart_merge_directory(source_dir: Path, target_dir: Path) -> None:
    """Smart merge directory: add missing files, prompt for conflicts."""
    
    console = Console()
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # If it's a symlink, resolve it first
    if source_dir.is_symlink():
        resolved_source = source_dir.resolve()
        if resolved_source.is_dir():
            source_dir = resolved_source
        else:
            return
    
    # Track what we're doing
    added_files = []
    updated_files = []
    conflicts = []
    
    # Process all source files
    for source_file in source_dir.rglob("*"):
        if source_file.is_file():
            # Calculate relative path and target
            rel_path = source_file.relative_to(source_dir)
            target_file = target_dir / rel_path
            
            # Create parent directories
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            if not target_file.exists():
                # File doesn't exist - add it
                shutil.copy2(source_file, target_file)
                added_files.append(rel_path)
            else:
                # File exists - check if different
                source_content = source_file.read_text(encoding='utf-8')
                target_content = target_file.read_text(encoding='utf-8')
                
                if source_content != target_content:
                    # Files differ - prompt for update
                    conflicts.append((rel_path, source_file, target_file))
    
    # Report results
    if added_files:
        console.print(f"[green]✅ Added {len(added_files)} new template files:[/green]")
        for file in added_files[:5]:  # Show first 5
            console.print(f"  + {file}")
        if len(added_files) > 5:
            console.print(f"  ... and {len(added_files) - 5} more")
    
    # Handle conflicts
    if conflicts:
        console.print(f"\n[yellow]⚠️  Found {len(conflicts)} template conflicts:[/yellow]")
        for rel_path, source_file, target_file in conflicts:
            console.print(f"\n📄 {rel_path}:")
            console.print(f"  Source (claude-helpers): {len(source_file.read_text())} chars")
            console.print(f"  Target (Memory-Bank):    {len(target_file.read_text())} chars")
            
            if Confirm.ask(f"Update {rel_path} with claude-helpers version?"):
                shutil.copy2(source_file, target_file)
                updated_files.append(rel_path)
                console.print(f"  [green]✅ Updated {rel_path}[/green]")
            else:
                console.print(f"  [blue]⏭️  Kept existing {rel_path}[/blue]")
    
    if updated_files:
        console.print(f"\n[green]✅ Updated {len(updated_files)} template files[/green]")
    
    if not added_files and not conflicts:
        console.print(f"[blue]ℹ️  All template files are up to date[/blue]")