"""
Run this from inside task6_visual_automation folder.
Removes maximize_window() and set_window_position() that conflict with undetected_chromedriver.
"""

with open("screenshot_manager.py", "r") as f:
    lines = f.readlines()

lines_to_remove = [
    "    driver.maximize_window()\n",
    "    driver.set_window_position(0, 0)\n",
]

new_lines = [line for line in lines if line not in lines_to_remove]

with open("screenshot_manager.py", "w") as f:
    f.writelines(new_lines)

removed = len(lines) - len(new_lines)
print(f"Removed {removed} line(s) — screenshot_manager.py patched successfully.")
