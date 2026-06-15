"""
Run this from inside task6_visual_automation folder.
Views current resize function then fixes it.
"""

with open("screenshot_manager.py", "r") as f:
    lines = f.readlines()

# Find and print the resize function
print("=== Current resize function ===")
in_resize = False
for i, line in enumerate(lines):
    if "def resize(" in line:
        in_resize = True
    if in_resize:
        print(f"{i+1}: {line}", end="")
        if in_resize and i > 0 and line.strip() == "" and "def resize" not in line:
            break
        if in_resize and "def " in line and "def resize" not in line:
            break

print("\n=== Applying fix ===")

# Replace the entire resize function with a robust version
new_resize = '''def resize(driver: webdriver.Remote, width: int, height: int) -> None:
    """Resize the browser window and wait for CSS layout reflow."""
    try:
        driver.set_window_rect(0, 0, width, height)
    except Exception:
        try:
            driver.execute_script(
                f"window.moveTo(0,0); window.resizeTo({width},{height});"
            )
        except Exception:
            pass
    time.sleep(SLEEP["after_resize"])     # ✅ SLEEP: layout / CSS reflow

'''

# Build new file replacing the resize function
new_lines = []
in_resize = False
skip_until_next_def = False

for i, line in enumerate(lines):
    if "def resize(" in line:
        in_resize = True
        new_lines.append(new_resize)
        continue
    if in_resize:
        # Skip lines until we hit the next function or end of file
        if line.strip().startswith("def ") or line.strip().startswith("# ──"):
            in_resize = False
            new_lines.append(line)
        continue
    new_lines.append(line)

with open("screenshot_manager.py", "w") as f:
    f.writelines(new_lines)

print("Done — resize function replaced successfully.")
