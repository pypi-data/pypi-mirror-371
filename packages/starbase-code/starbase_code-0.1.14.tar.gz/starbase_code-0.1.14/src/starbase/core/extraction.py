"""
Extraction helper functions for starbase.

This module contains functions to help with code extraction logic,
breaking down the complex extract_menu function into smaller pieces.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Set
from datetime import datetime
import shutil
import json
import tinydb

from .analysis import extract_local_imports, trace_dependencies


def extract_single_file(path: Path) -> Dict[str, Any]:
    """Create entry point for single file extraction."""
    content = path.read_text()
    return {
        'file': path,
        'priority': 10,
        'line_count': len(content.splitlines()),
        'import_count': 0,
        'mtime': path.stat().st_mtime,
        'has_main': '__main__' in content,
        'type': 'script' if path.suffix == '.py' else 'file'
    }


def get_python_files_in_directory(path: Path) -> Tuple[List[Path], int]:
    """Get Python files in directory and count files in subdirectories."""
    py_files = list(path.glob("*.py"))
    
    # Get subdirectories
    subdirs = [d for d in path.iterdir() 
               if d.is_dir() and not d.name.startswith('.') 
               and d.name not in {'__pycache__', 'venv', '.venv'}]
    
    # Count files in subdirectories
    py_files_in_subdirs = 0
    for subdir in subdirs:
        py_files_in_subdirs += len(list(subdir.rglob("*.py")))
    
    return py_files, py_files_in_subdirs


def display_group_info(group: Dict[str, Any], index: int, path: Path, console: Any) -> None:
    """Display information about a single group."""
    # Show group header
    total_py_files = len([f for f in group['files'] if f.suffix == '.py'])
    if group['type'] == 'connected' or total_py_files > 1:
        console.print(f"{index}️⃣  [bold]{group['name']}[/bold] - {total_py_files} files")
    else:
        console.print(f"{index}️⃣  [bold]{group['name']}[/bold] - standalone")
    
    # Show top-level files in group first
    top_level_files = [f for f in group['files'] if f.parent == path]
    for file in top_level_files:
        display_file_info(file, group, console)
    
    # Show subdirectories if any
    if group.get('subdirectories'):
        for subdir in group['subdirectories']:
            subdir_files = [f for f in group['files'] if str(subdir) in str(f)]
            if subdir_files:
                console.print(f"   📁 {subdir.name}/ ({len(subdir_files)} files)")
    
    # Show version information if any
    if group.get('versions'):
        for file, versions in group['versions'].items():
            console.print(f"   [dim]⚠️  Has {len(versions)} old version(s): {', '.join(v.name for v in versions)}[/dim]")
            console.print(f"      [dim]These will be skipped during extraction[/dim]")
    
    console.print()


def display_file_info(file: Path, group: Dict[str, Any], console: Any) -> None:
    """Display information about a single file within a group."""
    is_main = file == group['main_file']
    is_test = file in group.get('test_files', [])
    
    if is_main:
        prefix = "   📍"
    elif is_test:
        prefix = "   🧪"
    else:
        prefix = "   📄"
        
    console.print(f"{prefix} {file.name}")
    
    # Show import relationships if connected group
    if group['type'] == 'connected' and not is_main:
        local_imports = extract_local_imports(file)
        imports_in_group = [f.name for f in local_imports if f in group['files']]
        if imports_in_group:
            console.print(f"      → imports: {', '.join(imports_in_group)}")


def check_existing_files(groups: List[Dict[str, Any]], check_starbase_status) -> List[Dict[str, Any]]:
    """Check if any files already exist in starbase."""
    existing_warnings = []
    for group in groups:
        for file in group['files']:
            status = check_starbase_status(file)
            if status['exists']:
                existing_warnings.append({
                    'file': file,
                    'group': group['name'],
                    'status': status
                })
    return existing_warnings


def convert_group_to_entry_points(group: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert a group to entry points format for do_extraction."""
    entry_points = []
    for file in group['files']:
        entry_points.append({
            'file': file,
            'priority': 10 if file == group['main_file'] else 5,
            'line_count': len(file.read_text().splitlines()),
            'import_count': 0,
            'mtime': file.stat().st_mtime,
            'has_main': file == group['main_file'],
            'type': 'script'
        })
    return entry_points


def parse_package_selection(selection: str, total_groups: int) -> List[int]:
    """Parse user selection string for packages."""
    if selection.lower() == 'all':
        return list(range(1, total_groups + 1))
    
    selected_indices = []
    for part in selection.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            selected_indices.extend(range(start, end + 1))
        else:
            selected_indices.append(int(part))
    
    # Filter valid indices
    return [i for i in selected_indices if 0 < i <= total_groups]


def find_related_files(py_file: Path) -> List[str]:
    """Find bash scripts, configs, etc. related to this file"""
    base_name = py_file.stem
    related = []
    
    # Check for shell scripts with same base name
    for ext in ['', '.sh', '.bash']:
        script = py_file.parent / (base_name + ext)
        if script.exists() and script != py_file and script.is_file():
            # Check if executable
            import os
            if os.access(script, os.X_OK) or script.suffix in ['.sh', '.bash']:
                related.append(script.name)
    
    # For package isolation, only include config files if the file is the main entry point
    # or if we're extracting a whole directory
    # Don't automatically include project-wide configs for single file extractions
    
    return related[:5]  # Limit display


def generate_smart_description(project_path: Path, entry_points: List[Dict] = None, manager=None, console=None) -> str:
    """Generate intelligent description by analyzing code with LLM"""
    try:
        # Try to use LLM for smart description
        if manager:
            # Import here to avoid circular dependency
            import sys
            import os
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            # Import get_llm from starbase
            try:
                from starbase import get_llm
            except ImportError:
                # Try alternate import for installed package
                from starbase.cli import get_llm
            
            # Collect relevant files to analyze
            files_to_analyze = []
            
            # Common code file patterns
            code_patterns = ['*.py', '*.js', '*.ts', '*.jsx', '*.tsx', '*.java', '*.go', '*.rs', 
                           '*.cpp', '*.c', '*.h', '*.cs', '*.rb', '*.php', '*.swift', '*.kt']
            
            # Documentation patterns
            doc_patterns = ['README*', '*.md', '*.txt', 'LICENSE*', 'CHANGELOG*']
            
            # Collect files
            for pattern in code_patterns + doc_patterns:
                files_to_analyze.extend(project_path.glob(pattern))
                # Also check one level deep for organized projects
                files_to_analyze.extend(project_path.glob(f"*/{pattern}"))
            
            # Filter out unwanted directories
            skip_dirs = {'venv', '.venv', 'env', '.env', 'node_modules', '__pycache__', 
                        '.git', 'dist', 'build', '.pytest_cache', '.tox', 'htmlcov',
                        'site-packages', 'migrations', '.idea', '.vscode'}
            
            files_to_analyze = [
                f for f in files_to_analyze 
                if f.is_file() and not any(skip in f.parts for skip in skip_dirs)
            ]
            
            # Limit to reasonable number of files and size
            content_parts = []
            total_chars = 0
            max_total_chars = 15000  # Limit total content
            
            # Prioritize README and main files
            priority_files = sorted(files_to_analyze, key=lambda f: (
                0 if 'README' in f.name.upper() else
                1 if f.name in ['main.py', 'app.py', 'index.js', 'index.ts'] else
                2 if entry_points and any(str(f) == str(ep.get('file', '')) for ep in entry_points) else
                3
            ))
            
            for file in priority_files[:20]:  # Max 20 files
                try:
                    if file.stat().st_size < 50000:  # Under 50KB per file
                        content = file.read_text(errors='ignore')
                        # Take more content from important files
                        char_limit = 3000 if 'README' in file.name.upper() else 1500
                        truncated = content[:char_limit]
                        if len(content) > char_limit:
                            truncated += "\n... (truncated)"
                        
                        content_parts.append(f"\n--- File: {file.name} ---\n{truncated}\n")
                        total_chars += len(truncated)
                        
                        if total_chars > max_total_chars:
                            break
                except Exception:
                    continue  # Skip files that can't be read
            
            if content_parts:
                # Get LLM instance
                llm = get_llm()
                
                # Create prompt
                prompt = """Analyze this code and write a concise 1-2 sentence description.
Focus on: what it does, main purpose, key algorithms or patterns, and technologies/frameworks used.
Be specific - mention actual function names, libraries, or algorithms if notable.
Do NOT just say "Python script" or "code package" - explain what it actually does.

Code files:
{}

Write a clear, specific description:""".format(''.join(content_parts))
                
                # Get LLM response
                if console:
                    console.print("[dim]Analyzing code with LLM...[/dim]")
                
                response = llm.invoke(prompt)
                description = response.content.strip() if hasattr(response, 'content') else str(response).strip()
                
                # Clean up the description
                description = description.replace('\n', ' ').strip()
                
                # Ensure it's not too long
                if len(description) > 200:
                    description = description[:197] + "..."
                
                return description
                
    except Exception as e:
        # Fallback if LLM fails
        if console:
            console.print(f"[dim]LLM analysis failed: {e}[/dim]")
    
    # Fallback to basic description
    if entry_points and len(entry_points) == 1:
        file_path = entry_points[0]['file']
        return f"Extracted {file_path.name} - Python script"
    elif entry_points:
        return f"Python project with {len(entry_points)} entry points"
    else:
        return "Extracted code package"


def do_extraction(entry_points: List[Dict], source_path: Path, include_deps: bool, 
                 package_name: Optional[str], manager, db, console) -> List[Dict]:
    """Perform the actual extraction of files to starbase
    
    Args:
        entry_points: List of entry point dictionaries
        source_path: Source path being extracted from
        include_deps: Whether to include dependencies
        package_name: Optional package name override
        manager: StarbaseManager instance
        db: TinyDB database instance
        console: Rich Console instance
    
    Returns:
        List of extracted file dictionaries
    """
    starbase_path = Path(manager.get_active_path())
    extracted_files = []
    
    # Check if we already have an entry with this exact name
    Query = tinydb.Query()
    
    # First determine the package name
    if package_name is None:
        # Only determine package name if not provided
        if len(entry_points) == 1 and entry_points[0]['file'].is_file():
            # For single file extractions, use the file stem as package name
            package_name = entry_points[0]['file'].stem
        else:
            # For multiple files, use the first file's stem as fallback
            package_name = entry_points[0]['file'].stem
    
    # Now search for existing entry by package name
    existing_entry = db.search(Query.name == package_name)
    
    # Package name is already determined above
    
    # Get all files to extract
    all_files = set()
    for ep in entry_points:
        all_files.add(ep['file'])
        
        # Add dependencies if requested
        if include_deps:
            deps = trace_dependencies(ep['file'])
            all_files.update(deps)
            console.print(f"[dim]Found {len(deps)} dependencies for {ep['file'].name}[/dim]")
        
        # Add related files (configs, scripts)
        related = find_related_files(ep['file'])
        for rel in related:
            rel_path = ep['file'].parent / rel
            if rel_path.exists():
                all_files.add(rel_path)
    
    # Determine target structure
    # If all files are from same directory, preserve structure
    common_parent = None
    if len(all_files) > 1:
        parents = {f.parent for f in all_files}
        if len(parents) == 1:
            common_parent = list(parents)[0]
    
    # Use the package name determined earlier
    extract_name = package_name
    
    # Determine target directory
    if existing_entry:
        # Use existing directory
        target_dir = starbase_path / existing_entry[0]['path']
        console.print(f"\n[yellow]Updating existing extraction: {target_dir.name}/[/yellow]")
        # Clear existing files first
        if target_dir.exists() and target_dir.is_dir():
            for item in target_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
    else:
        # Make name unique if needed
        target_dir = starbase_path / extract_name
        counter = 1
        while target_dir.exists():
            target_dir = starbase_path / f"{extract_name}_{counter}"
            counter += 1
        console.print(f"\n[green]Extracting to: {target_dir.name}/[/green]")
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    for file in all_files:
        try:
            # Determine relative path
            if common_parent:
                rel_path = file.relative_to(common_parent)
            else:
                rel_path = file.name
            
            target_file = target_dir / rel_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(file, target_file)
            extracted_files.append({
                'source': str(file),
                'target': str(target_file.relative_to(starbase_path)),
                'size': file.stat().st_size
            })
            console.print(f"  [dim]✓ {rel_path}[/dim]")
        except Exception as e:
            console.print(f"  [red]✗ {file.name}: {e}[/red]")
    
    # Update catalog
    if extracted_files:
        # Generate smart description using LLM
        description = generate_smart_description(target_dir, entry_points, manager, console)
        
        catalog_entry = {
            'name': extract_name,
            'path': str(target_dir.relative_to(starbase_path)),
            'type': 'project',
            'description': description,
            'extracted_from': str(source_path),
            'extracted_at': datetime.now().isoformat()
        }
        
        # Update or insert catalog entry based on what we found earlier
        Query = tinydb.Query()
        
        if existing_entry:
            # Update existing entry - use the correct query based on how we found it
            if existing_entry[0].get('extracted_from') == str(source_path):
                # Found by source path
                db.update(catalog_entry, Query.extracted_from == str(source_path))
            else:
                # Found by name
                db.update(catalog_entry, Query.name == existing_entry[0]['name'])
            console.print(f"[yellow]Updated existing catalog entry: {existing_entry[0]['name']}[/yellow]")
        else:
            # Add new entry
            db.insert(catalog_entry)
        
        total_size = sum(f['size'] for f in extracted_files)
        console.print(f"\n[green]✓ Extracted {len(extracted_files)} files ({total_size / 1024:.1f} KB)[/green]")
        if existing_entry:
            console.print(f"[green]✓ Updated catalog entry '{extract_name}'[/green]")
        else:
            console.print(f"[green]✓ Added to catalog as '{extract_name}'[/green]")
        
        # Show what was extracted
        if len(entry_points) > 1:
            console.print("\n[cyan]Entry points:[/cyan]")
            for ep in entry_points:
                console.print(f"  • {ep['file'].name}")
        
        if include_deps and len(all_files) > len(entry_points):
            console.print(f"\n[cyan]Included {len(all_files) - len(entry_points)} dependencies[/cyan]")
        
        # Create package.json manifest for package isolation
        manifest = {
            'name': extract_name,
            'version': '0.1.0',
            'description': description,
            'extracted_from': str(source_path),
            'extracted_at': datetime.now().isoformat(),
            'files': [f['target'] for f in extracted_files],
            'entry_points': [str(ep['file'].name) for ep in entry_points],
            'dependencies': [],
            'file_count': len(extracted_files),
            'total_size': sum(f['size'] for f in extracted_files)
        }
        
        manifest_path = target_dir / 'package.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        console.print(f"[green]✓ Created package manifest[/green]")
        
        # Note: ensure_mcp_installed is not called here - handle it in the caller if needed
    
    return extracted_files


def validate_and_resolve_path(initial_path: Optional[str], console: Any) -> Optional[Path]:
    """Validate and resolve extraction path from user input.
    
    Returns None if path is invalid.
    """
    if initial_path:
        path = Path(initial_path).resolve()
    else:
        from rich.prompt import Prompt
        path = Prompt.ask("Enter path to analyze", default=".")
        path = Path(path).resolve()
    
    if not path.exists():
        console.print("[red]Path does not exist![/red]")
        return None
    
    return path


def handle_single_file_extraction(path: Path, console: Any, do_extraction) -> None:
    """Handle extraction of a single file."""
    from rich.prompt import Confirm
    
    console.print(f"\n[cyan]🔍 Extracting single file: {path.name}[/cyan]")
    entry_point = extract_single_file(path)
    include_deps = Confirm.ask("Include dependencies?", default=True)
    do_extraction([entry_point], path.parent, include_deps)


def analyze_directory_for_extraction(path: Path, console: Any) -> Optional[List[Dict[str, Any]]]:
    """Analyze directory and return groups or None if no files found."""
    from .analysis import analyze_file_relationships
    from .assignment import analyze_project_with_subdirectories
    
    # Get Python files and analyze
    py_files, py_files_in_subdirs = get_python_files_in_directory(path)
    
    if not py_files:
        console.print("[yellow]No Python files found in directory.[/yellow]")
        return None
    
    # Analyze file relationships for smart grouping
    if py_files_in_subdirs > 0:
        console.print(f"\n[dim]Analyzing {len(py_files)} top-level files and {py_files_in_subdirs} files in subdirectories...[/dim]")
        groups = analyze_project_with_subdirectories(path)
    else:
        console.print(f"\n[dim]Analyzing relationships between {len(py_files)} files...[/dim]")
        groups = analyze_file_relationships(py_files)
    
    return groups


def handle_existing_file_warnings(existing_warnings: List[Dict[str, Any]], console: Any) -> bool:
    """Display warnings about existing files and ask for confirmation.
    
    Returns True if user wants to continue, False otherwise.
    """
    from rich.prompt import Confirm
    
    if not existing_warnings:
        return True
    
    console.print("\n[yellow]⚠️  Some files already exist in starbase:[/yellow]")
    for warning in existing_warnings:
        console.print(f"   • {warning['file'].name} in package '{warning['group']}'")
    
    return Confirm.ask("\nContinue anyway?", default=True)


def handle_single_group_extraction(group: Dict[str, Any], path: Path, console: Any, do_extraction) -> None:
    """Handle extraction when there's only one group."""
    from rich.prompt import Confirm
    
    console.print(f"\nPackage '{group['name']}' contains {len(group['files'])} file(s)")
    if Confirm.ask("Extract this package?", default=True):
        entry_points = convert_group_to_entry_points(group)
        do_extraction(entry_points, path, include_deps=False, package_name=group['name'])


def parse_group_selection(selection: str, total_groups: int) -> List[int]:
    """Parse user selection string into list of indices."""
    selected_indices = []
    
    if selection.lower() == 'all':
        return list(range(1, total_groups + 1))
    
    for part in selection.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            selected_indices.extend(range(start, end + 1))
        else:
            selected_indices.append(int(part))
    
    # Filter valid indices
    return [i for i in selected_indices if 0 < i <= total_groups]


def extract_selected_groups(selected_groups: List[Dict[str, Any]], path: Path, console: Any, do_extraction) -> None:
    """Extract the selected groups."""
    console.print(f"\n[cyan]Extracting {len(selected_groups)} package(s)...[/cyan]")
    
    for group in selected_groups:
        console.print(f"\n📦 Extracting package '{group['name']}'...")
        entry_points = create_entry_points_for_group(group)
        do_extraction(entry_points, path, include_deps=False, package_name=group['name'])


def create_entry_points_for_group(group: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create entry points list for a group of files."""
    entry_points = []
    
    for file in group['files']:
        entry_points.append({
            'file': file,
            'priority': 10 if file == group['main_file'] else 5,
            'line_count': len(file.read_text().splitlines()),
            'import_count': 0,
            'mtime': file.stat().st_mtime,
            'has_main': file == group['main_file'],
            'type': 'script'
        })
    
    return entry_points


def beamup_directory(source_path: Path, max_size_mb: int, package_name: Optional[str], 
                    manager, db, console) -> Dict[str, Any]:
    """Beam up entire directory to starbase, respecting .gitignore.
    
    Args:
        source_path: Directory to beam up
        max_size_mb: Maximum file size in MB
        package_name: Optional package name (defaults to directory name)
        manager: StarbaseManager instance
        db: TinyDB database instance
        console: Rich Console instance
    
    Returns:
        Dictionary with success status and details
    """
    import pathspec
    
    console.print(f"\n[cyan]🚀 Beaming up {source_path}...[/cyan]")
    
    # Determine package name
    if not package_name:
        # Try to get from package.json or pyproject.toml
        if (source_path / "package.json").exists():
            try:
                pkg_data = json.loads((source_path / "package.json").read_text())
                package_name = pkg_data.get("name", source_path.name)
            except:
                package_name = source_path.name
        elif (source_path / "pyproject.toml").exists():
            try:
                import toml
                pkg_data = toml.loads((source_path / "pyproject.toml").read_text())
                package_name = pkg_data.get("project", {}).get("name", source_path.name)
            except:
                package_name = source_path.name
        else:
            package_name = source_path.name
    
    # Clean package name (remove special chars)
    package_name = package_name.replace("/", "-").replace("@", "").replace(" ", "-")
    
    # Read .gitignore if exists
    gitignore_path = source_path / '.gitignore'
    spec = None
    if gitignore_path.exists():
        console.print("[dim]📋 Using .gitignore patterns[/dim]")
        try:
            gitignore_lines = gitignore_path.read_text().splitlines()
            # Filter out comments and empty lines
            gitignore_lines = [line.strip() for line in gitignore_lines 
                             if line.strip() and not line.strip().startswith('#')]
            spec = pathspec.PathSpec.from_lines('gitwildmatch', gitignore_lines)
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not parse .gitignore: {e}[/yellow]")
    else:
        console.print("[dim]📋 No .gitignore found - including all files[/dim]")
    
    # Collect files to beam up
    files_to_copy = []
    skipped_large = []
    skipped_gitignore = []
    total_size = 0
    max_size_bytes = max_size_mb * 1024 * 1024
    
    for file_path in source_path.rglob('*'):
        if not file_path.is_file():
            continue
            
        # Skip .git directory
        if '.git' in file_path.parts:
            continue
        
        # Get relative path for gitignore matching
        try:
            rel_path = file_path.relative_to(source_path)
        except ValueError:
            continue
            
        # Check gitignore
        if spec and spec.match_file(str(rel_path)):
            skipped_gitignore.append(rel_path)
            continue
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > max_size_bytes:
            skipped_large.append((rel_path, file_size))
            console.print(f"[yellow]⚠️  Skipping large file: {rel_path} ({file_size / 1024 / 1024:.1f} MB)[/yellow]")
            continue
        
        files_to_copy.append((file_path, rel_path))
        total_size += file_size
    
    if not files_to_copy:
        console.print("[red]❌ No files to beam up![/red]")
        return {'success': False, 'reason': 'no_files'}
    
    # Show summary
    console.print(f"\n[green]📁 Found {len(files_to_copy)} files ({total_size / 1024 / 1024:.1f} MB total)[/green]")
    if skipped_gitignore:
        console.print(f"[dim]   Skipped {len(skipped_gitignore)} files from .gitignore[/dim]")
    if skipped_large:
        console.print(f"[dim]   Skipped {len(skipped_large)} large files[/dim]")
    
    # Create target directory in starbase
    starbase_path = Path(manager.get_active_path())
    target_dir = starbase_path / package_name
    
    if target_dir.exists():
        console.print(f"[yellow]⚠️  Package '{package_name}' already exists in starbase[/yellow]")
        from rich.prompt import Confirm
        if not Confirm.ask("Overwrite existing package?"):
            return {'success': False, 'reason': 'cancelled'}
        # Remove existing directory
        shutil.rmtree(target_dir)
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files maintaining structure
    console.print(f"\n[cyan]📦 Beaming up to: {target_dir}[/cyan]")
    copied_files = []
    
    for source_file, rel_path in files_to_copy:
        target_file = target_dir / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(source_file, target_file)
            copied_files.append({
                'source': str(source_file),
                'target': str(target_file.relative_to(starbase_path)),
                'size': source_file.stat().st_size
            })
        except Exception as e:
            console.print(f"[red]❌ Error copying {rel_path}: {e}[/red]")
    
    # Generate smart description using LLM
    console.print("\n[dim]🤖 Generating AI description...[/dim]")
    description = generate_smart_description(target_dir, None, manager, console)
    
    # Update catalog
    Query = tinydb.Query()
    catalog_entry = {
        'name': package_name,
        'path': package_name,
        'type': 'beamup',
        'description': description,
        'extracted_from': str(source_path),
        'extracted_at': datetime.now().isoformat(),
        'file_count': len(copied_files),
        'total_size': total_size
    }
    
    db.upsert(catalog_entry, Query.name == package_name)
    
    console.print(f"\n[bold green]✅ Successfully beamed up '{package_name}'![/bold green]")
    console.print(f"[green]   📁 {len(copied_files)} files[/green]")
    console.print(f"[green]   💾 {total_size / 1024 / 1024:.1f} MB[/green]")
    console.print(f"[green]   📍 Location: {target_dir}[/green]")
    console.print(f"[green]   📝 Description: {description[:100]}...[/green]" if len(description) > 100 else f"[green]   📝 Description: {description}[/green]")
    
    return {
        'success': True,
        'package_name': package_name,
        'target_dir': str(target_dir),
        'files_copied': len(copied_files),
        'total_size': total_size,
        'description': description
    }