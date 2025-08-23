#!/usr/bin/env python3
"""
Comprehensive test comparing LLM, Heuristic, and Hybrid approaches
for subdirectory assignment.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from starbase import (
    analyze_project_with_subdirectories,
    load_subdirectory_config,
    assign_subdirectories_llm_with_scores,
    assign_subdirectories_heuristic_with_scores,
    analyze_file_relationships
)


def calculate_assignment_metrics(assignments: Dict[Path, int], groups: List[Dict], subdirs: List[Path]) -> Dict:
    """Calculate quality metrics for an assignment approach."""
    metrics = {}
    
    # 1. Distribution balance - how evenly are subdirectories distributed?
    group_counts = {}
    for subdir, group_idx in assignments.items():
        group_counts[group_idx] = group_counts.get(group_idx, 0) + 1
    
    # Calculate standard deviation of distribution
    if group_counts:
        avg_count = sum(group_counts.values()) / len(groups)
        variance = sum((count - avg_count) ** 2 for count in group_counts.values()) / len(groups)
        metrics['distribution_balance'] = 1.0 / (1.0 + variance ** 0.5)  # Higher is better
    else:
        metrics['distribution_balance'] = 0.0
    
    # 2. Semantic coherence - check if related directories are grouped together
    coherence_score = 0.0
    coherence_checks = 0
    
    # Check if test directories are with their code
    for subdir, group_idx in assignments.items():
        if 'test' in subdir.name.lower():
            # Check if there's corresponding code in the same group
            group = groups[group_idx]
            if any('test' in f.name for f in group['files']):
                coherence_score += 1.0
            coherence_checks += 1
    
    metrics['semantic_coherence'] = coherence_score / coherence_checks if coherence_checks > 0 else 1.0
    
    # 3. Import coherence - directories that import from each other should be together
    # (This is a simplified check)
    import_coherence = 0.0
    import_checks = 0
    for subdir in subdirs[:5]:  # Sample check
        py_files = list(subdir.rglob("*.py"))[:3]
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple import check
                    if 'import' in content:
                        import_checks += 1
                        # Check if imports are from same group
                        assigned_group = assignments[subdir]
                        if groups[assigned_group]['files']:
                            import_coherence += 0.5  # Simplified scoring
            except:
                pass
    
    metrics['import_coherence'] = import_coherence / import_checks if import_checks > 0 else 0.5
    
    # 4. Overall score
    metrics['overall_score'] = (
        metrics['distribution_balance'] * 0.3 +
        metrics['semantic_coherence'] * 0.4 +
        metrics['import_coherence'] * 0.3
    )
    
    return metrics


def run_comparison_test(root_path: Path) -> Dict:
    """Run comprehensive comparison of all three approaches."""
    
    print("=" * 80)
    print("SUBDIRECTORY ASSIGNMENT APPROACH COMPARISON")
    print("=" * 80)
    
    # Get top-level groups first
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
    for d in sorted(subdirs, key=lambda x: x.name):
        py_count = len(list(d.rglob("*.py")))
        print(f"  - {d.name}/ ({py_count} Python files)")
    
    results = {}
    
    # Test 1: LLM Approach
    print("\n" + "-" * 80)
    print("APPROACH A: LLM (Token Similarity)")
    print("-" * 80)
    
    start_time = time.time()
    llm_assignments, llm_scores = assign_subdirectories_llm_with_scores(subdirs, top_level_groups, root_path)
    llm_time = time.time() - start_time
    
    print(f"Time taken: {llm_time:.3f}s")
    print("\nAssignments:")
    for subdir, group_idx in sorted(llm_assignments.items(), key=lambda x: x[0].name):
        if group_idx < len(top_level_groups):
            scores_str = ", ".join(f"{s:.3f}" for s in llm_scores[subdir])
            print(f"  {subdir.name:20} → {top_level_groups[group_idx]['name']:15} (scores: [{scores_str}])")
    
    llm_metrics = calculate_assignment_metrics(llm_assignments, top_level_groups, subdirs)
    results['llm'] = {
        'assignments': {str(k): v for k, v in llm_assignments.items()},
        'metrics': llm_metrics,
        'time': llm_time
    }
    
    # Test 2: Heuristic Approach
    print("\n" + "-" * 80)
    print("APPROACH B: Heuristic (Rule-based)")
    print("-" * 80)
    
    start_time = time.time()
    heur_assignments, heur_scores = assign_subdirectories_heuristic_with_scores(subdirs, top_level_groups, root_path)
    heur_time = time.time() - start_time
    
    print(f"Time taken: {heur_time:.3f}s")
    print("\nAssignments:")
    for subdir, group_idx in sorted(heur_assignments.items(), key=lambda x: x[0].name):
        if group_idx < len(top_level_groups):
            scores_str = ", ".join(f"{s:.0f}" for s in heur_scores[subdir])
            print(f"  {subdir.name:20} → {top_level_groups[group_idx]['name']:15} (scores: [{scores_str}])")
    
    heur_metrics = calculate_assignment_metrics(heur_assignments, top_level_groups, subdirs)
    results['heuristic'] = {
        'assignments': {str(k): v for k, v in heur_assignments.items()},
        'metrics': heur_metrics,
        'time': heur_time
    }
    
    # Test 3: Hybrid Approach
    print("\n" + "-" * 80)
    print("APPROACH A+B: Hybrid (Weighted Combination)")
    print("-" * 80)
    
    # Configure hybrid approach
    hybrid_config = {
        "assignment": {"method": "hybrid"},
        "hybrid": {"strategy": "weighted", "llm_weight": 0.3, "heuristic_weight": 0.7}
    }
    
    start_time = time.time()
    hybrid_groups = analyze_project_with_subdirectories(root_path, hybrid_config)
    hybrid_time = time.time() - start_time
    
    # Extract assignments from hybrid results
    hybrid_assignments = {}
    for group in hybrid_groups:
        if 'subdirectories' in group:
            for subdir in group['subdirectories']:
                group_idx = top_level_groups.index(
                    next(g for g in top_level_groups if g['name'] == group['name'])
                )
                hybrid_assignments[subdir] = group_idx
    
    print(f"Time taken: {hybrid_time:.3f}s")
    print("\nAssignments:")
    for subdir, group_idx in sorted(hybrid_assignments.items(), key=lambda x: x[0].name):
        if group_idx < len(top_level_groups):
            print(f"  {subdir.name:20} → {top_level_groups[group_idx]['name']:15}")
    
    hybrid_metrics = calculate_assignment_metrics(hybrid_assignments, top_level_groups, subdirs)
    results['hybrid'] = {
        'assignments': {str(k): v for k, v in hybrid_assignments.items()},
        'metrics': hybrid_metrics,
        'time': hybrid_time
    }
    
    # Summary Comparison
    print("\n" + "=" * 80)
    print("SUMMARY COMPARISON")
    print("=" * 80)
    
    print("\nMetrics Comparison:")
    print(f"{'Approach':15} {'Distribution':>15} {'Semantic':>15} {'Import':>15} {'Overall':>15} {'Time (s)':>10}")
    print("-" * 85)
    
    for approach, label in [('llm', 'A: LLM'), ('heuristic', 'B: Heuristic'), ('hybrid', 'A+B: Hybrid')]:
        m = results[approach]['metrics']
        print(f"{label:15} {m['distribution_balance']:>15.3f} {m['semantic_coherence']:>15.3f} "
              f"{m['import_coherence']:>15.3f} {m['overall_score']:>15.3f} {results[approach]['time']:>10.3f}")
    
    # Agreement Analysis
    print("\n" + "-" * 80)
    print("AGREEMENT ANALYSIS")
    print("-" * 80)
    
    total_dirs = len(subdirs)
    llm_heur_agree = sum(1 for d in subdirs if llm_assignments[d] == heur_assignments[d])
    llm_hybrid_agree = sum(1 for d in subdirs if d in hybrid_assignments and llm_assignments[d] == hybrid_assignments[d])
    heur_hybrid_agree = sum(1 for d in subdirs if d in hybrid_assignments and heur_assignments[d] == hybrid_assignments[d])
    
    print(f"LLM vs Heuristic agreement: {llm_heur_agree}/{total_dirs} ({100*llm_heur_agree/total_dirs:.1f}%)")
    print(f"LLM vs Hybrid agreement: {llm_hybrid_agree}/{total_dirs} ({100*llm_hybrid_agree/total_dirs:.1f}%)")
    print(f"Heuristic vs Hybrid agreement: {heur_hybrid_agree}/{total_dirs} ({100*heur_hybrid_agree/total_dirs:.1f}%)")
    
    # Winner Declaration
    print("\n" + "=" * 80)
    print("WINNER ANALYSIS")
    print("=" * 80)
    
    best_approach = max(results.items(), key=lambda x: x[1]['metrics']['overall_score'])
    print(f"\nBest Overall Score: {best_approach[0].upper()} (score: {best_approach[1]['metrics']['overall_score']:.3f})")
    
    print("\nCategory Winners:")
    for metric in ['distribution_balance', 'semantic_coherence', 'import_coherence']:
        best = max(results.items(), key=lambda x: x[1]['metrics'][metric])
        print(f"  {metric.replace('_', ' ').title()}: {best[0].upper()} ({best[1]['metrics'][metric]:.3f})")
    
    fastest = min(results.items(), key=lambda x: x[1]['time'])
    print(f"  Fastest: {fastest[0].upper()} ({fastest[1]['time']:.3f}s)")
    
    return results


if __name__ == "__main__":
    root_path = Path('.')
    results = run_comparison_test(root_path)
    
    # Save results to JSON for further analysis
    with open('approach_comparison_results.json', 'w') as f:
        # Convert Path objects to strings for JSON serialization
        json_results = {}
        for approach, data in results.items():
            json_results[approach] = {
                'metrics': data['metrics'],
                'time': data['time'],
                'assignment_count': len(data['assignments'])
            }
        json.dump(json_results, f, indent=2)
    
    print(f"\n\nDetailed results saved to approach_comparison_results.json")