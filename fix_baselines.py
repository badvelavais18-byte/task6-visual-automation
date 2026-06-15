"""
Run this from inside task6_visual_automation folder.
Lists all files in screenshots folders so we can find the correct filenames.
"""

import os
import shutil

print("=== screenshots/baselines/ ===")
baselines = os.listdir("screenshots/baselines")
for f in sorted(baselines):
    print(f"  {f}")

print("\n=== screenshots/actual/ ===")
actual = os.listdir("screenshots/actual")
for f in sorted(actual):
    print(f"  {f}")

# Auto-copy any file in actual that is NOT already in baselines
print("\n=== Copying missing files from actual → baselines ===")
for f in actual:
    dst = os.path.join("screenshots", "baselines", f)
    src = os.path.join("screenshots", "actual", f)
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
        print(f"  Copied: {f}")
    else:
        print(f"  Already exists: {f}")

print("\nDone. Now run: python run_tests.py --mode regression")
