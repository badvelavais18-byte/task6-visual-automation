"""
Run this from inside task6_visual_automation folder.
Shows the two failing test methods so we can see what URLs they use.
"""

with open("tests/test_visual_regression.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find and print test_login_form_visual_integrity
print("=== test_login_form_visual_integrity ===")
in_test = False
for i, line in enumerate(lines):
    if "def test_login_form_visual_integrity" in line:
        in_test = True
    if in_test:
        print(f"{i+1}: {line}", end="")
        if in_test and i > 0 and line.strip().startswith("def ") and "test_login_form" not in line:
            break

print("\n=== test_search_results_product_grid ===")
in_test = False
for i, line in enumerate(lines):
    if "def test_search_results_product_grid" in line:
        in_test = True
    if in_test:
        print(f"{i+1}: {line}", end="")
        if in_test and i > 0 and line.strip().startswith("def ") and "test_search_results" not in line:
            break
