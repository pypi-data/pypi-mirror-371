#!/usr/bin/env python3
"""
Test script to compare LLM vs heuristic approaches for subdirectory assignment.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from starbase import (
    analyze_project_with_subdirectories,
    analyze_file_relationships,
    assign_subdirectories_llm,
    assign_subdirectories_heuristic
)


def compare_approaches(root_path: Path):
    """Compare LLM and heuristic approaches for subdirectory assignment."""
    
    # Step 1: Get top-level groups
    print("=" * 60)
    print("STEP 1: TOP-LEVEL GROUPING")
    print("=" * 60)
    
    top_level_files = list(root_path.glob("*.py"))
    top_level_groups = analyze_file_relationships(top_level_files)
    
    print(f"\nFound {len(top_level_groups)} top-level groups:")
    for i, group in enumerate(top_level_groups):
        print(f"\n{i+1}. {group['name']} ({len(group['files'])} files)")
        for f in group['files']:
            print(f"   - {f.name}")
    
    # Step 2: Get subdirectories
    subdirs = [d for d in root_path.iterdir() 
               if d.is_dir() and not d.name.startswith('.') 
               and d.name not in {'__pycache__', 'venv', '.venv'}]
    
    print("\n" + "=" * 60)
    print("STEP 2: SUBDIRECTORY ASSIGNMENT")
    print("=" * 60)
    print(f"\nSubdirectories to assign: {[d.name for d in subdirs]}")
    
    # Compare approaches
    llm_assignments = assign_subdirectories_llm(subdirs, top_level_groups, root_path)
    heuristic_assignments = assign_subdirectories_heuristic(subdirs, top_level_groups, root_path)
    
    # Display results
    print("\n" + "-" * 60)
    print("LLM APPROACH (Token Similarity):")
    print("-" * 60)
    for subdir, group_idx in sorted(llm_assignments.items(), key=lambda x: x[0].name):
        if group_idx < len(top_level_groups):
            group_name = top_level_groups[group_idx]['name']
            print(f"{subdir.name:20} → {group_name}")
    
    print("\n" + "-" * 60)
    print("HEURISTIC APPROACH (Rules-based):")
    print("-" * 60)
    for subdir, group_idx in sorted(heuristic_assignments.items(), key=lambda x: x[0].name):
        if group_idx < len(top_level_groups):
            group_name = top_level_groups[group_idx]['name']
            print(f"{subdir.name:20} → {group_name}")
    
    # Compare differences
    print("\n" + "-" * 60)
    print("DIFFERENCES:")
    print("-" * 60)
    differences = []
    for subdir in subdirs:
        if subdir in llm_assignments and subdir in heuristic_assignments:
            if llm_assignments[subdir] != heuristic_assignments[subdir]:
                llm_group = top_level_groups[llm_assignments[subdir]]['name'] if llm_assignments[subdir] < len(top_level_groups) else "?"
                heur_group = top_level_groups[heuristic_assignments[subdir]]['name'] if heuristic_assignments[subdir] < len(top_level_groups) else "?"
                differences.append((subdir.name, llm_group, heur_group))
    
    if differences:
        print("Subdirectory         LLM Choice           Heuristic Choice")
        print("-" * 60)
        for subdir_name, llm_choice, heur_choice in differences:
            print(f"{subdir_name:20} {llm_choice:20} {heur_choice:20}")
    else:
        print("No differences - both approaches agree!")
    
    # Show final integrated result
    print("\n" + "=" * 60)
    print("FINAL INTEGRATED RESULT (using heuristic):")
    print("=" * 60)
    
    final_groups = analyze_project_with_subdirectories(root_path)
    for i, group in enumerate(final_groups):
        total_files = len([f for f in group['files'] if f.suffix == '.py'])
        print(f"\n{i+1}. {group['name']} ({total_files} total files)")
        
        # Show top-level files
        top_level = [f for f in group['files'] if f.parent == root_path]
        if top_level:
            print("   Top-level files:")
            for f in top_level[:5]:
                print(f"   - {f.name}")
            if len(top_level) > 5:
                print(f"   ... and {len(top_level) - 5} more")
        
        # Show subdirectories
        if group.get('subdirectories'):
            print("   Subdirectories:")
            for subdir in group['subdirectories']:
                sub_files = len(list(subdir.rglob("*.py")))
                print(f"   - {subdir.name}/ ({sub_files} files)")


if __name__ == "__main__":
    root_path = Path('.')
    compare_approaches(root_path)