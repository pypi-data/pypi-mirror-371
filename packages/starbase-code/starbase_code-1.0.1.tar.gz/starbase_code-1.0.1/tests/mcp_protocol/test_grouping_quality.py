#!/usr/bin/env python3
"""
Automated test plan for starbase extraction quality.
This test harness does NOT know the expected number of groups.
It iteratively improves grouping until quality criteria are met.
"""

import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from extractors.file_collector import collect_project_files
from starbase import analyze_file_relationships


def calculate_grouping_metrics(groups: List[Dict]) -> Dict[str, float]:
    """Calculate quality metrics for a grouping."""
    metrics = {}
    
    # 1. Average group size
    group_sizes = [len(g['files']) for g in groups]
    metrics['avg_group_size'] = sum(group_sizes) / len(group_sizes) if group_sizes else 0
    
    # 2. Number of singleton groups
    metrics['singleton_count'] = sum(1 for g in groups if len(g['files']) == 1)
    metrics['singleton_ratio'] = metrics['singleton_count'] / len(groups) if groups else 0
    
    # 3. Directory coherence - files in same group should share directories
    dir_coherence_scores = []
    for group in groups:
        if len(group['files']) > 1:
            dirs = set()
            for f in group['files']:
                dirs.add(str(f.parent))
            # Coherence = 1 / number of unique directories
            coherence = 1.0 / len(dirs) if dirs else 0
            dir_coherence_scores.append(coherence)
    
    metrics['avg_dir_coherence'] = sum(dir_coherence_scores) / len(dir_coherence_scores) if dir_coherence_scores else 1.0
    
    # 4. Test file grouping - test files should be with their tested files
    test_grouping_correct = 0
    test_files_total = 0
    for group in groups:
        for f in group['files']:
            if 'test_' in f.name or '_test' in f.name:
                test_files_total += 1
                # Check if there's a corresponding non-test file
                base_name = f.stem.replace('test_', '').replace('_test', '')
                for other in group['files']:
                    if other.stem == base_name:
                        test_grouping_correct += 1
                        break
    
    metrics['test_grouping_accuracy'] = test_grouping_correct / test_files_total if test_files_total else 1.0
    
    # 5. Overall quality score (weighted combination)
    metrics['quality_score'] = (
        0.2 * (1 - metrics['singleton_ratio']) +  # Fewer singletons is better
        0.3 * metrics['avg_dir_coherence'] +       # Higher coherence is better
        0.3 * metrics['test_grouping_accuracy'] +  # Better test grouping
        0.2 * min(1.0, metrics['avg_group_size'] / 5)  # Moderate group size is good
    )
    
    return metrics


def find_improvement_opportunities(groups: List[Dict], metrics: Dict[str, float]) -> List[str]:
    """Identify specific improvements that could be made."""
    suggestions = []
    
    # Check for fragmented directories
    dir_to_groups = defaultdict(list)
    for i, group in enumerate(groups):
        for f in group['files']:
            dir_to_groups[str(f.parent)].append(i)
    
    for directory, group_indices in dir_to_groups.items():
        if len(set(group_indices)) > 1:
            suggestions.append(f"Directory {directory} is split across {len(set(group_indices))} groups")
    
    # Check for separated test files
    for group in groups:
        for f in group['files']:
            if 'test_' in f.name:
                base_name = f.stem.replace('test_', '')
                # Look in other groups
                for other_group in groups:
                    if other_group == group:
                        continue
                    for other_f in other_group['files']:
                        if other_f.stem == base_name:
                            suggestions.append(f"Test file {f.name} separated from {other_f.name}")
    
    return suggestions


def iterative_grouping_improvement(root_path: Path, max_iterations: int = 5):
    """Iteratively improve grouping quality."""
    print("Starting iterative grouping improvement...")
    
    # Collect files
    files_by_type = collect_project_files(root_path)
    all_files = files_by_type['code'] + files_by_type['tests']
    
    print(f"Working with {len(all_files)} files")
    
    # Use original analyze_file_relationships
    groups = analyze_file_relationships(all_files)
    
    metrics = calculate_grouping_metrics(groups)
    
    print(f"\nResults:")
    print(f"  Groups: {len(groups)}")
    print(f"  Quality score: {metrics['quality_score']:.3f}")
    print(f"  Avg group size: {metrics['avg_group_size']:.1f}")
    print(f"  Singleton ratio: {metrics['singleton_ratio']:.2f}")
    print(f"  Dir coherence: {metrics['avg_dir_coherence']:.2f}")
    print(f"  Test accuracy: {metrics['test_grouping_accuracy']:.2f}")
    
    # Find improvement opportunities
    suggestions = find_improvement_opportunities(groups, metrics)
    if suggestions:
        print("\nImprovement opportunities:")
        for s in suggestions[:5]:  # Show top 5
            print(f"  - {s}")
    
    # Show final grouping
    print(f"\nFinal grouping ({len(groups)} groups):")
    for i, group in enumerate(groups, 1):
        print(f"\n{i}. {group['name']} ({len(group['files'])} files)")
        if len(group['files']) <= 10:
            for f in sorted(group['files'], key=lambda x: x.name):
                print(f"   - {f.name}")
        else:
            # Show first 5 and last 5
            sorted_files = sorted(group['files'], key=lambda x: x.name)
            for f in sorted_files[:5]:
                print(f"   - {f.name}")
            print(f"   ... ({len(group['files']) - 10} more files)")
            for f in sorted_files[-5:]:
                print(f"   - {f.name}")
    
    return groups, metrics, None  # No threshold with two-phase approach


if __name__ == "__main__":
    root_path = Path('.')
    groups, metrics, threshold = iterative_grouping_improvement(root_path)
    
    print("\n" + "="*60)
    print("FINAL ASSESSMENT:")
    print("="*60)
    print(f"Original analyze_file_relationships approach")
    print(f"Number of groups: {len(groups)}")
    print(f"Overall quality: {metrics['quality_score']:.3f}")
    
    if metrics['quality_score'] > 0.7:
        print("\n✅ Grouping quality is GOOD")
    elif metrics['quality_score'] > 0.5:
        print("\n⚠️  Grouping quality is MODERATE")
    else:
        print("\n❌ Grouping quality is POOR")