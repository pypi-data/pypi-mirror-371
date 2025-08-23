#\!/usr/bin/env python3
"""
Real comparison test using the refactored core functions.
This provides actual scores for LLM vs heuristic vs hybrid approaches.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import (
    analyze_file_relationships,
    assign_subdirectories_llm_with_scores,
    assign_subdirectories_heuristic_with_scores
)

def main():
    root_path = Path(".")
    
    print("REAL COMPARISON TEST - ACTUAL SCORES")
    print("=" * 80)
    
    # Step 1: Get top-level groups
    top_level_files = list(root_path.glob("*.py"))
    groups = analyze_file_relationships(top_level_files)
    
    print(f"\nGroups found: {len(groups)}")
    for i, group in enumerate(groups):
        print(f"  {i}. {group['name']} - {len(group['files'])} files")
    
    # Step 2: Get subdirectories
    subdirs = [d for d in root_path.iterdir() 
               if d.is_dir() and not d.name.startswith('.') 
               and d.name not in {'__pycache__', 'venv', '.venv', 'test_extract'}]
    
    print(f"\nSubdirectories to assign: {len(subdirs)}")
    for d in sorted(subdirs, key=lambda x: x.name):
        print(f"  - {d.name}")
    
    # Step 3: Run each approach
    print("\n" + "-" * 80)
    print("APPROACH A: HEURISTIC (Rule-based)")
    print("-" * 80)
    
    heur_assignments, heur_scores = assign_subdirectories_heuristic_with_scores(subdirs, groups, root_path)
    
    for subdir in sorted(subdirs, key=lambda x: x.name):
        idx = heur_assignments[subdir]
        group_name = groups[idx]['name'] if idx < len(groups) else "INVALID"
        score = max(heur_scores[subdir]) if heur_scores[subdir] else 0
        print(f"  {subdir.name:20} -> {group_name:15} (score: {score:.0f})")
    
    print("\n" + "-" * 80)
    print("APPROACH B: LLM (Token Similarity)")
    print("-" * 80)
    
    llm_assignments, llm_scores = assign_subdirectories_llm_with_scores(subdirs, groups, root_path)
    
    if llm_assignments:
        for subdir in sorted(subdirs, key=lambda x: x.name):
            idx = llm_assignments[subdir]
            group_name = groups[idx]['name'] if idx < len(groups) else "INVALID"
            score = max(llm_scores[subdir]) if llm_scores[subdir] else 0
            print(f"  {subdir.name:20} -> {group_name:15} (score: {score:.3f})")
    else:
        print("  LLM approach not available (token_similarity missing)")
    
    print("\n" + "-" * 80)
    print("APPROACH A+B: 50/50 HYBRID")
    print("-" * 80)
    
    if llm_assignments and heur_assignments:
        hybrid_assignments = {}
        for subdir in subdirs:
            combined_scores = []
            for i in range(len(groups)):
                llm = llm_scores[subdir][i] if i < len(llm_scores[subdir]) else 0
                heur = heur_scores[subdir][i] / 100.0 if i < len(heur_scores[subdir]) else 0
                combined = 0.5 * llm + 0.5 * heur
                combined_scores.append(combined)
            hybrid_assignments[subdir] = combined_scores.index(max(combined_scores))
        
        for subdir in sorted(subdirs, key=lambda x: x.name):
            idx = hybrid_assignments[subdir]
            group_name = groups[idx]['name'] if idx < len(groups) else "INVALID"
            print(f"  {subdir.name:20} -> {group_name}")
    else:
        print("  Hybrid not available (requires both approaches)")
    
    # Step 4: Calculate accuracy
    print("\n" + "=" * 80)
    print("ACCURACY ANALYSIS")
    print("=" * 80)
    
    # Assume the main group is the one with most files (starbase)
    main_idx = max(range(len(groups)), key=lambda i: len(groups[i]['files']))
    main_name = groups[main_idx]['name']
    
    print(f"\nMain group: {main_name} (has {len(groups[main_idx]['files'])} files)")
    print("Assuming all subdirectories should be assigned to this group.")
    
    # Calculate accuracy for each approach
    approaches = [("Heuristic", heur_assignments)]
    if llm_assignments:
        approaches.append(("LLM", llm_assignments))
        if 'hybrid_assignments' in locals():
            approaches.append(("50/50 Hybrid", hybrid_assignments))
    
    for name, assignments in approaches:
        correct = sum(1 for idx in assignments.values() if idx == main_idx)
        total = len(assignments)
        accuracy = 100 * correct / total if total > 0 else 0
        
        print(f"\n{name} Approach:")
        print(f"  Correct assignments: {correct}/{total} ({accuracy:.1f}%)")
        
        incorrect = [(s.name, groups[assignments[s]]['name']) 
                     for s in assignments 
                     if assignments[s] != main_idx]
        
        if incorrect:
            print(f"  Incorrect assignments:")
            for subdir_name, wrong_group in sorted(incorrect):
                print(f"    {subdir_name} -> {wrong_group}")
    
    # Configuration recommendation
    print("\n" + "=" * 80)
    print("CONFIGURATION RECOMMENDATION")
    print("=" * 80)
    
    if llm_assignments:
        # Compare approaches
        heur_correct = sum(1 for idx in heur_assignments.values() if idx == main_idx)
        llm_correct = sum(1 for idx in llm_assignments.values() if idx == main_idx)
        
        if 'hybrid_assignments' in locals():
            hybrid_correct = sum(1 for idx in hybrid_assignments.values() if idx == main_idx)
            
            best_score = max(heur_correct, llm_correct, hybrid_correct)
            if hybrid_correct == best_score:
                print("Recommendation: Use HYBRID approach (method = 'hybrid')")
                print("This combines the strengths of both approaches.")
            elif heur_correct == best_score:
                print("Recommendation: Use HEURISTIC approach (method = 'heuristic')")
                print("Rule-based approach performs best for this codebase.")
            else:
                print("Recommendation: Use LLM approach (method = 'llm')")
                print("Token similarity performs best for this codebase.")
        else:
            if heur_correct >= llm_correct:
                print("Recommendation: Use HEURISTIC approach (method = 'heuristic')")
                print("Rule-based approach performs equal or better.")
            else:
                print("Recommendation: Use LLM approach (method = 'llm')")
                print("Token similarity performs better.")
    else:
        print("Recommendation: Use HEURISTIC approach (method = 'heuristic')")
        print("(LLM approach not available)")
    
    print("\nUpdate config/subdirectory_assignment.toml with your preferred method.")

if __name__ == "__main__":
    main()
