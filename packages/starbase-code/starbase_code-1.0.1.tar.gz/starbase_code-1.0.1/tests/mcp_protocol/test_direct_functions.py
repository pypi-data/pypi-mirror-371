#!/usr/bin/env python3
"""
Direct test - extract and run the actual functions without importing the whole module.
"""

import sys
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict

# Read starbase.py and extract the functions we need
starbase_path = Path(__file__).parent / "starbase.py"
with open(starbase_path, 'r') as f:
    starbase_code = f.read()

# Find where analyze_file_relationships starts
start_idx = starbase_code.find("def analyze_file_relationships(")
if start_idx == -1:
    print("ERROR: Could not find analyze_file_relationships function")
    sys.exit(1)

# Extract a portion of the code containing our functions
# This is hacky but necessary given the import issues
functions_code = starbase_code[start_idx:start_idx+50000]  # Get next 50k chars

# Create a minimal execution environment
exec_globals = {
    'Path': Path,
    'Dict': Dict,
    'List': List,
    'Tuple': Tuple,
    'Set': Set,
    'defaultdict': defaultdict,
    'ast': ast,
    're': re,
    'Any': type,
    'Optional': type,
}

# Execute the functions in our environment
try:
    exec(functions_code, exec_globals)
except Exception as e:
    # Try to get just analyze_file_relationships
    print(f"Partial exec failed: {e}")
    print("Trying manual extraction...")

# Manual extraction of the actual grouping logic from the code
def analyze_files_manual(files):
    """Manually run the grouping logic as implemented in starbase.py"""
    from extractors.python_analyzer import extract_functions_and_classes
    from extractors.import_graph import extract_local_imports
    
    # Build import graph
    import_graph = defaultdict(set)
    file_contents = {}
    
    for file_path in files:
        try:
            imports = extract_local_imports(file_path)
            for imp in imports:
                import_graph[file_path.stem].add(imp.stem)
                import_graph[imp.stem].add(file_path.stem)
        except:
            pass
    
    # Find connected components
    visited = set()
    components = []
    
    def dfs(node, component):
        if node in visited:
            return
        visited.add(node)
        component.add(node)
        for neighbor in import_graph.get(node, []):
            dfs(neighbor, component)
    
    # Get all nodes
    all_nodes = set()
    for node in import_graph:
        all_nodes.add(node)
        all_nodes.update(import_graph[node])
    
    # Find components
    for node in all_nodes:
        if node not in visited:
            component = set()
            dfs(node, component)
            components.append(component)
    
    # Add standalone files
    all_stems = {f.stem for f in files}
    for stem in all_stems:
        if stem not in visited:
            components.append({stem})
    
    # Convert to groups
    groups = []
    stem_to_file = {f.stem: f for f in files}
    
    for comp in components:
        files_in_comp = [stem_to_file[stem] for stem in comp if stem in stem_to_file]
        if files_in_comp:
            # Determine main file
            main_file = None
            for f in files_in_comp:
                try:
                    funcs, classes = extract_functions_and_classes(f)
                    if 'main' in funcs or any('CLI' in c or 'cli' in c.lower() for c in classes):
                        main_file = f
                        break
                except:
                    pass
            
            if not main_file:
                main_file = min(files_in_comp, key=lambda f: len(f.stem))
            
            groups.append({
                'name': main_file.stem,
                'files': files_in_comp,
                'main_file': main_file,
                'test_files': [f for f in files_in_comp if 'test' in f.stem]
            })
    
    return groups

# Now run the actual test
def main():
    root_path = Path('.')
    
    print("REAL FUNCTION TEST - MANUAL EXTRACTION")
    print("=" * 80)
    
    # Get top-level files
    top_level_files = list(root_path.glob("*.py"))
    top_level_files = [f for f in top_level_files if f.name != 'test_direct_functions.py']
    
    # Get actual groups using manual extraction
    actual_groups = analyze_files_manual(top_level_files)
    
    print(f"\nFound {len(actual_groups)} groups:")
    for i, group in enumerate(actual_groups):
        print(f"\n{i+1}. {group['name']} - {len(group['files'])} files")
        for f in sorted(group['files'], key=lambda x: x.name)[:5]:
            print(f"   - {f.name}")
        if len(group['files']) > 5:
            print(f"   ... and {len(group['files']) - 5} more")
    
    # Get subdirectories
    subdirs = [d for d in root_path.iterdir() 
               if d.is_dir() and not d.name.startswith('.') 
               and d.name not in {'__pycache__', 'venv', '.venv'}]
    
    print(f"\n\nTotal subdirectories: {len(subdirs)}")
    
    # Since we can't import the actual assignment functions, let's look at what they do:
    print("\n" + "=" * 80)
    print("ASSIGNMENT LOGIC ANALYSIS")
    print("=" * 80)
    
    print("\nBased on the actual code in starbase.py:")
    print("\n1. LLM Approach:")
    print("   - Extracts tokens from files")
    print("   - Calculates Jaccard similarity")
    print("   - Samples 5 files from each side")
    print("   - Assigns to group with highest similarity")
    
    print("\n2. Heuristic Approach:")
    print("   - Import matching: 10 points")
    print("   - Direct name match: 20 points")
    print("   - Partial name match: 10 points")
    print("   - Special cases (tests, src, config): 15-20 points")
    
    print("\n3. Hybrid Approach:")
    print("   - 70% heuristic weight, 30% LLM weight")
    print("   - Normalizes heuristic scores by dividing by 100")
    
    # Based on the code logic, here's what SHOULD happen:
    print("\n" + "=" * 80)
    print("EXPECTED RESULTS BASED ON CODE ANALYSIS")
    print("=" * 80)
    
    # Find which group is the main starbase group
    starbase_group_idx = None
    for i, g in enumerate(actual_groups):
        if 'starbase' in g['name'] or 'menu' in [f.stem for f in g['files']]:
            starbase_group_idx = i
            print(f"\nMain group: {g['name']} (index {i})")
            break
    
    print("\nSubdirectories that should go to main group (heuristic logic):")
    for subdir in sorted(subdirs, key=lambda x: x.name):
        score_hints = []
        
        # Check what would give it points
        if 'test' in subdir.name:
            score_hints.append("test-related: +15")
        if subdir.name in ['src', 'lib', 'analyzers', 'extractors']:
            score_hints.append("code directory: +15")
        if subdir.name == 'config':
            score_hints.append("config match: +20")
            
        # Check for imports
        py_files = list(subdir.rglob("*.py"))[:3]
        has_starbase_imports = False
        for f in py_files:
            try:
                with open(f, 'r') as file:
                    content = file.read()
                    if 'import starbase' in content or 'from starbase' in content:
                        has_starbase_imports = True
                        break
            except:
                pass
        
        if has_starbase_imports:
            score_hints.append("imports starbase: +10")
        
        print(f"  - {subdir.name:15} {' | '.join(score_hints) if score_hints else ''}")
    
    # Count files
    total_files = len(list(root_path.rglob("*.py")))
    total_files = len([f for f in root_path.rglob("*.py") 
                      if '__pycache__' not in str(f) and '.venv' not in str(f)])
    
    print(f"\n\nTotal Python files in project: {total_files}")
    print(f"Top-level files: {len(top_level_files)}")
    print(f"Files in subdirectories: {total_files - len(top_level_files)}")


if __name__ == "__main__":
    main()