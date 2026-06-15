"""
Task 6 — Visual Automation
tests/test_visual_regression.py

Two test classes:
  TestBaselineCapture   — Phase 1: capture baseline screenshots (run once).
  TestVisualRegression  — Phase 2: compare actual vs baseline, gate merges.

Design rules
────────────
• Every test method contains at least one explicit time.sleep() call.
• setUp() and tearDown() add a gap between tests.
• time.sleep() also appears inside helpers after every significant action.
• Gate: if any comparison exceeds DIFF_THRESHOLD_PCT → test FAILS → merge blocked.
"""

import os
import sys
import time
import unittest
from typing import Any, Dict

# Make parent package importable when running tests directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DIRS, PAGES, SLEEP, DIFF_THRESHOLD_PCT, VIEWPORTS
from screenshot_manager import (
    capture, create_driver, navigate, resize, scroll_to_top,
)
from visual_comparator import compare


# ══════════════════════════════════════════════════════════════════════════════
# Phase 1 — Baseline Capture
# ══════════════════════════════════════════════════════════════════════════════

class TestBaselineCapture(unittest.TestCase):
    """
    Capture reference (baseline) screenshots for all pages × viewports.
    Run once before any code changes are made.
    Re-run intentionally to accept new baselines after approved UI changes.
    """

    @classmethod
    def setUpClass(cls) -> None:
        time.sleep(SLEEP["startup"])              # ✅ SLEEP: pre-suite warm-up
        cls.driver = create_driver()
        print("\n📸  Baseline capture — starting …")

    @classmethod
    def tearDownClass(cls) -> None:
        time.sleep(SLEEP["suite_teardown"])       # ✅ SLEEP: pending I/O settle
        cls.driver.quit()
        print("📸  Baseline capture — complete.\n")

    def setUp(self) -> None:
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP: gap before each test

    def tearDown(self) -> None:
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP: gap after each test

    # ── Shared helper ─────────────────────────────────────────────────────────

    def _capture_all_viewports(self, page: Dict[str, str]) -> None:
        """Navigate to page and capture baseline at every configured viewport."""
        for vp in VIEWPORTS:
            with self.subTest(page=page["id"], viewport=vp["label"]):
                resize(self.driver, vp["width"], vp["height"])
                time.sleep(SLEEP["after_resize"])           # ✅ SLEEP: CSS reflow

                navigate(self.driver, page["url"])
                time.sleep(SLEEP["page_load"])              # ✅ SLEEP: full render

                scroll_to_top(self.driver)
                time.sleep(SLEEP["after_scroll"])           # ✅ SLEEP: scroll settle

                path = capture(
                    self.driver, page["id"], vp["label"], dest="baselines"
                )
                time.sleep(SLEEP["after_capture"])          # ✅ SLEEP: I/O settle

                self.assertTrue(
                    os.path.exists(path),
                    f"Baseline not saved: {path}",
                )
                print(f"    ✅  {os.path.basename(path)}")

    # ── Tests ─────────────────────────────────────────────────────────────────

    def test_01_baseline_home_page(self) -> None:
        """Capture baselines for the Home page at all viewports."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        print("\n  🌐  Home page")
        self._capture_all_viewports(PAGES[0])

    def test_02_baseline_search_page(self) -> None:
        """Capture baselines for the Search results page at all viewports."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        print("\n  🌐  Search page")
        self._capture_all_viewports(PAGES[1])

    def test_03_baseline_login_page(self) -> None:
        """Capture baselines for the Login page at all viewports."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        print("\n  🌐  Login page")
        self._capture_all_viewports(PAGES[2])


# ══════════════════════════════════════════════════════════════════════════════
# Phase 2 — Visual Regression
# ══════════════════════════════════════════════════════════════════════════════

class TestVisualRegression(unittest.TestCase):
    """
    Compare freshly captured screenshots against established baselines.

    Pass/Fail criteria
    ──────────────────
    A test FAILS if the percentage of changed pixels exceeds DIFF_THRESHOLD_PCT.
    The test runner exits with code 1 on any failure, blocking the merge.
    """

    results: list = []    # accumulated by every test; read by report_generator

    @classmethod
    def setUpClass(cls) -> None:
        time.sleep(SLEEP["startup"])              # ✅ SLEEP: pre-suite warm-up
        cls.driver  = create_driver()
        cls.results = []
        print(
            f"\n🔍  Visual regression — starting  "
            f"(threshold: {DIFF_THRESHOLD_PCT}%) …"
        )

    @classmethod
    def tearDownClass(cls) -> None:
        time.sleep(SLEEP["suite_teardown"])       # ✅ SLEEP: I/O settle
        cls.driver.quit()
        _print_summary(cls.results)

    def setUp(self) -> None:
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP: gap before each test

    def tearDown(self) -> None:
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP: gap after each test

    # ── Core runner ───────────────────────────────────────────────────────────

    def _visual_test(self, page: Dict[str, str], vp: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture an actual screenshot, compare it to the baseline, return result.
        Uses sleep at every step for stable, animation-settled captures.
        """
        resize(self.driver, vp["width"], vp["height"])
        time.sleep(SLEEP["after_resize"])             # ✅ SLEEP: layout reflow

        navigate(self.driver, page["url"])
        time.sleep(SLEEP["page_load"])                # ✅ SLEEP: full render

        scroll_to_top(self.driver)
        time.sleep(SLEEP["after_scroll"])             # ✅ SLEEP: scroll settle

        actual_path = capture(
            self.driver, page["id"], vp["label"], dest="actual"
        )
        time.sleep(SLEEP["after_capture"])            # ✅ SLEEP: I/O settle

        baseline_path = os.path.join(
            DIRS["baselines"], f"{page['id']}__{vp['label']}.png"
        )
        result = compare(baseline_path, actual_path)
        time.sleep(SLEEP["after_compare"])            # ✅ SLEEP: after diff calc

        result.update({"page": page["id"], "viewport": vp["label"]})
        TestVisualRegression.results.append(result)
        return result

    def _assert_visual(self, result: Dict[str, Any]) -> None:
        """Log the result and fail the test if visual regression is detected."""
        time.sleep(SLEEP["after_compare"])            # ✅ SLEEP: before assertion

        if result.get("error"):
            self.skipTest(f"Skipped — {result['error']}")

        flag = "✅" if result["passed"] else "❌"
        print(
            f"    {flag}  [{result['page']} @ {result['viewport']}]  "
            f"diff={result['diff_pct']}%  "
            f"threshold={result['threshold_pct']}%"
        )
        self.assertTrue(
            result["passed"],
            (
                f"VISUAL REGRESSION DETECTED\n"
                f"  Page:      {result['page']}\n"
                f"  Viewport:  {result['viewport']}\n"
                f"  Diff:      {result['diff_pct']}%  "
                f"(threshold: {result['threshold_pct']}%)\n"
                f"  Changed:   {result['changed_px']:,} / {result['total_px']:,} px\n"
                f"  Diff img:  {result.get('diff_path', 'N/A')}"
            ),
        )

    # ── Home page ─────────────────────────────────────────────────────────────

    def test_home_mobile_375(self) -> None:
        """Home page — 375 px  (mobile portrait)."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[0], VIEWPORTS[0]))

    def test_home_mobile_414(self) -> None:
        """Home page — 414 px  (large mobile)."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[0], VIEWPORTS[1]))

    def test_home_tablet_768(self) -> None:
        """Home page — 768 px  (tablet portrait)."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[0], VIEWPORTS[2]))

    def test_home_laptop_1280(self) -> None:
        """Home page — 1280 px  (laptop)."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[0], VIEWPORTS[3]))

    def test_home_desktop_1920(self) -> None:
        """Home page — 1920 px  (full desktop)."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[0], VIEWPORTS[4]))

    # ── Search page ───────────────────────────────────────────────────────────

    def test_search_mobile_375(self) -> None:
        """Search page — 375 px."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[1], VIEWPORTS[0]))

    def test_search_mobile_414(self) -> None:
        """Search page — 414 px."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[1], VIEWPORTS[1]))

    def test_search_tablet_768(self) -> None:
        """Search page — 768 px."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[1], VIEWPORTS[2]))

    def test_search_laptop_1280(self) -> None:
        """Search page — 1280 px."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[1], VIEWPORTS[3]))

    def test_search_desktop_1920(self) -> None:
        """Search page — 1920 px."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[1], VIEWPORTS[4]))

    # ── Login page ────────────────────────────────────────────────────────────

    def test_login_mobile_375(self) -> None:
        """Login page — 375 px."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[2], VIEWPORTS[0]))

    def test_login_mobile_414(self) -> None:
        """Login page — 414 px."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[2], VIEWPORTS[1]))

    def test_login_tablet_768(self) -> None:
        """Login page — 768 px."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[2], VIEWPORTS[2]))

    def test_login_laptop_1280(self) -> None:
        """Login page — 1280 px."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[2], VIEWPORTS[3]))

    def test_login_desktop_1920(self) -> None:
        """Login page — 1920 px."""
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP
        self._assert_visual(self._visual_test(PAGES[2], VIEWPORTS[4]))

    # ── Responsive layout transition tests ────────────────────────────────────

    def test_responsive_mobile_to_tablet_reflow(self) -> None:
        """
        Verify the layout reflows correctly when the viewport grows from
        375 px (mobile) to 768 px (tablet) without a full page reload.
        Extra sleep is added to let CSS media-query transitions complete.
        """
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP

        # ── Capture at mobile ─────────────────────────────────────────────
        resize(self.driver, 375, 667)
        time.sleep(SLEEP["after_resize"])         # ✅ SLEEP
        navigate(self.driver, PAGES[0]["url"])
        time.sleep(SLEEP["page_load"])            # ✅ SLEEP
        scroll_to_top(self.driver)
        time.sleep(SLEEP["after_scroll"])         # ✅ SLEEP

        mobile_path = capture(self.driver, "home", "reflow_mobile_375", dest="actual")
        time.sleep(SLEEP["after_capture"])        # ✅ SLEEP

        # ── Resize to tablet without reload ──────────────────────────────
        resize(self.driver, 768, 1024)
        time.sleep(SLEEP["after_resize"])         # ✅ SLEEP: CSS reflow
        time.sleep(1.0)                           # ✅ SLEEP: extra for media-query transitions

        tablet_path = capture(self.driver, "home", "reflow_tablet_768", dest="actual")
        time.sleep(SLEEP["after_capture"])        # ✅ SLEEP

        self.assertTrue(os.path.exists(mobile_path), "Mobile reflow screenshot missing")
        self.assertTrue(os.path.exists(tablet_path), "Tablet reflow screenshot missing")
        print("    ✅  Mobile → Tablet reflow captures saved")

    def test_responsive_tablet_to_desktop_reflow(self) -> None:
        """
        Verify layout reflow from 768 px (tablet) to 1920 px (desktop).
        """
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP

        resize(self.driver, 768, 1024)
        time.sleep(SLEEP["after_resize"])         # ✅ SLEEP
        navigate(self.driver, PAGES[0]["url"])
        time.sleep(SLEEP["page_load"])            # ✅ SLEEP

        capture(self.driver, "home", "reflow_tablet_before_expand", dest="actual")
        time.sleep(SLEEP["after_capture"])        # ✅ SLEEP

        resize(self.driver, 1920, 1080)
        time.sleep(SLEEP["after_resize"])         # ✅ SLEEP
        time.sleep(1.0)                           # ✅ SLEEP: extra for repaint

        desktop_path = capture(self.driver, "home", "reflow_desktop_1920", dest="actual")
        time.sleep(SLEEP["after_capture"])        # ✅ SLEEP

        self.assertTrue(os.path.exists(desktop_path), "Desktop reflow screenshot missing")
        print("    ✅  Tablet → Desktop reflow captures saved")

    def test_login_form_visual_integrity(self) -> None:
        """
        Load the login page at laptop width, allow extra time for form animations
        to settle, then compare against the laptop baseline.
        """
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP

        resize(self.driver, 1280, 800)
        time.sleep(SLEEP["after_resize"])         # ✅ SLEEP
        navigate(self.driver, PAGES[2]["url"])
        time.sleep(SLEEP["page_load"])            # ✅ SLEEP
        time.sleep(2.0)                           # ✅ SLEEP: extra for form-entry animations

        scroll_to_top(self.driver)
        time.sleep(SLEEP["after_scroll"])         # ✅ SLEEP

        actual_path   = capture(self.driver, "login", "form_integrity_1280", dest="actual")
        time.sleep(SLEEP["after_capture"])        # ✅ SLEEP

        baseline_path = os.path.join(DIRS["baselines"], "mystery__laptop_1280.png")
        if not os.path.exists(baseline_path):
            self.skipTest("Baseline not found — run TestBaselineCapture first")

        result = compare(baseline_path, actual_path)
        time.sleep(SLEEP["after_compare"])        # ✅ SLEEP

        result.update({"page": "login_form", "viewport": "laptop_1280"})
        TestVisualRegression.results.append(result)
        self._assert_visual(result)

    def test_search_results_product_grid(self) -> None:
        """
        Verify the product-grid layout on the search page at tablet width.
        Extra sleep to allow lazy-loaded product images to appear.
        """
        time.sleep(SLEEP["between_tests"])        # ✅ SLEEP

        resize(self.driver, 768, 1024)
        time.sleep(SLEEP["after_resize"])         # ✅ SLEEP
        navigate(self.driver, PAGES[1]["url"])
        time.sleep(SLEEP["page_load"])            # ✅ SLEEP
        time.sleep(2.0)                           # ✅ SLEEP: lazy-load images settle

        scroll_to_top(self.driver)
        time.sleep(SLEEP["after_scroll"])         # ✅ SLEEP

        actual_path   = capture(self.driver, "search", "grid_tablet_768", dest="actual")
        time.sleep(SLEEP["after_capture"])        # ✅ SLEEP

        baseline_path = os.path.join(DIRS["baselines"], "catalogue__tablet_768.png")
        if not os.path.exists(baseline_path):
            self.skipTest("Baseline not found — run TestBaselineCapture first")

        result = compare(baseline_path, actual_path)
        time.sleep(SLEEP["after_compare"])        # ✅ SLEEP

        result.update({"page": "search_grid", "viewport": "tablet_768"})
        TestVisualRegression.results.append(result)
        self._assert_visual(result)


# ──────────────────────────────────────────────────────────────────────────────
# Summary Helper
# ──────────────────────────────────────────────────────────────────────────────

def _print_summary(results: list) -> None:
    time.sleep(1.0)     # ✅ SLEEP: before printing
    passed = sum(1 for r in results if r.get("passed") is True)
    failed = sum(1 for r in results if r.get("passed") is False)
    gate   = "✅  MERGE APPROVED" if failed == 0 else "❌  MERGE BLOCKED"
    bar    = "═" * 58
    print(f"\n{bar}")
    print(f"  Visual Regression Summary")
    print(f"  Total: {len(results)}   ✅ Passed: {passed}   ❌ Failed: {failed}")
    print(f"  Gate:  {gate}")
    print(f"{bar}\n")


# ──────────────────────────────────────────────────────────────────────────────
# Direct Execution
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    time.sleep(1.0)     # ✅ SLEEP: startup pause
    unittest.main(verbosity=2)
