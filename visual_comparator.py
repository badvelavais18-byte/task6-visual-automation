"""
Task 6 — Visual Automation
visual_comparator.py  ·  Pixel-level screenshot comparison with diff overlay.

Algorithm
─────────
1. Load baseline + actual as RGB arrays (NumPy).
2. Compute absolute per-channel delta; flag pixels where delta > sensitivity.
3. Calculate changed-pixel percentage.
4. Generate a diff overlay image (red = changed pixel).
5. Pass/Fail against DIFF_THRESHOLD_PCT.
"""

import os
import time

import numpy as np
from PIL import Image

from config import DIRS, SLEEP, PIXEL_DIFF_SENSITIVITY, DIFF_THRESHOLD_PCT


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def compare(baseline_path: str, actual_path: str) -> dict:
    """
    Compare a baseline screenshot against a newly captured actual screenshot.

    Returns:
        {
            "passed":         bool,
            "diff_pct":       float,    # % of changed pixels
            "threshold_pct":  float,
            "changed_px":     int,
            "total_px":       int,
            "diff_path":      str,      # path to red-overlay diff image
            "baseline_path":  str,
            "actual_path":    str,
            "error":          str | None,
        }
    """
    time.sleep(SLEEP["after_compare"])    # ✅ SLEEP: before loading images

    # ── Guard: baseline must exist ──────────────────────────────────────────
    if not os.path.exists(baseline_path):
        return {
            "passed":        None,
            "error":         f"Baseline not found: {baseline_path}",
            "baseline_path": baseline_path,
            "actual_path":   actual_path,
        }

    # ── Load images as RGB ──────────────────────────────────────────────────
    baseline_img = Image.open(baseline_path).convert("RGB")
    actual_img   = Image.open(actual_path).convert("RGB")

    # ── Normalise dimensions (resize actual if mismatch) ────────────────────
    if baseline_img.size != actual_img.size:
        actual_img = actual_img.resize(baseline_img.size, Image.LANCZOS)

    b_arr = np.asarray(baseline_img, dtype=np.int16)   # shape (H, W, 3)
    a_arr = np.asarray(actual_img,   dtype=np.int16)

    # ── Pixel-level diff (vectorised) ───────────────────────────────────────
    delta        = np.abs(b_arr - a_arr)                          # (H, W, 3)
    changed_mask = np.any(delta > PIXEL_DIFF_SENSITIVITY, axis=2) # (H, W) bool

    total_px   = changed_mask.size
    changed_px = int(changed_mask.sum())
    diff_pct   = round(changed_px / total_px * 100, 2)
    passed     = diff_pct <= DIFF_THRESHOLD_PCT

    time.sleep(SLEEP["after_compare"])    # ✅ SLEEP: after computation

    # ── Diff overlay image ──────────────────────────────────────────────────
    diff_path = _save_diff_overlay(a_arr, changed_mask, actual_path)

    return {
        "passed":        passed,
        "diff_pct":      diff_pct,
        "threshold_pct": DIFF_THRESHOLD_PCT,
        "changed_px":    changed_px,
        "total_px":      total_px,
        "diff_path":     diff_path,
        "baseline_path": baseline_path,
        "actual_path":   actual_path,
        "error":         None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Internal Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _save_diff_overlay(
    actual_arr: np.ndarray,
    changed_mask: np.ndarray,
    actual_path: str,
) -> str:
    """
    Paint changed pixels red on a copy of the actual screenshot and save.

    Returns:
        Absolute path to the saved diff PNG.
    """
    diff_arr = actual_arr.copy().astype(np.uint8)
    diff_arr[changed_mask] = [255, 0, 0]          # bright red = regression pixel

    diff_img  = Image.fromarray(diff_arr)
    diff_name = os.path.basename(actual_path).replace(".png", "_diff.png")
    diff_path = os.path.join(DIRS["diffs"], diff_name)
    diff_img.save(diff_path)

    return diff_path
