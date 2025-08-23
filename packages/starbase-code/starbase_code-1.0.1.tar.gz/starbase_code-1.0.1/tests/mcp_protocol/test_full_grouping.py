#!/usr/bin/env python3
"""
Test the complete grouping system with subdirectories.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from starbase import analyze_project_with_subdirectories


def test_full_grouping():
    """Test the complete project grouping."""
    root_path = Path('.')
    groups = analyze_project_with_subdirectories(root_path)
    
    print("=" * 60)
    print("FULL PROJECT GROUPING RESULTS")
    print("=" * 60)
    
    total_files = sum(len([f for f in g['files'] if f.suffix == '.py']) for g in groups)
    print(f"\nTotal Python files: {total_files}")
    print(f"Number of groups: {len(groups)}")
    
    for i, group in enumerate(groups, 1):
        py_files = [f for f in group['files'] if f.suffix == '.py']
        print(f"\n{i}. {group['name']} ({len(py_files)} files)")
        
        # Show top-level files
        top_level = [f for f in py_files if f.parent == root_path]
        if top_level:
            print("   Top-level:")
            for f in sorted(top_level, key=lambda x: x.name):
                print(f"      - {f.name}")
        
        # Show subdirectories
        if group.get('subdirectories'):
            print("   Subdirectories:")
            for subdir in sorted(group['subdirectories'], key=lambda x: x.name):
                subdir_py_files = [f for f in py_files if str(subdir) in str(f)]
                print(f"      - {subdir.name}/ ({len(subdir_py_files)} files)")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    # Check if all subdirectories were assigned
    all_subdirs = [d for d in root_path.iterdir() 
                   if d.is_dir() and not d.name.startswith('.') 
                   and d.name not in {'__pycache__', 'venv', '.venv'}]
    
    assigned_subdirs = set()
    for group in groups:
        if group.get('subdirectories'):
            assigned_subdirs.update(group['subdirectories'])
    
    unassigned = set(all_subdirs) - assigned_subdirs
    
    print(f"Total subdirectories: {len(all_subdirs)}")
    print(f"Assigned subdirectories: {len(assigned_subdirs)}")
    print(f"Unassigned subdirectories: {len(unassigned)}")
    
    if unassigned:
        print("\nUnassigned directories:")
        for d in sorted(unassigned, key=lambda x: x.name):
            print(f"   - {d.name}/")
    
    # Quality assessment
    print("\nQuality Assessment:")
    if len(groups) <= 5 and len(unassigned) == 0:
        print("✅ Excellent - Clean grouping with all directories assigned")
    elif len(groups) <= 10 and len(unassigned) <= 2:
        print("⚠️  Good - Reasonable grouping with minor issues")
    else:
        print("❌ Poor - Too many groups or unassigned directories")


if __name__ == "__main__":
    test_full_grouping()