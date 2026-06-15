#!/usr/bin/env python3
"""
Task 6 — Visual Automation  |  run_tests.py
============================================
Entry point for the visual regression test suite.

Usage
─────
  python run_tests.py                        # baseline → regression → report
  python run_tests.py --mode baseline        # capture baselines only
  python run_tests.py --mode regression      # regression checks only
  python run_tests.py --mode both --no-report

Exit codes
──────────
  0  — all tests passed  →  merge may proceed
  1  — one or more tests failed  →  merge is BLOCKED
"""

import argparse
import os
import sys
import time
import unittest

# ── Ensure project root is on sys.path ────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from config import SLEEP


# ──────────────────────────────────────────────────────────────────────────────
# Suite Builder
# ──────────────────────────────────────────────────────────────────────────────

def build_suite(mode: str):
    """Load the appropriate test classes and return (suite, regression_cls)."""
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "tests"))
    from test_visual_regression import TestBaselineCapture, TestVisualRegression

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    if mode in ("baseline", "both"):
        suite.addTests(loader.loadTestsFromTestCase(TestBaselineCapture))
        time.sleep(SLEEP["between_tests"])    # ✅ SLEEP: between suite additions

    if mode in ("regression", "both"):
        suite.addTests(loader.loadTestsFromTestCase(TestVisualRegression))
        time.sleep(SLEEP["between_tests"])    # ✅ SLEEP

    regression_cls = TestVisualRegression if mode in ("regression", "both") else None
    return suite, regression_cls


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    time.sleep(SLEEP["startup"])              # ✅ SLEEP: startup warm-up

    parser = argparse.ArgumentParser(
        description="Task 6 — Visual Automation Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python run_tests.py                      # full run + report\n"
            "  python run_tests.py --mode baseline      # baselines only\n"
            "  python run_tests.py --mode regression    # regression only\n"
        ),
    )
    parser.add_argument(
        "--mode",
        choices=["baseline", "regression", "both"],
        default="both",
        help="Run mode  (default: both)",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip HTML report generation",
    )
    args = parser.parse_args()

    # ── Banner ────────────────────────────────────────────────────────────────
    print(f"\n{'═' * 60}")
    print("  Task 6 — Visual Automation")
    print(f"  Mode   : {args.mode}")
    print(f"  Report : {'disabled' if args.no_report else 'enabled'}")
    print(f"{'═' * 60}\n")

    # ── Build & run ───────────────────────────────────────────────────────────
    suite, regression_cls = build_suite(args.mode)

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)

    time.sleep(SLEEP["between_tests"])        # ✅ SLEEP: before running
    result = runner.run(suite)
    time.sleep(SLEEP["suite_teardown"])       # ✅ SLEEP: after running

    # ── Report ────────────────────────────────────────────────────────────────
    if (
        not args.no_report
        and regression_cls is not None
        and hasattr(regression_cls, "results")
        and regression_cls.results
    ):
        from report_generator import generate_report
        generate_report(regression_cls.results)

    # ── Gate ──────────────────────────────────────────────────────────────────
    time.sleep(SLEEP["between_tests"])        # ✅ SLEEP: before exit
    gate = "✅  MERGE APPROVED" if result.wasSuccessful() else "❌  MERGE BLOCKED"
    print(f"\n  Gate: {gate}\n")
    sys.exit(0 if result.wasSuccessful() else 1)


# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    time.sleep(1.0)     # ✅ SLEEP: initial startup pause
    main()
