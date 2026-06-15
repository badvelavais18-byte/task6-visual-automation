"""
Run this from inside task6_visual_automation folder.
Fixes resize function with proper UTF-8 encoding.
"""

with open("screenshot_manager.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

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
    time.sleep(SLEEP["after_resize"])     # SLEEP: layout / CSS reflow

'''

new_lines = []
in_resize = False

for line in lines:
    if "def resize(" in line:
        in_resize = True
        new_lines.append(new_resize)
        continue
    if in_resize:
        if line.strip().startswith("def ") or line.strip().startswith("# \u2500"):
            in_resize = False
            new_lines.append(line)
        continue
    new_lines.append(line)

with open("screenshot_manager.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Done — resize function replaced successfully.")
