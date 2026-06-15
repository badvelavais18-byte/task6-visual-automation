"""
Run this from inside task6_visual_automation folder.
Removes experimental options that are incompatible with undetected_chromedriver.
"""

with open("screenshot_manager.py", "r") as f:
    content = f.read()

# Remove the two lines that uc.Chrome rejects
lines_to_remove = [
    '        opts.add_experimental_option("excludeSwitches", ["enable-automation"])\n',
    '        opts.add_experimental_option("useAutomationExtension", False)\n',
]

for line in lines_to_remove:
    if line in content:
        content = content.replace(line, "")
        print(f"Removed: {line.strip()}")
    else:
        print(f"Not found (already removed?): {line.strip()}")

with open("screenshot_manager.py", "w") as f:
    f.write(content)

print("\nDone — screenshot_manager.py patched successfully.")
