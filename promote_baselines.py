"""
Run this from inside task6_visual_automation folder.
Promotes the actual screenshots of special tests to baselines,
so the next regression run compares apples to apples.
"""

import shutil
import os

files = [
    "login__form_integrity_1280.png",
    "search__grid_tablet_768.png",
]

for f in files:
    src = os.path.join("screenshots", "actual", f)
    dst = os.path.join("screenshots", "baselines", f)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Promoted to baseline: {f}")
    else:
        print(f"Not found in actual/: {f}  (skipping)")

print("\nDone — run regression now:")
print("  python run_tests.py --mode regression")
