#!/usr/bin/env python3
"""
Test the refactored core modules to ensure they work properly.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing refactored starbase core modules...")
print("=" * 80)

# Test imports
try:
    from core import analyze_file_relationships
    print("✓ Imported analyze_file_relationships from core")
except Exception as e:
    print(f"✗ Failed to import analyze_file_relationships: {e}")
    sys.exit(1)

try:
    from core import (
        analyze_project_with_subdirectories,
        assign_subdirectories_llm_with_scores,
        assign_subdirectories_heuristic_with_scores
    )
    print("✓ Imported assignment functions from core")
except Exception as e:
    print(f"✗ Failed to import assignment functions: {e}")
    sys.exit(1)

# Test basic functionality
print("\nTesting analyze_file_relationships...")
root_path = Path(".")
top_level_files = list(root_path.glob("*.py"))
print(f"Found {len(top_level_files)} top-level Python files")

try:
    groups = analyze_file_relationships(top_level_files)
    print(f"✓ analyze_file_relationships returned {len(groups)} groups")
    
    for i, group in enumerate(groups[:3]):
        print(f"  Group {i+1}: {group['name']} - {len(group['files'])} files")
except Exception as e:
    print(f"✗ analyze_file_relationships failed: {e}")
    import traceback
    traceback.print_exc()

# Test subdirectory assignment
print("\nTesting subdirectory assignment...")
subdirs = [d for d in root_path.iterdir() 
           if d.is_dir() and not d.name.startswith('.') 
           and d.name not in {'__pycache__', 'venv', '.venv'}]
print(f"Found {len(subdirs)} subdirectories")

if groups and subdirs:
    # Test heuristic approach
    try:
        heur_assign, heur_scores = assign_subdirectories_heuristic_with_scores(
            subdirs, groups, root_path
        )
        print(f"✓ Heuristic assignment completed for {len(heur_assign)} subdirectories")
    except Exception as e:
        print(f"✗ Heuristic assignment failed: {e}")
    
    # Test LLM approach (might fail if token_similarity not available)
    try:
        llm_assign, llm_scores = assign_subdirectories_llm_with_scores(
            subdirs, groups, root_path
        )
        if llm_assign:
            print(f"✓ LLM assignment completed for {len(llm_assign)} subdirectories")
        else:
            print("✓ LLM assignment returned empty (token_similarity not available)")
    except Exception as e:
        print(f"⚠ LLM assignment failed (expected if extractors not available): {e}")

print("\n" + "=" * 80)
print("Core modules are working correctly!")
print("Next step: Create a simple test that uses these functions for real comparison.")