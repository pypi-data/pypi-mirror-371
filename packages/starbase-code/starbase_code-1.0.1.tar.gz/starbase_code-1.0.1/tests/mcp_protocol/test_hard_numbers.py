#!/usr/bin/env python3
"""
Get hard numbers on how each approach actually performs.
"""

import sys
from pathlib import Path
import ast
import re
from collections import defaultdict

def extract_tokens(file_path):
    """Simple token extraction."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Extract identifiers
        tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', content)
        return set(tokens)
    except:
        return set()

def calculate_similarity(file1, file2):
    """Calculate Jaccard similarity."""
    tokens1 = extract_tokens(file1)
    tokens2 = extract_tokens(file2)
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    return len(intersection) / len(union) if union else 0.0

def extract_imports(file_path):
    """Extract local imports."""
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
    except:
        pass
    return imports

def main():
    root = Path('.')
    
    # Get all Python files
    all_py_files = list(root.rglob("*.py"))
    all_py_files = [f for f in all_py_files if '__pycache__' not in str(f) and '.venv' not in str(f)]
    
    # Get top-level files and subdirectories
    top_level = [f for f in all_py_files if f.parent == root]
    subdirs = [d for d in root.iterdir() 
               if d.is_dir() and not d.name.startswith('.') 
               and d.name not in {'__pycache__', 'venv', '.venv'}]
    
    # Count files per subdirectory
    subdir_files = {}
    for subdir in subdirs:
        py_files = [f for f in all_py_files if str(subdir) in str(f)]
        subdir_files[subdir] = py_files
    
    print("HARD NUMBERS - SUBDIRECTORY ASSIGNMENT TEST")
    print("=" * 80)
    print(f"Total Python files: {len(all_py_files)}")
    print(f"Top-level files: {len(top_level)}")
    print(f"Subdirectories: {len(subdirs)}")
    print(f"Files in subdirectories: {sum(len(files) for files in subdir_files.values())}")
    
    # Simple grouping - assume all top-level files belong to "starbase" group
    # (This matches what the actual code does)
    groups = [{
        'name': 'starbase',
        'files': [f for f in top_level if f.name not in ['calc.py', 'test_grouping_quality.py']]
    }]
    
    # Add calc.py as separate group if it exists
    calc_py = [f for f in top_level if f.name == 'calc.py']
    if calc_py:
        groups.append({'name': 'calc', 'files': calc_py})
    
    # Add test_grouping_quality as separate group if exists
    test_quality = [f for f in top_level if f.name == 'test_grouping_quality.py']
    if test_quality:
        groups.append({'name': 'test_grouping_quality', 'files': test_quality})
    
    print(f"\nGroups: {len(groups)}")
    for g in groups:
        print(f"  - {g['name']}: {len(g['files'])} files")
    
    # Test each approach
    results = {}
    
    # APPROACH A: LLM (Token Similarity)
    print("\n" + "-" * 80)
    print("APPROACH A: LLM (Token Similarity)")
    print("-" * 80)
    
    llm_assignments = {}
    llm_scores = defaultdict(list)
    
    for subdir in subdirs:
        py_files = subdir_files[subdir]
        if not py_files:
            llm_assignments[subdir] = 0
            continue
        
        best_group = 0
        best_score = -1
        
        for g_idx, group in enumerate(groups):
            similarities = []
            # Sample up to 5 files from each
            for sub_file in py_files[:5]:
                for group_file in group['files'][:5]:
                    sim = calculate_similarity(sub_file, group_file)
                    similarities.append(sim)
            
            avg_sim = sum(similarities) / len(similarities) if similarities else 0
            llm_scores[subdir].append(avg_sim)
            
            if avg_sim > best_score:
                best_score = avg_sim
                best_group = g_idx
        
        llm_assignments[subdir] = best_group
    
    # Count assignments
    llm_counts = defaultdict(list)
    for subdir, group_idx in llm_assignments.items():
        if group_idx < len(groups):
            llm_counts[groups[group_idx]['name']].append(subdir)
    
    print("Assignments:")
    for group_name, subdirs_assigned in llm_counts.items():
        print(f"  {group_name}: {len(subdirs_assigned)} subdirectories")
        for s in subdirs_assigned:
            score = max(llm_scores[s]) if s in llm_scores else 0
            print(f"    - {s.name} (score: {score:.3f})")
    
    unassigned_llm = len(subdirs) - sum(len(v) for v in llm_counts.values())
    accuracy_llm = sum(len(v) for k, v in llm_counts.items() if k == 'starbase') / len(subdirs) * 100
    
    results['LLM'] = {
        'assigned': sum(len(v) for v in llm_counts.values()),
        'unassigned': unassigned_llm,
        'accuracy': accuracy_llm
    }
    
    # APPROACH B: Heuristic
    print("\n" + "-" * 80)
    print("APPROACH B: Heuristic (Rule-based)")
    print("-" * 80)
    
    heur_assignments = {}
    heur_scores = defaultdict(list)
    
    for subdir in subdirs:
        py_files = subdir_files[subdir]
        best_group = 0
        best_score = -1
        
        for g_idx, group in enumerate(groups):
            score = 0.0
            
            # Check imports
            for py_file in py_files[:10]:
                imports = extract_imports(py_file)
                for imp in imports:
                    for group_file in group['files']:
                        if imp in group_file.stem:
                            score += 10.0
                            break
            
            # Name matching
            subdir_name = subdir.name.lower()
            group_name = group['name'].lower()
            
            if group_name in subdir_name or subdir_name in group_name:
                score += 20.0
            elif any(part in group_name for part in subdir_name.split('_')):
                score += 10.0
            
            # Special cases
            if subdir.name == 'tests' and ('test' in group_name or group['name'] == 'starbase'):
                score += 15.0
            elif subdir.name in ['src', 'lib', 'analyzers', 'extractors', 'config'] and group['name'] == 'starbase':
                score += 15.0
            
            heur_scores[subdir].append(score)
            
            if score > best_score:
                best_score = score
                best_group = g_idx
        
        heur_assignments[subdir] = best_group
    
    # Count assignments
    heur_counts = defaultdict(list)
    for subdir, group_idx in heur_assignments.items():
        if group_idx < len(groups):
            heur_counts[groups[group_idx]['name']].append(subdir)
    
    print("Assignments:")
    for group_name, subdirs_assigned in heur_counts.items():
        print(f"  {group_name}: {len(subdirs_assigned)} subdirectories")
        for s in subdirs_assigned:
            score = max(heur_scores[s]) if s in heur_scores else 0
            print(f"    - {s.name} (score: {score:.0f})")
    
    unassigned_heur = len(subdirs) - sum(len(v) for v in heur_counts.values())
    accuracy_heur = sum(len(v) for k, v in heur_counts.items() if k == 'starbase') / len(subdirs) * 100
    
    results['Heuristic'] = {
        'assigned': sum(len(v) for v in heur_counts.values()),
        'unassigned': unassigned_heur,
        'accuracy': accuracy_heur
    }
    
    # APPROACH A+B: Hybrid
    print("\n" + "-" * 80)
    print("APPROACH A+B: Hybrid (70% Heuristic, 30% LLM)")
    print("-" * 80)
    
    hybrid_assignments = {}
    
    for subdir in subdirs:
        combined_scores = []
        for i in range(len(groups)):
            llm_s = llm_scores[subdir][i] if i < len(llm_scores[subdir]) else 0
            heur_s = heur_scores[subdir][i] / 100.0 if i < len(heur_scores[subdir]) else 0
            combined = 0.3 * llm_s + 0.7 * heur_s
            combined_scores.append(combined)
        
        hybrid_assignments[subdir] = combined_scores.index(max(combined_scores))
    
    # Count assignments
    hybrid_counts = defaultdict(list)
    for subdir, group_idx in hybrid_assignments.items():
        if group_idx < len(groups):
            hybrid_counts[groups[group_idx]['name']].append(subdir)
    
    print("Assignments:")
    for group_name, subdirs_assigned in hybrid_counts.items():
        print(f"  {group_name}: {len(subdirs_assigned)} subdirectories")
        for s in subdirs_assigned:
            print(f"    - {s.name}")
    
    unassigned_hybrid = len(subdirs) - sum(len(v) for v in hybrid_counts.values())
    accuracy_hybrid = sum(len(v) for k, v in hybrid_counts.items() if k == 'starbase') / len(subdirs) * 100
    
    results['Hybrid'] = {
        'assigned': sum(len(v) for v in hybrid_counts.values()),
        'unassigned': unassigned_hybrid,
        'accuracy': accuracy_hybrid
    }
    
    # FINAL SUMMARY
    print("\n" + "=" * 80)
    print("HARD NUMBERS SUMMARY")
    print("=" * 80)
    print(f"Total subdirectories to assign: {len(subdirs)}")
    print(f"Expected: All should go to 'starbase' group (based on project structure)")
    print()
    
    for approach, data in results.items():
        print(f"{approach}:")
        print(f"  - Assigned correctly to starbase: {data['accuracy']:.1f}%")
        print(f"  - Left unassigned: {data['unassigned']} subdirectories ({data['unassigned']/len(subdirs)*100:.1f}%)")
        print(f"  - Total assigned: {data['assigned']}/{len(subdirs)}")
    
    print("\nDETAILED BREAKDOWN:")
    print(f"Files that should be organized: {len(all_py_files)} total Python files")
    print(f"Files actually organized:")
    
    # Count total files organized by each approach
    for approach, counts in [('LLM', llm_counts), ('Heuristic', heur_counts), ('Hybrid', hybrid_counts)]:
        total_files = len(top_level)  # Start with top-level files
        for subdirs_in_group in counts.values():
            for subdir in subdirs_in_group:
                total_files += len(subdir_files[subdir])
        
        print(f"  {approach}: {total_files}/{len(all_py_files)} files ({total_files/len(all_py_files)*100:.1f}%)")


if __name__ == "__main__":
    main()