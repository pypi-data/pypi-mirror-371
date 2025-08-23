#!/usr/bin/env python3
"""
Test using the actual starbase module functions directly.
"""

import subprocess
import sys
import json

# Run starbase's actual extract command to see the groups
print("Running actual starbase extract command to see groups...")
result = subprocess.run([sys.executable, "starbase.py", "extract", ".", "--analyze-only"], 
                       capture_output=True, text=True)

if result.returncode != 0:
    print("Fallback: Running manual analysis...")
    
# Create a test that imports and runs the actual functions
test_code = '''
import sys
from pathlib import Path

# Temporarily modify starbase.py to not initialize at module level
starbase_content = Path("starbase.py").read_text()
starbase_content = starbase_content.replace("manager = StarbaseManager()", "manager = None  # Disabled for test")
starbase_content = starbase_content.replace("db = tinydb.TinyDB", "db = None  # Disabled for test")

# Write modified version
Path("starbase_test.py").write_text(starbase_content)

# Now import from the modified version
from starbase_test import (
    analyze_file_relationships,
    assign_subdirectories_llm_with_scores,
    assign_subdirectories_heuristic_with_scores
)

# Clean up
Path("starbase_test.py").unlink()

# Run the actual test
root = Path(".")
print("REAL STARBASE FUNCTIONS TEST")
print("=" * 80)

# Get groups
top_level = list(root.glob("*.py"))
groups = analyze_file_relationships(top_level)

print(f"\\nGroups found: {len(groups)}")
for i, g in enumerate(groups):
    print(f"{i}. {g['name']} - {len(g['files'])} files")

# Get subdirs
subdirs = [d for d in root.iterdir() 
           if d.is_dir() and not d.name.startswith('.') 
           and d.name not in {'__pycache__', 'venv', '.venv', 'test_extract'}]

print(f"\\nSubdirectories: {len(subdirs)}")

# Test each approach
print("\\n" + "-" * 80)
print("LLM APPROACH")
llm_assign, llm_scores = assign_subdirectories_llm_with_scores(subdirs, groups, root)

llm_dist = {}
for s, idx in llm_assign.items():
    gname = groups[idx]['name'] if idx < len(groups) else "ERROR"
    if gname not in llm_dist:
        llm_dist[gname] = []
    llm_dist[gname].append(s.name)

for gname, dirs in sorted(llm_dist.items()):
    print(f"\\n{gname}: {len(dirs)} subdirs")
    for d in sorted(dirs):
        print(f"  - {d}")

print("\\n" + "-" * 80)
print("HEURISTIC APPROACH")
heur_assign, heur_scores = assign_subdirectories_heuristic_with_scores(subdirs, groups, root)

heur_dist = {}
for s, idx in heur_assign.items():
    gname = groups[idx]['name'] if idx < len(groups) else "ERROR"
    if gname not in heur_dist:
        heur_dist[gname] = []
    heur_dist[gname].append(s.name)

for gname, dirs in sorted(heur_dist.items()):
    print(f"\\n{gname}: {len(dirs)} subdirs")
    for d in sorted(dirs):
        print(f"  - {d}")

print("\\n" + "-" * 80)
print("50/50 HYBRID")

hybrid_assign = {}
for subdir in subdirs:
    combined = []
    for i in range(len(groups)):
        l = llm_scores[subdir][i] if i < len(llm_scores[subdir]) else 0
        h = heur_scores[subdir][i] / 100.0 if i < len(heur_scores[subdir]) else 0
        combined.append(0.5 * l + 0.5 * h)
    hybrid_assign[subdir] = combined.index(max(combined))

hybrid_dist = {}
for s, idx in hybrid_assign.items():
    gname = groups[idx]['name'] if idx < len(groups) else "ERROR"
    if gname not in hybrid_dist:
        hybrid_dist[gname] = []
    hybrid_dist[gname].append(s.name)

for gname, dirs in sorted(hybrid_dist.items()):
    print(f"\\n{gname}: {len(dirs)} subdirs")
    for d in sorted(dirs):
        print(f"  - {d}")

# Calculate statistics
print("\\n" + "=" * 80)
print("STATISTICS")
print("=" * 80)

# Assume starbase is the main group
starbase_idx = next((i for i, g in enumerate(groups) if g['name'] == 'starbase'), -1)
if starbase_idx == -1:
    # Find the largest group
    starbase_idx = max(range(len(groups)), key=lambda i: len(groups[i]['files']))
    
main_name = groups[starbase_idx]['name']
print(f"\\nMain group: {main_name} (index {starbase_idx})")

# Stats for each approach
for name, assign in [("LLM", llm_assign), ("Heuristic", heur_assign), ("50/50 Hybrid", hybrid_assign)]:
    correct = sum(1 for idx in assign.values() if idx == starbase_idx)
    total = len(assign)
    
    print(f"\\n{name}:")
    print(f"  Correctly assigned to {main_name}: {correct}/{total} ({100*correct/total:.1f}%)")
    print(f"  Incorrectly assigned: {total-correct}/{total} ({100*(total-correct)/total:.1f}%)")
    
    if total - correct > 0:
        print("  Wrong assignments:")
        for s, idx in sorted(assign.items(), key=lambda x: x[0].name):
            if idx != starbase_idx:
                wrong = groups[idx]['name'] if idx < len(groups) else "ERROR"
                print(f"    {s.name} -> {wrong}")

# Total files
total_files = len(list(root.rglob("*.py")))
total_files = len([f for f in root.rglob("*.py") if '__pycache__' not in str(f) and '.venv' not in str(f)])
organized = sum(len(g['files']) for g in groups)
for s in subdirs:
    organized += len([f for f in s.rglob("*.py") if '__pycache__' not in str(f)])

print(f"\\nTotal Python files: {total_files}")
print(f"Files organized: {organized}")
print(f"Files left behind: {total_files - organized}")
'''

# Save and run the test
with open("run_real_test.py", "w") as f:
    f.write(test_code)

result = subprocess.run([sys.executable, "run_real_test.py"], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Clean up
Path("run_real_test.py").unlink(missing_ok=True)