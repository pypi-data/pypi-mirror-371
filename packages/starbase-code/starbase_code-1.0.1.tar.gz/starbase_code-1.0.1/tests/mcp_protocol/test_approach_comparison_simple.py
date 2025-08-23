#!/usr/bin/env python3
"""
Simple comparison test that doesn't require external dependencies.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def simple_test():
    """Run a simple comparison without needing toml."""
    from starbase import (
        assign_subdirectories_llm_with_scores,
        assign_subdirectories_heuristic_with_scores,
        analyze_file_relationships
    )
    
    root_path = Path('.')
    
    print("=" * 80)
    print("SUBDIRECTORY ASSIGNMENT APPROACH COMPARISON")
    print("=" * 80)
    
    # Get top-level groups
    top_level_files = list(root_path.glob("*.py"))
    top_level_groups = analyze_file_relationships(top_level_files)
    
    print(f"\nFound {len(top_level_groups)} top-level groups:")
    for i, group in enumerate(top_level_groups):
        print(f"  {i+1}. {group['name']} ({len(group['files'])} files)")
    
    # Get subdirectories
    subdirs = [d for d in root_path.iterdir() 
               if d.is_dir() and not d.name.startswith('.') 
               and d.name not in {'__pycache__', 'venv', '.venv'}]
    
    print(f"\nSubdirectories to assign: {len(subdirs)}")
    
    # Test LLM approach
    print("\n" + "-" * 80)
    print("APPROACH A: LLM (Token Similarity)")
    print("-" * 80)
    
    llm_assignments, llm_scores = assign_subdirectories_llm_with_scores(subdirs, top_level_groups, root_path)
    
    print("\nAssignments:")
    for subdir in sorted(subdirs, key=lambda x: x.name):
        group_idx = llm_assignments[subdir]
        if group_idx < len(top_level_groups):
            scores = llm_scores[subdir]
            max_score = max(scores) if scores else 0
            print(f"  {subdir.name:20} → {top_level_groups[group_idx]['name']:15} (max score: {max_score:.3f})")
    
    # Test Heuristic approach
    print("\n" + "-" * 80)
    print("APPROACH B: Heuristic (Rule-based)")
    print("-" * 80)
    
    heur_assignments, heur_scores = assign_subdirectories_heuristic_with_scores(subdirs, top_level_groups, root_path)
    
    print("\nAssignments:")
    for subdir in sorted(subdirs, key=lambda x: x.name):
        group_idx = heur_assignments[subdir]
        if group_idx < len(top_level_groups):
            scores = heur_scores[subdir]
            max_score = max(scores) if scores else 0
            print(f"  {subdir.name:20} → {top_level_groups[group_idx]['name']:15} (max score: {max_score:.0f})")
    
    # Test Hybrid approach (simple weighted average)
    print("\n" + "-" * 80)
    print("APPROACH A+B: Hybrid (70% Heuristic, 30% LLM)")
    print("-" * 80)
    
    hybrid_assignments = {}
    for subdir in subdirs:
        # Weighted combination
        combined_scores = []
        for i in range(len(top_level_groups)):
            llm_score = llm_scores[subdir][i] if i < len(llm_scores[subdir]) else 0
            heur_score = heur_scores[subdir][i] / 100.0 if i < len(heur_scores[subdir]) else 0
            combined = 0.3 * llm_score + 0.7 * heur_score
            combined_scores.append(combined)
        
        best_idx = combined_scores.index(max(combined_scores))
        hybrid_assignments[subdir] = best_idx
    
    print("\nAssignments:")
    for subdir in sorted(subdirs, key=lambda x: x.name):
        group_idx = hybrid_assignments[subdir]
        if group_idx < len(top_level_groups):
            print(f"  {subdir.name:20} → {top_level_groups[group_idx]['name']:15}")
    
    # Agreement analysis
    print("\n" + "=" * 80)
    print("AGREEMENT ANALYSIS")
    print("=" * 80)
    
    agreements = {
        'llm_heur': 0,
        'llm_hybrid': 0,
        'heur_hybrid': 0
    }
    
    for subdir in subdirs:
        if llm_assignments[subdir] == heur_assignments[subdir]:
            agreements['llm_heur'] += 1
        if llm_assignments[subdir] == hybrid_assignments[subdir]:
            agreements['llm_hybrid'] += 1
        if heur_assignments[subdir] == hybrid_assignments[subdir]:
            agreements['heur_hybrid'] += 1
    
    total = len(subdirs)
    print(f"LLM vs Heuristic: {agreements['llm_heur']}/{total} agree ({100*agreements['llm_heur']/total:.1f}%)")
    print(f"LLM vs Hybrid: {agreements['llm_hybrid']}/{total} agree ({100*agreements['llm_hybrid']/total:.1f}%)")
    print(f"Heuristic vs Hybrid: {agreements['heur_hybrid']}/{total} agree ({100*agreements['heur_hybrid']/total:.1f}%)")
    
    # Score analysis
    print("\n" + "=" * 80)
    print("SCORING ANALYSIS")
    print("=" * 80)
    
    print("\nAverage confidence scores by approach:")
    
    # LLM average
    llm_avg = 0
    count = 0
    for subdir in subdirs:
        if llm_assignments[subdir] < len(llm_scores[subdir]):
            llm_avg += llm_scores[subdir][llm_assignments[subdir]]
            count += 1
    llm_avg = llm_avg / count if count > 0 else 0
    
    # Heuristic average
    heur_avg = 0
    count = 0
    for subdir in subdirs:
        if heur_assignments[subdir] < len(heur_scores[subdir]):
            heur_avg += heur_scores[subdir][heur_assignments[subdir]]
            count += 1
    heur_avg = heur_avg / count if count > 0 else 0
    
    print(f"  LLM: {llm_avg:.3f}")
    print(f"  Heuristic: {heur_avg:.1f}")
    
    # Distribution analysis
    print("\n" + "=" * 80)
    print("DISTRIBUTION ANALYSIS")
    print("=" * 80)
    
    for approach_name, assignments in [("LLM", llm_assignments), ("Heuristic", heur_assignments), ("Hybrid", hybrid_assignments)]:
        print(f"\n{approach_name} distribution:")
        group_counts = {}
        for subdir, group_idx in assignments.items():
            if group_idx < len(top_level_groups):
                group_name = top_level_groups[group_idx]['name']
                group_counts[group_name] = group_counts.get(group_name, 0) + 1
        
        for group_name, count in sorted(group_counts.items()):
            print(f"  {group_name}: {count} subdirectories")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nKey findings:")
    print("1. Heuristic approach assigns all subdirectories to the main 'starbase' group")
    print("2. LLM approach may distribute subdirectories across groups based on token similarity")
    print("3. Hybrid approach typically follows heuristic due to higher weight (70%)")
    print(f"4. Agreement between approaches: {100*agreements['llm_heur']/total:.1f}%")


if __name__ == "__main__":
    simple_test()