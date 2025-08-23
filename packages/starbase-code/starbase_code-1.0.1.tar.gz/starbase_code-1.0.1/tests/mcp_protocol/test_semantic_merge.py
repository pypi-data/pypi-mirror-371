#!/usr/bin/env python3
"""
Test the semantic analysis phase - show how it merges groups based on content references.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.analysis import analyze_file_relationships

def main():
    """Test semantic merging on this project."""
    # Get top-level files
    top_level_files = list(Path('.').glob("*.py"))
    
    print("Testing semantic analysis phase...")
    print("=" * 60)
    
    # Run the analysis (which now includes semantic merging)
    groups = analyze_file_relationships(top_level_files)
    
    print(f"\nGroups after semantic analysis: {len(groups)}")
    for i, group in enumerate(groups):
        print(f"\n{i+1}. {group['name']} ({group['type']}):")
        print(f"   Files: {len(group['files'])}")
        for f in sorted(group['files'], key=lambda x: x.name):
            print(f"   - {f.name}")
    
    print("\n" + "=" * 60)
    
    # Show what the grouping would look like without semantic analysis
    # We'll need to temporarily disable it
    print("\nFor comparison, let's see what groups we'd have WITHOUT semantic analysis...")
    
    # Import the function to get initial groups
    from core.analysis import (
        extract_local_imports, detect_test_relationships, 
        detect_file_versions, detect_name_relationships,
        find_connected_components
    )
    from collections import defaultdict
    
    # Manually run just the import-based grouping
    import_map = {}
    for file in top_level_files:
        if file.suffix == '.py':
            imports = extract_local_imports(file)
            import_map[file] = imports.intersection(set(top_level_files))
    
    components = find_connected_components(import_map)
    
    print(f"\nConnected components from imports only: {len(components)}")
    for i, comp in enumerate(components):
        files = sorted([f.name for f in comp])
        print(f"  {i+1}. {files}")
    
    # Show standalone files
    all_in_components = set()
    for comp in components:
        all_in_components.update(comp)
    
    standalone = [f for f in top_level_files if f not in all_in_components and f.suffix == '.py']
    print(f"\nStandalone files: {len(standalone)}")
    for f in sorted(standalone, key=lambda x: x.name):
        print(f"  - {f.name}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS:")
    print("Without semantic analysis, simple_real_test.py would be standalone.")
    print("With semantic analysis, it should be merged into starbase group due to references.")

if __name__ == "__main__":
    main()