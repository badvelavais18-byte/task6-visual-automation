"""
Task 6 — Visual Automation
Configuration: viewports, target pages, sleep durations, diff thresholds.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Output Directories ───────────────────────────────────────────────────────
DIRS = {
    "baselines": os.path.join(BASE_DIR, "screenshots", "baselines"),
    "actual":    os.path.join(BASE_DIR, "screenshots", "actual"),
    "diffs":     os.path.join(BASE_DIR, "screenshots", "diffs"),
    "reports":   os.path.join(BASE_DIR, "reports"),
}
for _path in DIRS.values():
    os.makedirs(_path, exist_ok=True)

# ─── Viewport / Device Breakpoints ────────────────────────────────────────────
VIEWPORTS = [
    {"label": "mobile_375",   "width": 375,  "height": 667},
    {"label": "mobile_414",   "width": 414,  "height": 896},
    {"label": "tablet_768",   "width": 768,  "height": 1024},
    {"label": "laptop_1280",  "width": 1280, "height": 800},
    {"label": "desktop_1920", "width": 1920, "height": 1080},
]

# ─── Target Pages ─────────────────────────────────────────────────────────────
PAGES = [
    {"id": "home",   "url": "https://demo.opencart.com/"},
    {"id": "search", "url": "https://demo.opencart.com/index.php?route=product/search&search=camera"},
    {"id": "login",  "url": "https://demo.opencart.com/index.php?route=account/login"},
]

# ─── Visual Diff Settings ─────────────────────────────────────────────────────
PIXEL_DIFF_SENSITIVITY = 10    # per-channel tolerance  (0–255)
DIFF_THRESHOLD_PCT     = 5.0   # max % of pixels that may differ before FAIL

# ─── Sleep Durations (seconds) ────────────────────────────────────────────────
SLEEP = {
    "startup":        2.0,   # pre-suite warm-up
    "page_load":      7.0,   # after driver.get()
    "after_resize":   1.0,   # after set_window_size()
    "after_scroll":   0.5,   # after window.scrollTo()
    "after_capture":  1.0,   # after save_screenshot()
    "after_compare":  0.5,   # after pixel comparison
    "between_tests":  2.0,   # setUp / tearDown gap
    "suite_teardown": 2.0,   # after tearDownClass
}

# ─── WebDriver ────────────────────────────────────────────────────────────────
BROWSER       = "chrome"   # chrome | firefox
HEADLESS = False
IMPLICIT_WAIT = 10
PAGE_LOAD_TMO = 60
