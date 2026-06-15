"""
Run this from inside task6_visual_automation folder.
Fixes the resize function to handle undetected_chromedriver's maximized state.
"""

with open("screenshot_manager.py", "r") as f:
    content = f.read()

old = '''def resize(driver: webdriver.Remote, width: int, height: int) -> None:
    """Resize the browser window and wait for CSS layout reflow."""
    driver.set_window_size(width, height)
    time.sleep(SLEEP["after_resize"])     # ✅ SLEEP: layout / CSS reflow'''

new = '''def resize(driver: webdriver.Remote, width: int, height: int) -> None:
    """Resize the browser window and wait for CSS layout reflow."""
    try:
        # Restore from maximized state first (required for undetected_chromedriver)
        driver.set_window_rect(0, 0, width, height)
    except Exception:
        try:
            driver.execute_script(
                f"window.moveTo(0,0); window.resizeTo({width},{height});"
            )
        except Exception:
            pass
    time.sleep(SLEEP["after_resize"])     # ✅ SLEEP: layout / CSS reflow'''

if old in content:
    content = content.replace(old, new)
    with open("screenshot_manager.py", "w") as f:
        f.write(content)
    print("Done — resize function patched successfully.")
else:
    print("ERROR: Could not find resize function. May already be patched.")
    print("Open screenshot_manager.py and manually replace the resize() function.")
