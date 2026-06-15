"""
Run this from inside task6_visual_automation folder.
Fixes hardcoded baseline paths in the two special tests.
"""

with open("tests/test_visual_regression.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: login_form test — was comparing against login__laptop_1280.png (OpenCart)
old1 = 'baseline_path = os.path.join(DIRS["baselines"], "login__laptop_1280.png")'
new1 = 'baseline_path = os.path.join(DIRS["baselines"], "mystery__laptop_1280.png")'

# Fix 2: search_grid test — was comparing against search__tablet_768.png (OpenCart)
old2 = 'baseline_path = os.path.join(DIRS["baselines"], "search__tablet_768.png")'
new2 = 'baseline_path = os.path.join(DIRS["baselines"], "catalogue__tablet_768.png")'

if old1 in content:
    content = content.replace(old1, new1)
    print("Fixed: login_form baseline → mystery__laptop_1280.png")
else:
    print("ERROR: Could not find login_form baseline path")

if old2 in content:
    content = content.replace(old2, new2)
    print("Fixed: search_grid baseline → catalogue__tablet_768.png")
else:
    print("ERROR: Could not find search_grid baseline path")

with open("tests/test_visual_regression.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\nDone — run: python run_tests.py --mode regression")
