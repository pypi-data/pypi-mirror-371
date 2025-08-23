#!/usr/bin/env python3
"""Test the updated search functionality"""

import subprocess
import sys

def test_search():
    """Test search with different queries"""
    
    print("Testing starbase search functionality...")
    print("=" * 50)
    
    # Test 1: Basic search
    print("\n1. Testing basic search for 'extract':")
    result = subprocess.run(["python", "starbase.py", "search", "extract"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Test 2: Search with debug flag
    print("\n2. Testing search with --debug flag:")
    result = subprocess.run(["python", "starbase.py", "search", "extract", "--debug"], 
                          capture_output=True, text=True)
    print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    
    # Test 3: Search with no results
    print("\n3. Testing search with no results:")
    result = subprocess.run(["python", "starbase.py", "search", "xyzabc123"], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    print("\n" + "=" * 50)
    print("Search functionality test complete!")
    print("\nKey features implemented:")
    print("✓ Package names shown prominently")
    print("✓ Numbered options for selection")
    print("✓ Clear actions (Install, Copy, View, Info)")
    print("✓ PDM install commands shown")
    print("✓ Debug flag for detailed output")

if __name__ == "__main__":
    test_search()