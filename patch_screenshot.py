"""Run this script from inside task6_visual_automation folder to patch screenshot_manager.py"""

with open("screenshot_manager.py", "r") as f:
    content = f.read()

old = '    time.sleep(0.5)'
new = '''    time.sleep(0.5)
    driver.execute_script("window.scrollTo(0, 600);")
    time.sleep(SLEEP["after_scroll"])'''

if old not in content:
    print("ERROR: Could not find the target line. Already patched?")
else:
    content = content.replace(old, new, 1)
    with open("screenshot_manager.py", "w") as f:
        f.write(content)
    print("Done — screenshot_manager.py patched successfully.")
