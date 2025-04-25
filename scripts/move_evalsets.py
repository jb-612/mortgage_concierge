#!/usr/bin/env python
"""
Script to move evalset JSON files from the project root to the tests/eval/data/recorded-sessions directory.
Run this periodically to keep evaluation datasets organized.

Usage:
    python scripts/move_evalsets.py
"""

import os
import shutil
import glob
import pathlib
import re
import sys

# Determine project root directory
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
TARGET_DIR = PROJECT_ROOT / "tests" / "eval" / "data" / "recorded-sessions"

def setup():
    """Ensure target directory exists."""
    if not TARGET_DIR.exists():
        print(f"Creating directory: {TARGET_DIR}")
        TARGET_DIR.mkdir(parents=True, exist_ok=True)

def move_evalset_files():
    """Find and move evalset files from project root to target directory."""
    # Find all evalset files in project root and subdirectories (excluding the target directory)
    pattern = re.compile(r"evalset.*\.evalset\.json$")
    moved_count = 0
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip the target directory itself and any git directories
        if TARGET_DIR.name in root or ".git" in root:
            continue
            
        for file in files:
            if pattern.match(file):
                source_path = os.path.join(root, file)
                relative_path = os.path.relpath(source_path, PROJECT_ROOT)
                
                # Skip files already in the recorded-sessions directory
                if "tests/eval/data/recorded-sessions" in relative_path:
                    continue
                    
                target_path = TARGET_DIR / file
                
                print(f"Moving: {relative_path} -> tests/eval/data/recorded-sessions/{file}")
                shutil.copy2(source_path, target_path)
                os.remove(source_path)
                moved_count += 1
                
    return moved_count

if __name__ == "__main__":
    setup()
    moved_count = move_evalset_files()
    
    if moved_count > 0:
        print(f"\nSuccessfully moved {moved_count} evalset file(s) to {TARGET_DIR}")
        print("\nTo run evaluation tests on these files:")
        print(f"  python -m pytest tests/eval/test_eval.py::test_recorded_sessions -v")
    else:
        print("No evalset files found to move.")
    
    sys.exit(0)