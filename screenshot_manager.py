"""
Task 6 — Visual Automation
screenshot_manager.py  ·  WebDriver factory + screenshot capture helpers.
Every public function uses time.sleep() to ensure stable renders.
"""

import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from config import DIRS, SLEEP, BROWSER, HEADLESS, IMPLICIT_WAIT, PAGE_LOAD_TMO


# ──────────────────────────────────────────────────────────────────────────────
# Driver Factory
# ──────────────────────────────────────────────────────────────────────────────

def create_driver(browser: str = BROWSER, headless: bool = HEADLESS) -> webdriver.Remote:
    """
    Create and return a configured WebDriver instance.

    Supports Chrome and Firefox; Selenium 4.6+ handles driver binary discovery
    automatically via Selenium Manager — no manual chromedriver install needed.
    """
    time.sleep(SLEEP["startup"])          # ✅ SLEEP: wait before browser launch

    if browser == "chrome":
        opts = ChromeOptions()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=opts)

    elif browser == "firefox":
        opts = FirefoxOptions()
        if headless:
            opts.add_argument("--headless")
        driver = webdriver.Firefox(options=opts)

    else:
        raise ValueError(f"Unsupported browser: {browser!r}.  Use 'chrome' or 'firefox'.")

    driver.implicitly_wait(IMPLICIT_WAIT)
    driver.set_page_load_timeout(PAGE_LOAD_TMO)
    return driver


# ──────────────────────────────────────────────────────────────────────────────
# Navigation & Viewport
# ──────────────────────────────────────────────────────────────────────────────

def navigate(driver: webdriver.Remote, url: str) -> None:
    """Navigate to a URL and wait for the page to fully render."""
    driver.get(url)
    time.sleep(SLEEP["page_load"])        # ✅ SLEEP: full page render


def resize(driver: webdriver.Remote, width: int, height: int) -> None:
    """Resize the browser window and wait for CSS layout reflow."""
    driver.set_window_size(width, height)
    time.sleep(SLEEP["after_resize"])     # ✅ SLEEP: layout / CSS reflow


def scroll_to_top(driver: webdriver.Remote) -> None:
    """Scroll the viewport to the page top and wait for animation."""
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(SLEEP["after_scroll"])     # ✅ SLEEP: scroll animation settle


# ──────────────────────────────────────────────────────────────────────────────
# Screenshot Capture
# ──────────────────────────────────────────────────────────────────────────────

def capture(
    driver: webdriver.Remote,
    page_id: str,
    viewport_label: str,
    dest: str = "actual",
) -> str:
    """
    Capture a screenshot and save it to the appropriate folder.

    Args:
        driver:         Active WebDriver session.
        page_id:        Short page identifier, e.g. "home", "login".
        viewport_label: Viewport key, e.g. "mobile_375", "desktop_1920".
        dest:           Destination key — "baselines" or "actual".

    Returns:
        Absolute path to the saved PNG file.
    """
    if dest not in DIRS:
        raise ValueError(
            f"Unknown dest {dest!r}. Valid options: {list(DIRS.keys())}"
        )

    filename = f"{page_id}__{viewport_label}.png"
    filepath = os.path.join(DIRS[dest], filename)

    driver.save_screenshot(filepath)
    time.sleep(SLEEP["after_capture"])    # ✅ SLEEP: I/O and post-capture settle

    return filepath
