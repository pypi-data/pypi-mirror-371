#!/usr/bin/env python3
"""
Test the complete grouping pipeline with proper metrics.
Shows all three phases clearly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.analysis import analyze_file_relationships
from core.assignment import analyze_project_with_subdirectories

def main():
    """Test complete grouping pipeline."""
    root_path = Path('.')
    
    print("COMPLETE GROUPING PIPELINE TEST")
    print("=" * 80)
    
    # PHASE 1: Initial import-based grouping (top-level files only)
    print("\nPHASE 1: Import-based grouping (top-level files only)")
    print("-" * 60)
    
    top_level_files = list(root_path.glob("*.py"))
    print(f"Top-level Python files: {len(top_level_files)}")
    
    # Get import relationships
    from core.analysis import extract_local_imports, find_connected_components
    import_map = {}
    for file in top_level_files:
        if file.suffix == '.py':
            imports = extract_local_imports(file)
            import_map[file] = imports.intersection(set(top_level_files))
    
    # Show connected components before semantic analysis
    components = find_connected_components(import_map)
    print(f"\nConnected components from imports: {len(components)}")
    
    # Find the starbase component
    starbase_component = None
    for comp in components:
        if any('starbase.py' == f.name for f in comp):
            starbase_component = comp
            break
    
    if starbase_component:
        print(f"\nStarbase component (import-connected): {len(starbase_component)} files")
        for f in sorted(starbase_component, key=lambda x: x.name):
            print(f"  - {f.name}")
    
    # PHASE 2: Semantic analysis (merges groups based on references)
    print("\n\nPHASE 2: After semantic analysis")
    print("-" * 60)
    
    # This runs the full analyze_file_relationships which includes semantic merging
    groups_after_semantic = analyze_file_relationships(top_level_files)
    
    print(f"Groups after semantic merging: {len(groups_after_semantic)}")
    
    # Find starbase group
    starbase_group = next((g for g in groups_after_semantic if g['name'] == 'starbase'), None)
    
    if starbase_group:
        print(f"\nStarbase group (after semantic merge): {len(starbase_group['files'])} files")
        
        # Show which files were added by semantic analysis
        added_by_semantic = set(starbase_group['files']) - starbase_component
        if added_by_semantic:
            print("\nFiles added by semantic analysis:")
            for f in sorted(added_by_semantic, key=lambda x: x.name):
                print(f"  + {f.name}")
    
    # PHASE 3: Subdirectory assignment
    print("\n\nPHASE 3: With subdirectory assignment")
    print("-" * 60)
    
    # This is what menu.py actually calls
    final_groups = analyze_project_with_subdirectories(root_path)
    
    print(f"Final groups with subdirectories: {len(final_groups)}")
    
    # Show complete starbase group
    starbase_final = next((g for g in final_groups if g['name'] == 'starbase'), None)
    
    if starbase_final:
        # Count files
        top_level_count = len([f for f in starbase_final['files'] if f.parent == root_path])
        subdir_count = len(starbase_final.get('subdirectories', []))
        total_files = len(starbase_final['files'])
        
        print(f"\nStarbase group (FINAL):")
        print(f"  Top-level files: {top_level_count}")
        print(f"  Subdirectories: {subdir_count}")
        print(f"  TOTAL FILES: {total_files}")
        
        if 'subdirectories' in starbase_final:
            print("\n  Subdirectories:")
            for subdir in sorted(starbase_final['subdirectories'], key=lambda x: x.name):
                subdir_files = len([f for f in starbase_final['files'] 
                                  if f.parent == subdir or any(p == subdir for p in f.parents)])
                print(f"    📁 {subdir.name}/ ({subdir_files} files)")
    
    # Summary metrics
    print("\n" + "=" * 80)
    print("SUMMARY METRICS")
    print("=" * 80)
    
    print(f"\nPhase 1 (imports only):")
    print(f"  - Starbase group: {len(starbase_component) if starbase_component else 0} files")
    
    print(f"\nPhase 2 (+ semantic analysis):")
    print(f"  - Starbase group: {len(starbase_group['files']) if starbase_group else 0} files")
    print(f"  - Files absorbed: {len(added_by_semantic) if 'added_by_semantic' in locals() else 0}")
    
    print(f"\nPhase 3 (+ subdirectories):")
    print(f"  - Starbase group: {total_files if 'total_files' in locals() else 0} files")
    print(f"  - Top-level: {top_level_count if 'top_level_count' in locals() else 0}")
    print(f"  - In subdirs: {total_files - top_level_count if 'total_files' in locals() and 'top_level_count' in locals() else 0}")
    
    # Verify against your expected numbers
    print("\n" + "-" * 60)
    print("VALIDATION:")
    if 'total_files' in locals() and total_files >= 49:
        print("✅ Starbase has 49+ files as expected!")
    else:
        print(f"❌ Starbase has {total_files if 'total_files' in locals() else 0} files, expected 49+")

if __name__ == "__main__":
    main()